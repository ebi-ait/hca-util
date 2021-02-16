import os
from tqdm import tqdm
from multiprocessing import cpu_count
from multiprocessing.pool import ThreadPool

from botocore.exceptions import ClientError
from boto3.s3.transfer import TransferConfig
from botocore.config import Config

from ait.commons.util.aws_client import Aws
from ait.commons.util.common import gen_uuid, format_err, INGEST_UPLOAD_AREA_PREFIX
from ait.commons.util.local_state import get_selected_area
from ait.commons.util.upload_service import notify_upload


class CmdSync:

    def __init__(self, aws: Aws, args):
        self.aws = aws
        self.args = args

    def run(self):
        if not self.aws:
            return False, 'You need configure your profile first'

        if self.aws.is_user:
            return False, 'You don\'t have permission to use this command'

        selected_area = get_selected_area()

        if not selected_area:
            return False, 'No area selected'
        
        dest_bucket, dest_env, dest_upload_area_uuid = self.args.INGEST_UPLOAD_AREA

        try:
            # Resources are not thread safe.
            # Low-level clients are thread safe. When using a low-level client, it is recommended to instantiate 
            # your client then pass that client object to each of your threads.

            s3_res = self.aws.common_session.resource('s3', config=Config(s3={'use_accelerate_endpoint': True}))
            s3_cli = s3_res.meta.client
            
            bucket = s3_res.Bucket(self.aws.bucket_name)

            fs = []
            total_size = 0

            # get all files from selected area
            for obj in bucket.objects.filter(Prefix=selected_area):
                # skip the top-level directory
                if obj.key == selected_area:
                    continue
                total_size += obj.size
                fs.append(obj)

            failed_fs = []
            
            def transfer(f):
                try:
                    
                    fname = f.key[37:]
                    content_type = ''
                    obj_ = s3_cli.head_object(Bucket=self.aws.bucket_name, Key=f.key)
                    if obj_ and obj_['ContentType']:
                        content_type = obj_['ContentType']
                        if "dcp-type=data" not in content_type:
                            content_type += '; dcp-type=data'

                    copy_source = {
                        'Bucket': self.aws.bucket_name,
                        'Key': f.key
                    }
                    dest_key = dest_upload_area_uuid + '/' + fname

                    s3_cli.copy(copy_source, dest_bucket, dest_key,
                                    Callback=pbar.update, 
                                    ExtraArgs={
                                        'ContentType': content_type,
                                        'MetadataDirective': 'REPLACE',
                                        },
                                    Config=get_transfer_config(f.size))

                    if not notify_upload(dest_env, dest_upload_area_uuid, fname):
                        failed_fs.append((f, 'Transferred. Notify failed.'))

                except ClientError as ex:
                    if ex.response['Error']['Code'] == 'NoSuchKey':
                        failed_fs.append((f, 'NoSuchKey'))
                    else:
                        failed_fs.append((f, str(thread_ex)))
                    pass

                except Exception as thread_ex:
                    failed_fs.append((f, str(thread_ex)))
                    pass

            print('Transferring...')
            pbar = tqdm(total=total_size, unit='B', unit_scale=True, desc=num_files(fs))
            pool = ThreadPool() # cpu_count() DEFAULT_THREAD_COUNT=25
            pool.map_async(transfer, fs)
            pool.close()
            pool.join()
            pbar.close()

            if failed_fs:
                print(f'{num_files(failed_fs)} failed to transfer: ')
                for f,err in failed_fs:
                    print(f'{f.key} {err}')
                return False, 'Transfer complete with error.'
            else:
                return True, 'Transfer complete.'
            
        except Exception as e:
            return False, format_err(e, 'sync')


def num_files(ls):
    l = len(ls)
    return f'{l} file{"s" if l > 1 else ""}'


# this is based on the dcplib s3_multipart module
KB = 1024
MB = KB * KB
MIN_CHUNK_SIZE = 64 * MB
MULTIPART_THRESHOLD = MIN_CHUNK_SIZE + 1
MAX_MULTIPART_COUNT = 10000 # s3 imposed


def get_transfer_config(filesize):
    return TransferConfig(multipart_threshold=MULTIPART_THRESHOLD, 
                          multipart_chunksize=get_chunk_size(filesize))


def get_chunk_size(filesize):
    if filesize <= MAX_MULTIPART_COUNT * MIN_CHUNK_SIZE:
        return MIN_CHUNK_SIZE
    else:
        div = filesize // MAX_MULTIPART_COUNT
        if div * MAX_MULTIPART_COUNT < filesize:
            div += 1
        return ((div + MB - 1) // MB) * MB

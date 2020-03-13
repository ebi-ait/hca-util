import os
import botocore
from hca_util.file_transfer import FileTransfer, TransferProgress, transfer
from hca_util.settings import DEBUG_MODE
from hca_util.local_state import get_selected_dir
from hca_util.common import print_err


class CmdDownload:
    """
    user: both wrangler and contributor
    aws resource or client used in command - s3 resource (Bucket().upload_file), s3 client list_objects_v2
    """

    def __init__(self, aws, args):
        self.aws = aws
        self.args = args

    def run(self):

        selected_dir = get_selected_dir()

        if not selected_dir:
            print('No directory selected')
            return

        try:
            s3_resource = self.aws.common_session.resource('s3')
            bucket = s3_resource.Bucket(self.aws.bucket_name)

            # choice 1
            all_files = self.args.a  # optional bool

            fs = []
            if all_files:
                # download all files from selected directory
                for obj in bucket.objects.filter(Prefix=selected_dir):
                    # skip the top-level directory
                    if obj.key == selected_dir:
                        continue
                    fs.append(FileTransfer(key=obj.key, size=obj.size))
            else:
                # choice 2
                # download specified file(s) only

                for f in self.args.f:
                    # check if f exists
                    key = f'{selected_dir}{f}'
                    try:
                        obj_summary = s3_resource.ObjectSummary(self.aws.bucket_name, key)
                        obj_size = obj_summary.size
                    except botocore.exceptions.ClientError as e:
                        if e.response['Error']['Code'] == "404":
                            fs.append(FileTransfer(key=key, status='File not found.', complete=True))
                        else:
                            # Something else has gone wrong.
                            fs.append(FileTransfer(key=key, status='Download error.', complete=True))
                    else:
                        fs.append(FileTransfer(key=key, size=obj_size))

            def download(idx):
                try:
                    file = fs[idx].key
                    if not os.path.exists(os.path.dirname(file)):
                        os.makedirs(os.path.dirname(file))

                    s3 = self.aws.new_session().resource('s3')
                    s3.Bucket(self.aws.bucket_name).download_file(file, file, Callback=TransferProgress(fs[idx]))

                except Exception as thread_ex:
                    fs[idx].status = 'Download failed.'
                    fs[idx].complete = True
                    if DEBUG_MODE:
                        print_err(thread_ex, 'download')

            print('Downloading...')

            transfer(download, fs)

        except Exception as e:
            print_err(e, 'download')

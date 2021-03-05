import os
import filetype

from ait.commons.util.settings import DIR_SUPPORT, MAX_DIR_DEPTH
from ait.commons.util.common import format_err
from ait.commons.util.file_transfer import FileTransfer, TransferProgress
from ait.commons.util.local_state import get_selected_area
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor

class CmdUpload:
    """
    admin and user
    aws resource or client used in command - s3 resource (Bucket().upload_file)
    """

    def __init__(self, aws, args):
        self.aws = aws
        self.args = args
        self.files = []

    def run(self):

        selected_area = get_selected_area()

        if not selected_area:
            return False, 'No area selected'

        try:

            # filter out any duplicate path after expansion
            # . -> curent drectory
            # ~ -> user home directory

            ps = []
            for p in self.args.PATH:
                p = os.path.abspath(p)  # Normalize a pathname by collapsing redundant separators and up-level references so that A//B, A/B/, A/./B and A/foo/../B all become A/B.
                if not p in ps:
                    ps.append(p)

            # create list of files to upload
            file_transfers = []

            max_depth = 1  # default
            if DIR_SUPPORT and self.args.r:
                max_depth = MAX_DIR_DEPTH

            exclude = lambda f: f.startswith('.') or f.startswith('__')

            def get_files(upload_path, curr_path, level):
                if level < max_depth:  # skip files deeper than max depth
                    level += 1
                    for f in os.listdir(curr_path):
                        full_path = os.path.join(curr_path, f)
                        # skip hidden files and dirs
                        if not exclude(f):
                            if os.path.isfile(full_path):
                                f_size = os.path.getsize(full_path)
                                rel_path = full_path.replace(upload_path + ('' if upload_path.endswith('/') else '/'), '')
                                file_transfers.append(FileTransfer(path=full_path, key=rel_path, size=f_size))

                            elif os.path.isdir(full_path):
                                get_files(upload_path, full_path, level)

            for p in ps:
                if os.path.isfile(p):  # explicitly specified files, whether hidden or starts with '__' not skipped
                    f_size = os.path.getsize(p)
                    f_name = os.path.basename(p)
                    file_transfers.append(FileTransfer(path=p, key=f_name, size=f_size))

                elif os.path.isdir(p):  # recursively handle dir upload
                    get_files(p, p, 0)

            def upload_files(file_transfers, prefix):
                with ThreadPoolExecutor() as executor:
                    # submit each job and map future to file
                    futures = {
                        executor.submit(upload_file, file_transfer, prefix): file_transfer
                        for file_transfer in file_transfers
                    }
                    # collect each finished job
                    for future in concurrent.futures.as_completed(futures):
                        try:
                            res = future.result()  # read the result of the future object
                        except Exception as ex:
                            pass
                        finally:
                            pass
                            file_transfer = futures[future]  # match result back to file
                            # print(f, success)

            def upload_file(file_transfer, prefix):

                key = f"{prefix}{file_transfer.key}"
                if not self.args.o and self.aws.obj_exists(key):
                    file_transfer.status = 'File exists. Use -o to overwrite.'
                    file_transfer.successful = True
                    file_transfer.complete = True

                else:
                    try:
                        session = self.aws.new_session()
                        s3 = session.resource('s3')

                        ftype = filetype.guess(file_transfer.path)
                        # default contentType
                        contentType = 'application/octet-stream'
                        if ftype is not None:
                            contentType = ftype.mime
                        contentType += '; dcp-type=data'

                        s3.Bucket(self.aws.bucket_name).upload_file(Filename=file_transfer.path,
                                                                    Key=key,
                                                                    Callback=TransferProgress(file_transfer),
                                                                    ExtraArgs={'ContentType': contentType}
                                                                    )

                        # if file size is 0, callback will likely never be called
                        # and complete will not change to True
                        # hack
                        if file_transfer.size == 0:
                            file_transfer.status = 'Empty file.'
                            file_transfer.complete = True
                            file_transfer.successful = True

                    except Exception as thread_ex:
                        file_transfer.status = 'Upload failed.'
                        file_transfer.complete = True
                        file_transfer.successful = False

            print('Uploading...')
            upload_files(file_transfers, selected_area)
            return True, 'Successful upload.'

        except Exception as e:
            return False, format_err(e, 'upload')



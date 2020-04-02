import os

from hca_util.common import format_err
from hca_util.file_transfer import FileTransfer, TransferProgress, transfer
from hca_util.local_state import get_selected_area

"""
Uploading to Upload Service upload area
1. get upload creds from upload service api
2. upload via awscli or hca-util. set content-type accordingly
3. post fileUpload notification to upload service api
"""


class CmdUpload:
    """
    user: both wrangler and contributor
    aws resource or client used in command - s3 resource (Bucket().upload_file), s3 client list_objects_v2
    """

    def __init__(self, aws, args):
        self.aws = aws
        self.args = args

    def run(self):

        selected_area = get_selected_area()

        if not selected_area:
            return False, 'No area selected'

        try:
            # choice 1
            all_files = self.args.a  # optional bool

            fs = []
            if all_files:
                # upload files from current directory
                for f in os.listdir('.'):
                    # only files (not directories) and skip hidden files
                    if os.path.isfile(f) and not f.startswith('.'):
                        f_size = os.path.getsize(f)
                        fs.append(FileTransfer(key=f, size=f_size))
            else:

                # choice 2 upload specified list of files
                # optional list of <_io.TextIOWrapper name='f1' mode='r' encoding='UTF-8'>

                for f in self.args.f:
                    # argparse takes care of path expansion and check if file doesn't exist
                    f_size = os.path.getsize(f.name)
                    fs.append(FileTransfer(key=f.name, size=f_size))

            def upload(idx):
                try:
                    fname = fs[idx].key
                    key = selected_area + os.path.basename(fname)

                    # creating a new session for each file upload/thread, as it's unclear whether they're
                    # thread-safe or not

                    sess = self.aws.new_session()

                    if not self.args.o and self.aws.obj_exists(key):
                        fs[idx].status = 'File exists. Use -o to overwrite.'
                        fs[idx].complete = True
                    else:
                        res = sess.resource('s3')
                        # upload_file automatically handles multipart uploads via the S3 Transfer Manager
                        # put_object maps to the low-level S3 API request, it does not handle multipart uploads
                        res.Bucket(self.aws.bucket_name).upload_file(Filename=fname, Key=key,
                                                                     Callback=TransferProgress(fs[idx]))

                        # if file size is 0, callback will likely never be called
                        # and complete will not change to True
                        # hack
                        if fs[idx].size == 0:
                            fs[idx].status = 'Empty file.'
                            fs[idx].complete = True
                except Exception as thread_ex:
                    fs[idx].status = 'Upload failed.'
                    fs[idx].complete = True

            print('Uploading...')

            transfer(upload, fs)

            return True, 'Success upload'

        except Exception as e:
            return False, format_err(e, 'upload')

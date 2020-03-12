import os
from hca_util.local_state import get_selected_dir
from hca_util.common import print_err
from hca_util.file_transfer import FileTransfer, TransferProgress, transfer
from hca_util.command.select import key_exists
from hca_util.settings import DEBUG_MODE


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

        selected_dir = get_selected_dir()

        if not selected_dir:
            print('No directory selected')
            return

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

                for f in self.args.f :
                    # argparse takes care of path expansion and check if file doesn't exist
                    f_size = os.path.getsize(f.name)
                    fs.append(FileTransfer(key=f.name, size=f_size))

            def upload(idx):
                try:
                    fname = fs[idx].key
                    key = selected_dir + os.path.basename(fname)

                    # creating a new session for each file upload/thread, as it's unclear whether they're
                    # thread-safe or not

                    sess = self.aws.new_session()
                    client = sess.client('s3')

                    if not self.args.o and key_exists(client, self.aws.bucket_name, key):
                        fs[idx].status = 'File exists. Use -o to overwrite.'
                        fs[idx].complete = True
                    else:
                        res = sess.resource('s3')
                        # upload_file automatically handles multipart uploads via the S3 Transfer Manager
                        # put_object maps to the low-level S3 API request, it does not handle multipart uploads
                        res.Bucket(self.aws.bucket_name).upload_file(Filename=fname, Key=key,
                                                                     Callback=TransferProgress(fs[idx]))
                except Exception as thread_ex:
                    fs[idx].status = 'Upload failed.'
                    fs[idx].complete = True
                    if DEBUG_MODE:
                        print_err(thread_ex, 'upload')

            print('Uploading...')

            transfer(upload, fs)

        except Exception as e:
            print_err(e, 'upload')

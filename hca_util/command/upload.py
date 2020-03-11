import os
# from multiprocessing.dummy import Pool
import threading
from time import sleep
from hca_util.local_state import get_selected_dir
from hca_util.common import print_err
from hca_util.upload_progress import UploadProgress
from hca_util.command.select import key_exists

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

            if all_files:
                # upload files from current directory
                fs = [f for f in os.listdir('.') if os.path.isfile(f) and not f.startswith('.')]
            else:

                # choice 2
                files = self.args.f  # optional list of <_io.TextIOWrapper name='f1' mode='r' encoding='UTF-8'>

                # upload specified list of files
                fs = []
                for f in files:
                    # argparse takes care of path expansion and check if file doesn't exist
                    fs.append(f.name)

            print('Uploading...')

            progress_list = fs.copy()

            def upload(idx):
                f = fs[idx]
                key = selected_dir + os.path.basename(f)

                # creating a new session for each file upload/thread, as it's unclear whether they're
                # thread-safe or not

                sess = self.aws.new_session()
                client = sess.client('s3')

                if not self.args.o and key_exists(client, self.aws.bucket_name, key):
                    progress_list[idx] = "%s  File exists. Use -o to overwrite." % f
                    sleep(1)
                else:
                    res = sess.resource('s3')
                    # upload_file automatically handles multipart uploads via the S3 Transfer Manager
                    # put_object maps to the low-level S3 API request, it does not handle multipart uploads
                    res.Bucket(self.aws.bucket_name).upload_file(Filename=f, Key=key,
                                                                 Callback=UploadProgress(f, progress_list, idx))

            # with Pool(12) as p:
            #    p.map(lambda f: self.upload(f), fs)
            #    print('Done.')

            # using a thread per file upload instead of threadpool as they are cheap

            ts = []
            for i in range(0, len(fs)):
                t = threading.Thread(target=upload, args=(i,))
                ts.append(t)
                t.start()

            while [t for t in ts if t.is_alive()]:
                for p in progress_list:
                    print(p)
                sleep(0.5)  # 1 sec
                if [t for t in ts if t.is_alive()]:
                    print(f'\033[{len(fs) + 1}A\r')  # go back to start of first progress_list item

            print('Done')

        except Exception as e:
            print_err(e, 'upload')

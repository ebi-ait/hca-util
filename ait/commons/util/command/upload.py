import os
import filetype

from ait.commons.util.settings import DIR_SUPPORT, MAX_DIR_DEPTH
from ait.commons.util.common import format_err
from ait.commons.util.file_transfer import FileTransfer, TransferProgress, transfer
from ait.commons.util.local_state import get_selected_area


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
            fs = []

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
                                fs.append(FileTransfer(path=full_path, key=rel_path, size=f_size))

                            elif os.path.isdir(full_path):
                                get_files(upload_path, full_path, level)

            for p in ps:
                if os.path.isfile(p):  # explicitly specified files, whether hidden or starts with '__' not skipped
                    f_size = os.path.getsize(p)
                    f_name = os.path.basename(p)
                    fs.append(FileTransfer(path=p, key=f_name, size=f_size))

                elif os.path.isdir(p):  # recursively handle dir upload
                    get_files(p, p, 0)

            def upload(idx):
                try:
                    key = selected_area + fs[idx].key

                    # creating a new session for each file upload/thread, as it's unclear whether they're
                    # thread-safe or not

                    sess = self.aws.new_session()

                    if not self.args.o and self.aws.obj_exists(key):
                        fs[idx].status = 'File exists. Use -o to overwrite.'
                        fs[idx].successful = True
                        fs[idx].complete = True
                    else:
                        res = sess.resource('s3')
                        ftype = filetype.guess(fs[idx].path)
                        # default contentType
                        contentType = 'application/octet-stream'
                        if ftype is not None:
                            contentType = ftype.mime
                        contentType += '; dcp-type=data'
                        
                        # upload_file automatically handles multipart uploads via the S3 Transfer Manager
                        # put_object maps to the low-level S3 API request, it does not handle multipart uploads
                        res.Bucket(self.aws.bucket_name).upload_file(Filename=fs[idx].path, Key=key,
                                                                     Callback=TransferProgress(fs[idx]),
                                                                     ExtraArgs={'ContentType': contentType})

                        # if file size is 0, callback will likely never be called
                        # and complete will not change to True
                        # hack
                        if fs[idx].size == 0:
                            fs[idx].status = 'Empty file.'
                            fs[idx].complete = True
                            fs[idx].successful = True

                except Exception as thread_ex:
                    fs[idx].status = 'Upload failed.'
                    fs[idx].complete = True
                    fs[idx].successful = False

            print('Uploading...')
            transfer(upload, fs)

            self.files = [f for f in fs if f.successful]

            if all([f.successful for f in fs]):
                return True, 'Successful upload.'

            else:
                return False, 'Failed upload.'

        except Exception as e:
            return False, format_err(e, 'upload')

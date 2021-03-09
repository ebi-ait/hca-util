import os
import filetype

from ait.commons.util.settings import DIR_SUPPORT, MAX_DIR_DEPTH
from ait.commons.util.common import format_err
from ait.commons.util.local_state import get_selected_area
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor
from ait.commons.util.progress_bar import ProgressBar


class CmdUpload:
    """
    admin and user
    aws resource or client used in command - s3 resource (Bucket().upload_file)
    """

    def __init__(self, aws, args):
        self.aws = aws
        self.args = args
        self.files = []

    def upload_file(self, file_path, key):

        file_size = os.path.getsize(file_path)

        if not self.args.o and self.aws.obj_exists(key):
            print(f"{file_path} already exists. Use -o to overwrite.")

        elif file_size == 0:
            print(f"{file_path} is an empty file")

        else:
            session = self.aws.new_session()
            s3 = session.resource('s3')

            ftype = filetype.guess(file_path)
            # default contentType
            content_type = 'application/octet-stream'
            if ftype is not None:
                content_type = ftype.mime
            content_type += '; dcp-type=data'

            s3.Bucket(self.aws.bucket_name).upload_file(Filename=file_path,
                                                        Key=key,
                                                        Callback=ProgressBar(target=file_path, total=file_size),
                                                        ExtraArgs={'ContentType': content_type}
                                                        )

    def upload_files(self, files, prefix):

        with ThreadPoolExecutor() as executor:
            futures = {
                executor.submit(self.upload_file, file_path,
                                f"{prefix}{os.path.basename(file_path)}"): file_path
                for file_path in files
            }

            # collect each finished job
            success = True
            for future in concurrent.futures.as_completed(futures):
                try:
                    file_path = futures[future]
                    future.result()  # read the result of the future object
                except Exception as ex:
                    print(f"Exception raised for {file_path}: ", ex)
                    success = False

            return success

    def run(self):

        selected_area = get_selected_area()

        if not selected_area:
            return False, 'No area selected'

        try:

            ps = []
            for p in self.args.PATH:
                p = os.path.abspath(p)  # Normalize a pathname by collapsing redundant separators and up-level references so that A//B, A/B/, A/./B and A/foo/../B all become A/B.
                if not p in ps:
                    ps.append(p)

            # create list of files to upload
            files = []

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
                                files.append(full_path)

                            elif os.path.isdir(full_path):
                                get_files(upload_path, full_path, level)

            for p in ps:
                if os.path.isfile(p):  # explicitly specified files, whether hidden or starts with '__' not skipped
                    files.append(p)

                elif os.path.isdir(p):  # recursively handle dir upload
                    get_files(p, p, 0)

            print('Uploading...')

            success = self.upload_files(files, selected_area)
            return (success, "Successful upload") if success else (success, "Failed upload")

        except Exception as e:
            return False, format_err(e, 'upload')



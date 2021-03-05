import os
import filetype

from ait.commons.util.settings import DIR_SUPPORT, MAX_DIR_DEPTH
from ait.commons.util.common import format_err
from ait.commons.util.local_state import get_selected_area
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor
import threading
from tqdm import tqdm


class CmdUpload:
    """
    admin and user
    aws resource or client used in command - s3 resource (Bucket().upload_file)
    """

    def __init__(self, aws, args):
        self.aws = aws
        self.args = args
        self.files = []

    def upload_file(self, f, key):
        session = self.aws.new_session()
        s3 = session.resource('s3')

        ftype = filetype.guess(f)
        # default contentType
        content_type = 'application/octet-stream'
        if ftype is not None:
            content_type = ftype.mime
        content_type += '; dcp-type=data'

        s3.Bucket(self.aws.bucket_name).upload_file(Filename=f,
                                                    Key=key,
                                                    Callback=ProgressBar(target=f, total=os.path.getsize(f)),
                                                    ExtraArgs={'ContentType': content_type}
                                                    )
        return True

    def upload_files(self, files, prefix):

        with ThreadPoolExecutor() as executor:
            # submit each job and map future to file
            futures = {}
            for f in files:
                key = f"{prefix}{os.path.basename(f)}"
                size = os.path.getsize(f)

                if not self.args.o and self.aws.obj_exists(key):
                    print(f"{f} already exists. Use -o to overwrite.")

                elif size == 0:
                    print(f"{f} is an empty file")

                else:
                    futures[executor.submit(self.upload_file, f, key)] = f

            # collect each finished job
            success = True
            for future in concurrent.futures.as_completed(futures):
                try:
                    f = futures[future]
                    future.result()  # read the result of the future object
                except Exception as ex:
                    print(f"Exception raised for {f}: ", ex)
                    success = False

            return success

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


class ProgressBar:
    def __init__(self, target, total):
        self._target = target
        self._total = total
        self._seen_so_far = 0
        self._lock = threading.Lock()

    def __call__(self, bytes_amount):
        with tqdm(total=self._total, desc=self._target) as pbar:
            with self._lock:
                self._seen_so_far += bytes_amount
            pbar.update(self._seen_so_far)


import os
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
            prefix = selected_dir
            s3_resource = self.aws.common_session.resource('s3')
            bucket = s3_resource.Bucket(self.aws.bucket_name)

            # choice 1
            all_files = self.args.a  # optional bool

            fs = []
            if all_files:
                # download all files from selected directory
                for obj in bucket.objects.filter(Prefix=prefix):
                    # skip the top-level directory
                    if obj.key == prefix:
                        continue
                    fs.append(obj.key)
            else:
                # choice 2
                # download specified file(s) only
                fs = [f'{prefix}{f}' for f in self.args.f]

            print('Downloading...')

            for f in fs:
                # todo check if f exists
                if not os.path.exists(os.path.dirname(f)):
                    os.makedirs(os.path.dirname(f))
                bucket.download_file(f, f)
                print(f)

        except Exception as e:
            print_err(e, 'download')

from hca_util.local_state import set_selected_dir
from hca_util.common import print_err


class CmdSelect:

    def __init__(self, aws, args):
        self.aws = aws
        self.args = args

    def run(self):
        dir_name = self.args.DIR if self.args.DIR.endswith('/') else f'{self.args.DIR}/'

        try:
            s3_resource = self.aws.common_session.resource('s3')
            bucket = s3_resource.Bucket(self.aws.bucket_name)
            bucket.Object(dir_name)

            set_selected_dir(dir_name)
            print('Selected ' + dir_name)

        except Exception as e:
            print_err(e, 'select')

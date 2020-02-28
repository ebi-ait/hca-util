from hca_util.local_state import get_selected_dir

from hca_util.common import print_err


class CmdList:

    def __init__(self, aws, args):
        self.aws = aws
        self.args = args

    def run(self):

        if self.args.b:  # list all dirs in bucket
            if self.aws.is_contributor:
                print('You don\'t have permission to use this command')
                return
            try:
                s3_resource = self.aws.common_session.resource('s3')
                bucket = s3_resource.Bucket(self.aws.bucket_name)

                for obj in bucket.objects.all():
                    k = obj.key
                    if k.endswith('/'):
                        n = obj.Object().metadata.get('name')
                        print(k + (f' {n}' if n else ''))

            except Exception as e:
                print_err(e, 'list')

        else:  # list selected dir contents

            selected_dir = get_selected_dir()

            if not selected_dir:
                print('No directory selected')
                return

            try:
                selected_dir += '' if selected_dir.endswith('/') else '/'

                s3_resource = self.aws.common_session.resource('s3')
                bucket = s3_resource.Bucket(self.aws.bucket_name)

                for obj in bucket.objects.filter(Prefix=selected_dir):
                    k = obj.key
                    if not k.endswith('/'):
                        print(k)

            except Exception as e:
                print_err(e, 'list')

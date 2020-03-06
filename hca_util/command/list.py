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
                        print(k, end=' ')
                        obj_meta = obj.Object().metadata
                        if obj_meta:
                            if 'perms' in obj_meta:
                                p = obj_meta.get('perms')
                                print(p.ljust(3), end=' ')
                            if 'name' in obj_meta:
                                n = obj_meta.get('name')
                                print(f'{n}' if n else '')
                        print()

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

                file_count = 0
                for obj in bucket.objects.filter(Prefix=selected_dir):
                    k = obj.key
                    #if not k.endswith('/'):
                    #    print(k)
                    print(k)
                    file_count += 1

                print(f'{file_count-1} files')

            except Exception as e:
                print_err(e, 'list')

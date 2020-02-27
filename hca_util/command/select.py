from .command import HcaCmd


class CmdSelect(HcaCmd):

    def cmd_select(self, argv):
        if not self.setup_ok:
            print(f'Setup failed: \nSee `help config` for help to configure your credentials')
            return

        if len(argv) == 1:
            dir_name = argv[0]
            if is_valid_dir_name(dir_name):

                dir_name += '' if dir_name.endswith('/') else '/'

                try:
                    s3_resource = self.aws.session.resource('s3')
                    bucket = s3_resource.Bucket(self.bucket_name)
                    bucket.Object(dir_name)
                    # serialize(select_dir, dir_name)
                    self.selected_dir = dir_name
                    print('Selected ' + dir_name)

                except Exception as e:
                    print(f'An exception of type {e.__class__.__name__} occurred in cmd select.\nDetail: ' + str(e))

            else:
                print('Invalid directory name')

        else:
            print('Invalid args. See `help select`')
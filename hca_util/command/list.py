from .command import HcaCmd


class CmdList(HcaCmd):

    def cmd_list(self, argv):
        if not self.setup_ok:
            print(f'Setup failed: \nSee `help config` for help to configure your credentials')
            return

        if len(argv) == 0 or len(argv) == 1:

            try:
                s3_resource = self.aws.session.resource('s3')
                bucket = s3_resource.Bucket(self.bucket_name)

                if len(argv) == 0:

                    for obj in bucket.objects.all():
                        k = obj.key
                        if k.endswith('/'):
                            n = obj.Object().metadata.get('name')
                            print(k + (f' {n}' if n else ''))
                else:
                    dir_name = argv[0]
                    if is_valid_dir_name(dir_name):

                        dir_name += '' if dir_name.endswith('/') else '/'

                        for obj in bucket.objects.filter(Prefix=dir_name):
                            k = obj.key
                            if not k.endswith('/'):
                                print(k)

                    else:
                        print('Invalid directory name')
            except Exception as e:
                print(f'An exception of type {e.__class__.__name__} occurred in cmd list.\nDetail: ' + str(e))

        else:
            print('Invalid args. See `help list`')

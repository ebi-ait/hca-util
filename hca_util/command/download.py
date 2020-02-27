from .command import HcaCmd


class CmdDownload(HcaCmd):

    def cmd_download(self, argv):
        if not self.setup_ok:
            print(f'Setup failed: \nSee `help config` for help to configure your credentials')
            return

        if self.selected_dir is None:
            print('No directory selected')
            return

        if len(argv) < 1:
            print('Invalid args. See `help download`')
            return

        try:
            prefix = self.selected_dir
            s3_resource = self.aws.session.resource('s3')
            bucket = s3_resource.Bucket(self.bucket_name)
            if len(argv) == 1 and argv[0] == '.':
                # download all files from selected directory
                for obj in bucket.objects.filter(Prefix=prefix):
                    # do not download folder object
                    if obj.key == prefix:
                        continue
                    print('Downloading ' + obj.key)
                    if not os.path.exists(os.path.dirname(obj.key)):
                        os.makedirs(os.path.dirname(obj.key))
                    bucket.download_file(obj.key, obj.key)
            else:
                # download specified file(s) from selected directory
                for f in argv:
                    print('Downloading ' + prefix + f)
                    obj = bucket.Object(prefix + f)
                    if not os.path.exists(os.path.dirname(obj.key)):
                        os.makedirs(os.path.dirname(obj.key))
                    obj.download_file(obj.key)

        except Exception as e:
            print(f'An exception of type {e.__class__.__name__} occurred in cmd config.\nDetail: ' + str(e))

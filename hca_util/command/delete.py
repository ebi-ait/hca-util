from .command import HcaCmd


class CmdDelete(HcaCmd):

    def cmd_delete(self, argv):
        if not self.setup_ok:
            print(f'Setup failed: \nSee `help config` for help to configure your credentials')
            return

        if self.selected_dir is None:
            print('No directory selected')
            return

        try:
            prefix = self.selected_dir
            s3_resource = self.aws.session.resource('s3')
            bucket = s3_resource.Bucket(self.bucket_name)

            if len(argv) == 0:
                # delete an entire directory
                confirm = input(f'Confirm delete {self.selected_dir} and its content? Y/y to proceed: ')
                if confirm == 'Y' or confirm == 'y':
                    print('Deleting...')

                    for obj in bucket.objects.filter(Prefix=prefix):
                        print('Deleting ' + obj.key)
                        obj.delete()

                    # TODO delete bucket policy for HCAContributer-folder permissions

                    # reset selected dir
                    self.selected_dir = None
                    print('Selected dir: None')

                else:
                    print('Delete cancelled')

                return

            if len(argv) == 1 and argv[0] == '.':
                # delete all files in selected directory
                for obj in bucket.objects.filter(Prefix=prefix):
                    # do not delete folder object
                    if obj.key == prefix:
                        continue
                    print('Deleting ' + obj.key)
                    obj.delete()
            else:
                # delete specified file(s) in selected directory
                for f in argv:
                    print('Deleting ' + prefix + f)
                    obj = bucket.Object(prefix + f)
                    obj.delete()

        except Exception as e:
            print(f'An exception of type {e.__class__.__name__} occurred in cmd delete.\nDetail: ' + str(e))
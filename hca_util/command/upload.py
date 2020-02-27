from .command import HcaCmd


class CmdUpload(HcaCmd):

    def cmd_upload(self, argv):
        if not self.setup_ok:
            print(f'Setup failed: \nSee `help config` for help to configure your credentials')
            return

        if len(argv) > 0:

            if self.selected_dir is None:
                print('No directory selected')
            else:
                if len(argv) == 1 and argv[0] == '.':
                    # upload files from current directory
                    fs = [f for f in os.listdir('.') if os.path.isfile(f) and not f.startswith('.')]
                else:
                    # upload specified list of files
                    fs = []
                    for f in argv:
                        if f.startswith('~'):
                            f = os.path.expanduser(f)
                        if os.path.exists(f):
                            fs.append(f)
                        else:
                            print(f'{f} doesn\'t exist')

                if len(fs) > 0:
                    print('Uploading...')

                    try:
                        # with Pool(12) as p:
                        #    p.map(lambda f: self.upload(f), fs)
                        #    print('Done.')
                        up = 0
                        for f in fs:
                            try:
                                self.upload(f)
                                up += 1
                                print()
                            except:
                                print(f'An error occurred while uploading {f}')
                        print(f'{up} uploaded')

                    except Exception as e:
                        print(f'An exception of type {e.__class__.__name__} occurred in cmd upload.\nDetail: ' + str(e))
                else:
                    print('Nothing to upload.')

        else:
            print('Invalid args. See `help upload`')


"""
It is recommended to create a resource instance for each thread / process in a multithreaded or 
multiprocess application rather than sharing a single instance among the threads / processes
"""


def upload(self, f):
    fname = os.path.basename(f)
    # upload_file automatically handles multipart uploads via the S3 Transfer Manager
    # put_object maps to the low-level S3 API request, it does not handle multipart uploads
    self.aws.session.resource('s3').Bucket(self.bucket_name) \
        .upload_file(Filename=f, Key=self.selected_dir + fname,
                     Callback=UploadProgress(f))
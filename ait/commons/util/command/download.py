import os

import botocore

from ait.commons.util.common import format_err
from ait.commons.util.file_transfer import FileTransfer, TransferProgress, transfer
from ait.commons.util.local_state import get_selected_area


class CmdDownload:
    """
    admin and user
    aws resource or client used in command - s3 resource (Bucket().upload_file)
    """

    def __init__(self, aws, args):
        self.aws = aws
        self.args = args
        self.files = []

    def run(self):

        selected_area = get_selected_area()

        if not selected_area:
            return False, 'No area selected'

        try:
            s3_resource = self.aws.common_session.resource('s3')
            bucket = s3_resource.Bucket(self.aws.bucket_name)

            # choice 1
            all_files = self.args.a  # optional bool

            fs = []
            if all_files:
                # download all files from selected area
                for obj in bucket.objects.filter(Prefix=selected_area):
                    # skip the top-level directory
                    if obj.key == selected_area:
                        continue
                    fs.append(FileTransfer(path=os.getcwd(), key=obj.key, size=obj.size))
            else:
                # choice 2
                # download specified file(s) only

                for f in self.args.f:
                    # check if f exists
                    key = f'{selected_area}{f}'
                    try:
                        # if you're able to download (s3:GetObject) you can do HEAD Object which
                        # is used by resource.ObjectSummary
                        obj_summary = s3_resource.ObjectSummary(self.aws.bucket_name, key)
                        obj_size = obj_summary.size
                    except botocore.exceptions.ClientError as e:
                        if e.response['Error']['Code'] == "404":
                            fs.append(FileTransfer(path=os.getcwd(), key=key, status='File not found.', complete=True))
                        elif e.response['Error']['Code'] == "403":
                            # An error occurred (403) when calling the HeadObject operation: Forbidden
                            fs.append(FileTransfer(path=os.getcwd(), key=key, status='Access denied.', complete=True))
                        else:
                            # Something else has gone wrong.
                            fs.append(FileTransfer(path=os.getcwd(), key=key, status='Download error.', complete=True))
                    else:
                        fs.append(FileTransfer(path=os.getcwd(), key=key, size=obj_size))

            def download(idx):
                try:
                    file = fs[idx].key
                    os.makedirs(os.path.dirname(file), exist_ok=True)

                    s3 = self.aws.new_session().resource('s3')
                    s3.Bucket(self.aws.bucket_name).download_file(file, file, Callback=TransferProgress(fs[idx]))

                    # if file size is 0, callback will likely never be called
                    # and complete will not change to True
                    # hack
                    if fs[idx].size == 0:
                        fs[idx].status = 'Empty file.'
                        fs[idx].complete = True
                        fs[idx].successful = True

                except Exception as thread_ex:
                    if 'Forbidden' in str(thread_ex) or 'AccessDenied' in str(thread_ex):
                        fs[idx].status = 'Access denied.'
                    else:
                        fs[idx].status = 'Download failed.'
                    fs[idx].complete = True
                    fs[idx].successful = False

            print('Downloading...')

            transfer(download, fs)

            self.files = [f for f in fs if f.successful]

            if all([f.successful for f in fs]):
                return True, 'Successful download.'
            else:
                return False, 'Failed download.'

        except Exception as e:
            return False, format_err(e, 'download')

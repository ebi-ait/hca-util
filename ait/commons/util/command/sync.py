import os
import json
import requests

from botocore.exceptions import ClientError

from ait.commons.util.aws_client import Aws
from ait.commons.util.bucket_policy import new_policy_statement
from ait.commons.util.common import gen_uuid, format_err, INGEST_UPLOAD_AREA_PREFIX
from ait.commons.util.file_transfer import FileTransfer, TransferProgress, transfer
from ait.commons.util.local_state import get_selected_area

UPLOAD_SERVICE_API = 'https://upload__ENV__archive.data.humancellatlas.org'


class CmdSync:
    """
    Upload srv steps
    1. get creds from upload srv api
    2. upload via awscli or hca-util (set content-type accordingly)
    3. post notification to upload srv api
    """

    def __init__(self, aws: Aws, args):
        self.aws = aws
        self.args = args

    def run(self):
        if not self.aws:
            return False, 'You need configure your profile first'

        if self.aws.is_user:
            return False, 'You don\'t have permission to use this command'

        selected_area = get_selected_area()

        if not selected_area:
            return False, 'No area selected'
        
        dest_bucket, dest_env, dest_upload_area_uuid = self.args.INGEST_UPLOAD_AREA

        try:

            s3_resource = self.aws.common_session.resource('s3')
            bucket = s3_resource.Bucket(self.aws.bucket_name)

            fs = []

            # get all files from selected area
            for obj in bucket.objects.filter(Prefix=selected_area):
                # skip the top-level directory
                if obj.key == selected_area:
                    continue
                contentType = obj.get().get('ContentType')
                # using path for contentType
                fs.append(FileTransfer(path=contentType, key=obj.key, size=obj.size))
                
            def copy(idx):
                try:
                    k = fs[idx].key
                    s3 = self.aws.new_session().resource('s3')
                    copy_source = {
                        'Bucket': self.aws.bucket_name,
                        'Key': k
                    }
                    filename = k[37:]

                    dest_key = dest_upload_area_uuid + '/' + filename
                    s3.meta.client.copy(copy_source, dest_bucket, dest_key, 
                                        Callback=TransferProgress(fs[idx]), 
                                        ExtraArgs={'ContentType': fs[idx].path})
                    
                    # if file size is 0, callback will likely never be called
                    # and complete will not change to True
                    # hack
                    if fs[idx].size == 0:
                        fs[idx].status = 'Empty file.'
                        fs[idx].complete = True
                        fs[idx].successful = True

                    if notify_upload(dest_env, dest_upload_area_uuid, filename):
                        fs[idx].status = 'Transferred. Notify failed.'
                        fs[idx].complete = True
                        fs[idx].successful = False


                except Exception as thread_ex:
                    if 'Forbidden' in str(thread_ex) or 'AccessDenied' in str(thread_ex):
                        fs[idx].status = 'Access denied.'
                    else:
                        fs[idx].status = 'Transfer failed.'
                    fs[idx].complete = True
                    fs[idx].successful = False

            print('Transferring...')
            transfer(copy, fs)

            self.files = [f for f in fs if f.successful]

            if all([f.successful for f in fs]):
                return True, 'Transfer complete.'
            else:
                return False, 'Transfer error.'
            
        except Exception as e:
            return False, format_err(e, 'sync')


"""
Upload service api endpoints
POST /v1/area/{upload_area_uuid}/credentials    Create credentials for access to this upload area
POST /v1/area/{upload_area_uuid}/{filename}     Notify upload of uploaded file
HEAD /v1/area/{upload_area_uuid}                Check if an upload area exists
"""

def upload_api_url(env, upload_area_uuid):
    sub = '.' if env == 'prod' else f'.{env}.'
    url = UPLOAD_SERVICE_API.replace("__ENV__", sub) + '/v1/area/' + upload_area_uuid
    return url


def create_creds(env, upload_area_uuid):
    r = requests.post(upload_api_url(env, upload_area_uuid) + '/credentials')
    if r.status_code == 201:
        # Created
        return r.json()
    #elif r.status_code == 404:
    #    # Upload area not found
    #    print(r.json())


def notify_upload(env, upload_area_uuid, filename):
    try:
        r = requests.post(upload_api_url(env, upload_area_uuid) + '/' + filename)
        if r.status_code == 202:
            return True # File upload notification added to queue
    except requests.exceptions.RequestException as e:
        pass # silently pass
    return False # notify failed


def check_upload_area_exists(env, upload_area_uuid):
    try:
        r = requests.head(upload_api_url(env, upload_area_uuid))
        if r.status_code == 200:
            return True
        else:
            # Upload area does not exist.
            return False
    except requests.exceptions.RequestException as e:
        print(str(e))

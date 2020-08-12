import json
import requests
import urllib.parse


UPLOAD_SERVICE_API = 'https://upload__ENV__archive.data.humancellatlas.org'

"""
Upload service steps to trigger data validation
1. get creds from upload srv api
2. upload data via awscli or hca-util (set content-type accordingly)
3. post notification to upload srv api

API endpoints
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
        notify_url = upload_api_url(env, upload_area_uuid) + '/' + urllib.parse.quote(filename)
        r = requests.post(notify_url)
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

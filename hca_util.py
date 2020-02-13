#!/usr/bin/python

import os
import sys
import boto3
from botocore.exceptions import ClientError, ProfileNotFound
import json
import subprocess
from multiprocessing.dummy import Pool
from common import *
from upload_progress import *
from aws import *


class HcaUtil:
    # use creds from [hca-util] section of ~/.aws/credentials
    # and config from [profile hca-util] section of ~/.aws/config
    profile_name = 'hca-util'
    secret_name = 'hca/util/secret'

    session = None
    awsClient = None
    bucket_name = None
    selected_dir = None

    profile_found = False
    access_ok = False

    # default constructor
    def __init__(self):
        # set a new session
        self.set_session()

        # only proceed if profile exists
        if profile_found:
            self.awsClient = Aws(session)
            # verify user config/creds

            # retrieve bucket name
            self.bucket_name = get_bucket_name()

    # set up functions
    def set_session(self):
        try:
            self.session = boto3.Session(profile_name=profile_name)
            profile_found = True
        except ProfileNotFound:
            print(f'`{profile_name}` profile not found. See `help config` for help to configure your credentials')

    def get_bucket_name(self):
        return self.awsClient.secret_mgr_get_bucket_name(secret_name)

    # command functions
    def cmd_config(self, argv):

        if len(argv) == 2:
            access_key = argv[0]
            secret_key = argv[1]
            configure(access_key, secret_key)
            print('Done.')
        else:
            print('Invalid args. See `help config`')

    def cmd_dir(self,argv):
        """Returns currently selected dir or None."""
        return self.selected_dir



# hca-wrangler - have full s3 access
# hca-contributer - access limited to created folder/object within bucket, added each time to bucket policy when a bucket
# is created -- REVIEW
def cmd_create(argv):
    nameStr = ''
    if len(argv) == 0:
        print('Name: <none>')
    elif len(argv) == 1:
        name = argv[0]
        print('Name: ' + name)
        if name.isalnum() and 0 < len(name) < 13:
            print('(Valid)')
            nameStr = name
        else:
            print('(Invalid) Ignoring')

    # generate a uuid for directory name
    dir_name = gen_uuid() + (f'-{nameStr}' if nameStr else '')
    try:
        bucket_name = get_bucket_name()
        self.awsClient.s3_create_dir(bucket_name, dir_name)
        print('Created ' + dir_name)
    except Exception as e:
        print(str(e))
        sys.exit(1)





# hca-wrangler and hca-contributor
def cmd_list(argv):
    if len(argv) == 0 or len(argv) == 1:
        bucket_name = get_bucket_name()

        try:
            s3 = session.client('s3')
            if len(argv) == 0:
                resp = s3.list_objects_v2(Bucket=bucket_name)
                list_objs(resp)
            else:
                dir_name = argv[0]
                if is_valid_dir_name(dir_name):
                    resp = s3.list_objects_v2(Bucket=bucket_name, Prefix=dir_name+'/')
                    list_objs(resp)
                else:
                    print('Invalid directory name')
        except ClientError as e:
            print(str(e))

    else:
        m = """usage:
        hca_util.py list               List contents of bucket (wrangler only)
        hca_util.py list <dir_name>    List contents of directory
        """
        print(m)


def list_objs(resp):
    if resp.get('Contents'):
        for obj in resp['Contents']:
            print(obj['Key'])
    else:
        print('None')


def cmd_select(argv):

    if len(argv) == 1:
        dir_name = argv[0]
        if is_valid_dir_name(dir_name):
            bucket_name = get_bucket_name()

            try:
                s3 = session.client('s3')
                s3.head_object(Bucket=bucket_name, Key=dir_name + '/')
                serialize(select_dir, dir_name)
                print('Selected ' + dir_name)

            except ClientError:
                print('Directory not found')
        else:
            print('Invalid directory name')

    else:
        m = """usage:
            hca_util.py select <dir_name>  Select directory
            """
        print(m)





def cmd_upload(argv):

    if len(argv) > 0:
        dir_name = dir()

        if dir_name is None:
            print('No directory selected')
        else:
            if len(argv) == 1 and argv[0] == '.':
                # upload files from current directory
                fs = [f for f in os.listdir('.') if os.path.isfile(f)]
            else:
                # upload specified list of files
                fs = [f for f in argv if os.path.exists(f)]

            upload(dir_name, fs)
    else:
        m = """usage:
        hca_util.py upload <f1> [<f2>..]   Upload specified file or files. Error if no directory selected
        hca_util.py upload .           Upload all files in current directory. Error if no directory selected
        """
        print(m)


def cmd_download():
    pass


def upload(dir_name, fs):
    print('Uploading...')
    bucket = get_bucket_name()
    try:
        s3 = session.client('s3')
        with Pool(12) as p:
            p.map(lambda f: u(s3, f, bucket, dir_name), fs)

        print('Done')
    except ClientError as e:
        print(str(e))


def u(s3, f, bucket, dir_name):
    print(f)
    s3.upload_file(f, bucket, dir_name + '/{}'.format(f), Callback=UploadProgress(f))


def usage():
    return """usage: 
    """


def main(argv):

    if len(argv) > 0:

        cmd = argv[0]

        global session
        set_session()
        if session is None:
            exit()

        if cmd == 'config':
            cmd_config(argv[1:])

        elif cmd == 'create':
            cmd_create(argv[1:])

        elif cmd == 'list':
            cmd_list(argv[1:])

        elif cmd == 'select':
            cmd_select(argv[1:])

        elif cmd == 'dir':
            if len(argv[1:]) > 0:
                print('Ignoring params after `dir` command')
            print(dir())

        elif cmd == 'upload':
            cmd_upload(argv[1:])

        elif cmd == 'download':
            cmd_download()

        else:
            print(usage())
    else:
        print(usage())


if __name__ == "__main__":
    main(sys.argv[1:])

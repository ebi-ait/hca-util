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

# use creds from [hca-util] section of ~/.aws/credentials
# and config from [profile hca-util] section of ~/.aws/config
profile_name = 'hca-util'

default_region = 'us-east-1'
secret_name = 'hca/util/secret'
select_dir = 'select_dir'


bucket_policy = {
    'Version': '2012-10-17',
    'Statement': [{
        'Sid': 'AddPerm',
        'Effect': 'Allow',
        'Principal': '*',
        'Action': ['s3:GetObject'],
        'Resource': f'arn:aws:s3:::<bucket_name>/*'
    }]
}

session = None


def set_session():
    try:
        global session # needed to set global var, not needed to only read
        session = boto3.Session(profile_name=profile_name)
    except ProfileNotFound:
        print(f'`{profile_name}` profile not found. Run `configure` command with your credentials')


def get_caller_arn():
    sts = session.client('sts')
    resp = sts.get_caller_identity()
    arn = resp.get('Arn')
    return arn


def get_bucket_name():
    # because you can't attach an access policy to a secret, allow action GetSecretValue for the hca-contributor group
    try:
        secret_mgr = session.client('secretsmanager')
        resp = secret_mgr.get_secret_value(SecretId=secret_name)
        secret_str = resp['SecretString']
        return json.loads(secret_str)['s3-bucket']
    except Exception as e:
        raise e


# hca-wrangler - have full s3 access
# hca-contributer - access limited to created folder/object within bucket, added each time to bucket policy when a bucket
# is created -- REVIEW
def handle_create():
    # generate a uuid for directory name
    dir_name = gen_uuid()
    bucket_name = get_bucket_name()
    try:
        s3 = session.client('s3')
        s3.put_object(Bucket=bucket_name, Key=(dir_name + '/'))
        print('Created ' + dir_name)
    except Exception as e:
        print('Error creating directory ' + str(e))


# hca-wrangler and hca-contributor
def handle_list(argv):
    if len(argv) == 0 or len(argv) == 1:
        bucket_name = get_bucket_name()

        try:
            s3 = session.client('s3')
            if len(argv) == 0:
                resp = s3.list_objects_v2(Bucket=bucket_name)
                list_objs(resp)
            else:
                dir_name = argv[0]
                if is_valid_uuid(dir_name):
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


def handle_select(argv):

    if len(argv) == 1:
        dir_name = argv[0]
        if is_valid_uuid(dir_name):
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


def dir():
    try:
        sel_dir = deserialize(select_dir)
    except (OSError, IOError) as e:
        sel_dir = None

    return sel_dir


def handle_upload(argv):

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


def handle_download():
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
    s3.upload_file(f, bucket, dir_name + '/{}'.format(f), Callback=ProgressPercentage(f))


def usage():
    return """usage: 
    hca_util.py config <access> <secret>    Configure your machine with credentials
    hca_util.py create             Create an upload directory (wrangler only)
    hca_util.py list               List contents of bucket (wrangler only)
    hca_util.py select <dir_name>  Select directory
    hca_util.py list <dir_name>    List contents of directory
    hca_util.py dir                Show selected directory
    hca_util.py upload <f1> [<f2>..]   Upload specified file or files. Error if no directory selected
    hca_util.py upload .           Upload all files in current directory. Error if no directory selected
    hca_util.py download           Download all files from selected directory
    hca_util.py download <f1>[<f2>..] Download specified files from selected directory
    """


def main(argv):

    if len(argv) > 0:

        cmd = argv[0]

        global session
        set_session()
        if session is None:
            exit()

        if cmd == 'configure':
            handle_configure(argv[1:])

        if cmd == 'create':
            if len(argv[1:]) > 0:
                print('Ignoring params after `create` command')
            handle_create()

        elif cmd == 'list':
            handle_list(argv[1:])

        elif cmd == 'select':
            handle_select(argv[1:])

        elif cmd == 'dir':
            if len(argv[1:]) > 0:
                print('Ignoring params after `dir` command')
            print(dir())

        elif cmd == 'upload':
            handle_upload(argv[1:])

        elif cmd == 'download':
            handle_download()

        else:
            print(usage())
    else:
        print(usage())


if __name__ == "__main__":
    main(sys.argv[1:])

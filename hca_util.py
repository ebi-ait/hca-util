#!/usr/bin/python

import os
import sys
import boto3
import json

from common import *


secret_name = 'tmp/upload/test/loc'
select_dir = 'select_dir'


def get_bucket_name():
    secret_mgr = boto3.client('secretsmanager')
    try:
        resp = secret_mgr.get_secret_value(SecretId=secret_name)
        secret_str = resp['SecretString']
        return json.loads(secret_str)['s3-bucket']
    except Exception:
        return None


def handle_create():
    # generate a uuid for directory name
    dir_name = gen_uuid()
    bucket_name = get_bucket_name()
    s3 = boto3.client('s3')
    try:
        s3.put_object(Bucket=bucket_name, Key=(dir_name + '/'))
        print('Created ' + dir_name)
    except Exception as e:
        print('Error creating directory ' + str(e))


def handle_list(argv):
    if len(argv) == 0 or len(argv) == 1:
        bucket_name = get_bucket_name()
        s3 = boto3.client('s3')

        if len(argv) == 0:
            resp = s3.list_objects_v2(Bucket=bucket_name)
            list_objs(resp)
        else:
            dir_name = argv[0]
            if is_valid_uuid(dir_name):
                resp = s3.list_objects_v2(Bucket=bucket_name, Prefix=dir_name)
                list_objs(resp)
            else:
                print('Invalid directory name')
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
            s3 = boto3.client('s3')
            resp = s3.list_objects_v2(Bucket=bucket_name, Prefix=dir_name)

            if resp.get('Contents'):
                serialize(select_dir, dir_name)
                print('Selected ' + dir_name)
            else:
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
        if len(argv) == 1 and argv[0] == '.':
            # upload files from current directory
            fs = [f for f in os.listdir('.') if os.path.isfile(f)]
        else:
            # upload specified list of files
            fs = [f for f in argv if os.path.exists(f)]

    else:
        m = """usage:
        hca_util.py upload <f1> [<f2>..]   Upload specified file or files. Error if no directory selected
        hca_util.py upload .           Upload all files in current directory. Error if no directory selected
        """
        print(m)


def handle_download():
    pass


def usage():
    return """usage: 
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

        if cmd == 'create':
            handle_create()

        elif cmd == 'list':
            handle_list(argv[1:])

        elif cmd == 'select':
            handle_select(argv[1:])

        elif cmd == 'dir':
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

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
    aws = None
    bucket_name = None
    setup_ok = False

    selected_dir = None

    # default constructor
    def __init__(self):
        self.setup()

    # setup function
    def setup(self):
        try:
            # try to set a session using profile_name
            self.session = boto3.Session(profile_name=profile_name)
            profile_found = True
            # use profile to create clients for aws services: s3, secret_mgr, sts
            self.aws = Aws(session)
            # get bucket name from aws secrets (also serve as a way to validate user config/creds)
            self.bucket_name = self.aws.secret_mgr_get_bucket_name(secret_name)
            if bucket_name
            self.setup_ok = True
        except ProfileNotFound:
            print(f'Setup failed: \n`{profile_name}` profile not found. ' + str(e))
        except Exception as e:
            print(f'Setup failed: \n' + str(e))

        if not self.setup_ok:
            print('See `help config` for help to configure your credentials')

    # can't proceed with most common if setup nok
    # except: config, dir

    # command functions
    def cmd_config(self, argv):

        if len(argv) == 2:
            access_key = argv[0]
            secret_key = argv[1]
            try:
                self.aws.configure(access_key, secret_key)
                print('Done.')
            except Exception as e:
                print('Error occurred running `config` command: ' + str(e))
        else:
            print('Invalid args. See `help config`')


    def cmd_create(self, argv):
        if not self.setup_ok:
            print(f'Setup failed: \nSee `help config` for help to configure your credentials')
            return
        project_name = ''
        if len(argv) == 0:
            print('Project name: <none specified>')
        elif len(argv) == 1:
            name = argv[0]
            print('Project name: ' + name)
            if is_valid_project_name(name):
                print('(Valid)')
                project_name = name
            else:
                print('(Invalid) Ignoring')

            # generate a uuid for directory name
            dir_name = gen_uuid() + (f'-{project_name}' if project_name else '')

            try:
                self.aws.s3.put_object(Bucket=self.bucket_name, Key=(dir_name + '/'))
                print('Created ' + dir_name)
            except Exception as e:
                print('Error occurred creating directory: ' + str(e))

        else:
            print('Invalid args. See `help create`')


    def cmd_list(self, argv):
        if not self.setup_ok:
            print(f'Setup failed: \nSee `help config` for help to configure your credentials')
            return

        if len(argv) == 0 or len(argv) == 1:

            try:
                if len(argv) == 0:
                    resp = self.aws.s3.list_objects_v2(Bucket=bucket_name)
                    list_objs(resp)
                else:
                    dir_name = argv[0]
                    if is_valid_dir_name(dir_name):
                        resp = self.aws.s3.list_objects_v2(Bucket=bucket_name, Prefix=dir_name+'/')
                        list_objs(resp)
                    else:
                        print('Invalid directory name')
            except Exception as e:
                print('Error occurred listing directory: ' + str(e))

        else:
            print('Invalid args. See `help list`')


    def list_objs(resp):
        if resp.get('Contents'):
            for obj in resp['Contents']:
                print(obj['Key'])
        else:
            print('None')


    def cmd_select(self, argv):

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


    def cmd_dir(self, argv):
        """Returns currently selected dir or None."""
        return self.selected_dir


    def cmd_upload(self, argv):

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


    def cmd_delete(self, argv):
        pass

    def cmd_download(self, argv):
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

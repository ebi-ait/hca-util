#!/usr/bin/python

import os
import sys
import boto3
from botocore.exceptions import ClientError, ProfileNotFound
import json
import subprocess
from multiprocessing.dummy import Pool

from hca_util.common import *
from hca_util.upload_progress import UploadProgress
from hca_util.aws import *


class HcaUtil:
    # use creds from [hca-hca_util] section of ~/.aws/credentials
    # and config from [profile hca-hca_util] section of ~/.aws/config
    profile_name = 'hca-hca_util'
    secret_name = 'hca/hca_util/secret'

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
            self.session = boto3.Session(profile_name=self.profile_name)
            profile_found = True
            # use profile to create clients for aws services: s3, secret_mgr, sts
            self.aws = Aws(self.session)
            # get bucket name from aws secrets (also serve as a way to validate user config/creds)
            self.bucket_name = self.aws.secret_mgr_get_bucket_name(self.secret_name)
            if self.bucket_name:
                self.setup_ok = True
        except ProfileNotFound:
            print(f'Setup failed: \n`{self.profile_name}` profile not found. ' + str(e))
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

        if len(argv) > 1:
            print('Invalid args. See `help create`')
            return

        # generate randon uuid prefix for directory name
        dir_name = gen_uuid()

        if len(argv) == 0:
            print('Project name: <none specified>')
        elif len(argv) == 1:
            project_name = argv[0]
            print('Project name: ' + project_name)
            if is_valid_project_name(project_name):
                print('(Valid)')
                dir_name += f'-{project_name}'
            else:
                print('(Invalid) Ignoring')

        try:
            self.aws.s3.put_object(Bucket=self.bucket_name, Key=(dir_name + '/'))
            print('Created ' + dir_name)
        except Exception as e:
            print('Error occurred creating directory: ' + str(e))

    def cmd_list(self, argv):
        if not self.setup_ok:
            print(f'Setup failed: \nSee `help config` for help to configure your credentials')
            return

        if len(argv) == 0 or len(argv) == 1:

            try:
                if len(argv) == 0:
                    resp = self.aws.s3.list_objects_v2(Bucket=self.bucket_name)
                    list_objs(resp)
                else:
                    dir_name = argv[0]
                    if is_valid_dir_name(dir_name):
                        resp = self.aws.s3.list_objects_v2(Bucket=self.bucket_name, Prefix=dir_name+'/')
                        list_objs(resp)
                    else:
                        print('Invalid directory name')
            except Exception as e:
                print('Error occurred listing directory: ' + str(e))

        else:
            print('Invalid args. See `help list`')

    def cmd_select(self, argv):
        if not self.setup_ok:
            print(f'Setup failed: \nSee `help config` for help to configure your credentials')
            return

        if len(argv) == 1:
            dir_name = argv[0]
            if is_valid_dir_name(dir_name):

                try:
                    s3_resource = self.aws.session.resource('s3')
                    bucket = s3_resource.Bucket(self.bucket_name)
                    bucket.Object(dir_name + '/')
                    #serialize(select_dir, dir_name)
                    self.selected_dir = dir_name
                    print('Selected ' + dir_name)

                except ClientError:
                    print('Directory not found')
            else:
                print('Invalid directory name')

        else:
            print('Invalid args. See `help select`')

    def cmd_dir(self, argv):
        """Returns currently selected dir or None."""
        print(self.selected_dir)

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
                    fs = [f for f in os.listdir('.') if os.path.isfile(f)]
                else:
                    # upload specified list of files
                    fs = [f for f in argv if os.path.exists(f)]

                print('Uploading...')

                try:
                    with Pool(12) as p:
                        p.map(lambda f: self.upload(f), fs)
                        print('Done.')

                except ClientError as e:
                    print('Error occurred during upload: ' + str(e))

        else:
            print('Invalid args. See `help upload`')

    """
    It is recommended to create a resource instance for each thread / process in a multithreaded or 
    multiprocess application rather than sharing a single instance among the threads / processes
    """
    def upload(self, f):
        # upload_file automatically handles multipart uploads via the S3 Transfer Manager
        # put_object maps to the low-level S3 API request, it does not handle multipart uploads
        self.aws.session.resource('s3').Bucket(self.bucket_name)\
                .upload_file(Filename=f, Key=self.selected_dir + '/' + os.path.basename(f),
                             Callback=UploadProgress(f))

    def cmd_delete(self, argv):
        if not self.setup_ok:
            print(f'Setup failed: \nSee `help config` for help to configure your credentials')
            return

        if self.selected_dir is None:
            print('No directory selected')
            return

        if len(argv) < 1:
            print('Invalid args. See `help delete`')
            return

        prefix = self.selected_dir+'/'
        s3_resource = self.aws.session.resource('s3')
        bucket = s3_resource.Bucket(self.bucket_name)
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
                try:
                    print('Deleting ' + prefix + f)
                    obj = bucket.Object(prefix + f)
                    obj.delete()
                except Exception as e:
                    print('Error deleting ' + prefix + f + ': ' + str(e))

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

        prefix = self.selected_dir+'/'
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
                try:
                    print('Downloading ' + prefix + f)
                    obj = bucket.Object(prefix + f)
                    if not os.path.exists(os.path.dirname(obj.key)):
                        os.makedirs(os.path.dirname(obj.key))
                    obj.download_file(obj.key)
                except Exception as e:
                    print('Error downloading ' + prefix + f + ': ' + str(e))


def list_objs(resp):
    if resp.get('Contents'):
        for obj in resp['Contents']:
            print(obj['Key'])
    else:
        print('None')

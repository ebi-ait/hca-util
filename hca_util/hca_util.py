#!/usr/bin/python

import os
from multiprocessing.dummy import Pool

import boto3
from botocore.exceptions import ClientError

from hca_util.aws import *
from hca_util.bucket_policies import *
from hca_util.common import *
from hca_util.upload_progress import UploadProgress


class HcaUtil:

    # steps to perform before executing command
    # 1. check user profile
    user_profile = None
    # 2. create an aws_client, get caller identity to check creds valid and if is_contributor
    aws_client = None


    session = None
    aws = None
    bucket_name = None
    setup_ok = False

    selected_dir = None

    # default constructor
    def __init__(self, profile, region):
        self.profile = profile
        self.region = region
        self.setup()

    # setup function
    def setup(self):
        try:
            # try to set a session using profile_name
            if not Aws.profile_exists(self.profile):
                print(f'Profile \'{self.profile}\' not found')
            else:
                profile_dict = Aws.get_profile(self.profile)
                self.session = boto3.Session(region_name=profile_dict['region'],
                                             aws_access_key_id=profile_dict['access_key'],
                                             aws_secret_access_key=profile_dict['secret_key'])

                # use profile to create clients/resources for aws services: s3, secret_mgr, sts
                self.aws = Aws(self.session)

                # get bucket name from aws secrets (also serve as a way to validate user config/creds)
                try:
                    # access policy can't be attached to a secret
                    # GetSecretValue action should be allowed for user
                    resp = self.aws.secret_mgr.get_secret_value(SecretId=Aws.SECRET_NAME)
                    secret_str = resp['SecretString']
                    self.bucket_name = json.loads(secret_str)['s3-bucket']
                except:
                    print(f'Invalid credentials')

                if self.bucket_name:
                    self.setup_ok = True
        except Exception as e:
            print(f'An exception of type {e.__class__.__name__} occurred in setup.\nDetail: ' + str(e))

        if not self.setup_ok:
            print('See `help config` for help to configure your credentials')

    # can't proceed with most common if setup nok
    # except: config, dir

    # command functions












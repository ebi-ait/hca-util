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
    def cmd_config(self, argv):
        """
        we may not have a session yet, if setup() wasn't successful.
        or we may have.
        In any case, we have to call setup() again after we have new config/creds.
        :param argv:
        :return:
        """

        if len(argv) == 2:
            access_key = argv[0]
            secret_key = argv[1]
            try:
                Aws.set_profile(self.profile, self.region, access_key, secret_key)
                self.setup()

            except Exception as e:
                print(f'An exception of type {e.__class__.__name__} occurred in cmd config.\nDetail: ' + str(e))
        else:
            print('Invalid args. See `help config`')

    def cmd_create(self, argv):
        if not self.setup_ok:
            print(f'Setup failed: \nSee `help config` for help to configure your credentials')
            return

        if len(argv) > 2:
            print('Invalid args. See `help create`')
            return

        # generate random uuid prefix for directory name
        dir_name = gen_uuid()

        # valid input
        # 1. create
        # 2. create [-udx]
        # 3. create [project_name]
        # 4. create [project_name] [-udx]

        def verify_perms(permissions):
            is_valid_perms = permissions in allowed_perms_combinations
            if not is_valid_perms:
                permissions = default_perms
                print('Invalid perms, using default')
            print(f'Perms <{permissions}>')
            return permissions

        def verify_projname(proj_name):
            is_valid_projname = is_valid_project_name(proj_name)
            if not is_valid_projname:
                proj_name = ''
                print('Invalid project name, ignoring')
            print(f'Project name <{proj_name}>')
            return proj_name

        perms = default_perms
        if len(argv) == 0:
            print(f'Project name <>')
            print(f'Default perms <{perms}>')
        elif len(argv) == 1 and argv[0].startswith('-'):
            print(f'Project name <>')
            perms = verify_perms(argv[0][1:])
        elif len(argv) == 1 and not argv[0].startswith('-'):
            project_name = verify_projname(argv[0])
            if project_name:
                dir_name += f'-{project_name}'
            print(f'Default perms <{perms}>')
        elif len(argv) == 2 and argv[1].startswith('-'):
            project_name = verify_projname(argv[0])
            if project_name:
                dir_name += f'-{project_name}'
            perms = verify_perms(argv[1][1:])
        else:
            print('Invalid args. See `help create`')
            return

        try:
            self.aws.s3.put_object(Bucket=self.bucket_name, Key=(dir_name + '/'))
            print('Created ' + dir_name)

            # get bucket policy
            s3_resource = self.session.resource('s3')
            try:
                bucket_policy = s3_resource.BucketPolicy(self.bucket_name)
                policy_str = bucket_policy.policy
            except ClientError:
                policy_str = ''

            if policy_str:
                policy_json = json.loads(policy_str)
            else:  # no bucket policy
                policy_json = json.loads('{ "Version": "2012-10-17", "Statement": [] }')

            # add new statement for dir to existing bucket policy
            new_statement = new_policy_statement(self.bucket_name, dir_name, perms)
            policy_json['Statement'].append(new_statement)

            updated_policy = json.dumps(policy_json)

            bucket_policy.put(Policy=updated_policy)

        except Exception as e:
            print(f'An exception of type {e.__class__.__name__} occurred in cmd create.\nDetail: ' + str(e))

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
                        resp = self.aws.s3.list_objects_v2(Bucket=self.bucket_name, Prefix=dir_name + '/')
                        list_objs(resp)
                    else:
                        print('Invalid directory name')
            except Exception as e:
                print(f'An exception of type {e.__class__.__name__} occurred in cmd list.\nDetail: ' + str(e))

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
                    # serialize(select_dir, dir_name)
                    self.selected_dir = dir_name
                    print('Selected ' + dir_name)

                except Exception as e:
                    print(f'An exception of type {e.__class__.__name__} occurred in cmd select.\nDetail: ' + str(e))

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

                except Exception as e:
                    print(f'An exception of type {e.__class__.__name__} occurred in cmd upload.\nDetail: ' + str(e))

        else:
            print('Invalid args. See `help upload`')

    """
    It is recommended to create a resource instance for each thread / process in a multithreaded or 
    multiprocess application rather than sharing a single instance among the threads / processes
    """

    def upload(self, f):
        # upload_file automatically handles multipart uploads via the S3 Transfer Manager
        # put_object maps to the low-level S3 API request, it does not handle multipart uploads
        self.aws.session.resource('s3').Bucket(self.bucket_name) \
            .upload_file(Filename=f, Key=self.selected_dir + '/' + os.path.basename(f),
                         Callback=UploadProgress(f))

    def cmd_delete(self, argv):
        if not self.setup_ok:
            print(f'Setup failed: \nSee `help config` for help to configure your credentials')
            return

        if self.selected_dir is None:
            print('No directory selected')
            return

        try:
            prefix = self.selected_dir + '/'
            s3_resource = self.aws.session.resource('s3')
            bucket = s3_resource.Bucket(self.bucket_name)

            if len(argv) == 0:
                # delete an entire directory
                confirm = input(f'Confirm delete directory {self.selected_dir} and its content? Y/y to proceed: ')
                if confirm == 'Y' or confirm == 'y':
                    print('Deleting...')

                    for obj in bucket.objects.filter(Prefix=prefix):
                        print('Deleting ' + obj.key)
                        obj.delete()

                    # reset selected dir
                    self.selected_dir = None
                    print('Selected dir: None')

                else:
                    print('Delete cancelled')

                return

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
                    print('Deleting ' + prefix + f)
                    obj = bucket.Object(prefix + f)
                    obj.delete()

        except Exception as e:
            print(f'An exception of type {e.__class__.__name__} occurred in cmd delete.\nDetail: ' + str(e))

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

        try:
            prefix = self.selected_dir + '/'
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
                    print('Downloading ' + prefix + f)
                    obj = bucket.Object(prefix + f)
                    if not os.path.exists(os.path.dirname(obj.key)):
                        os.makedirs(os.path.dirname(obj.key))
                    obj.download_file(obj.key)

        except Exception as e:
            print(f'An exception of type {e.__class__.__name__} occurred in cmd config.\nDetail: ' + str(e))


def list_objs(resp):
    if resp.get('Contents'):
        for obj in resp['Contents']:
            print(obj['Key'])
    else:
        print('None')

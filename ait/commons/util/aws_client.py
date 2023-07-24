import json

import boto3

from ait.commons.util.aws_cognito_authenticator import AwsCognitoAuthenticator
from ait.commons.util.settings import AWS_SECRET_NAME_AK_BUCKET, AWS_SECRET_NAME_SK_BUCKET, \
    AWS_SECRET_NAME_MORPHIC_BUCKET, COGNITO_MORPHIC_UTIL_ADMIN, S3_REGION


def static_bucket_name():
    return 'morphic-bio'


class Aws:

    def __init__(self, user_profile):
        self.is_user = False  # not admin
        self.user_dir_list = None
        self.center_name = None
        self.secret_key = None
        self.access_key = None
        self.user_profile = user_profile
        self.common_session = self.new_session()
        self.bucket_name = 'morphic-bio'

    def get_access_key(self, secret_mgr_client):
        resp = secret_mgr_client.get_secret_value(SecretId=AWS_SECRET_NAME_AK_BUCKET)
        secret_str = resp['SecretString']
        self.access_key = json.loads(secret_str)['AK-bucket']
        return self.access_key

    def get_secret_key(self, secret_mgr_client):
        resp = secret_mgr_client.get_secret_value(SecretId=AWS_SECRET_NAME_SK_BUCKET)
        secret_str = resp['SecretString']
        self.secret_key = json.loads(secret_str)['SK-bucket']
        return self.secret_key

    def get_bucket_name(self, secret_mgr_client):
        """
        Get bucket name from aws secrets
        :return:
        """
        # access policy can't be attached to a secret
        # GetSecretValue action should be allowed for user
        resp = secret_mgr_client.get_secret_value(SecretId=AWS_SECRET_NAME_MORPHIC_BUCKET)
        secret_str = resp['SecretString']
        self.bucket_name = json.loads(secret_str)['s3-bucket']
        return self.bucket_name

    def new_session(self):
        aws_cognito_authenticator = AwsCognitoAuthenticator(self)
        secret_manager_client = aws_cognito_authenticator.get_secret_manager_client(self.user_profile.username,
                                                                                    self.user_profile.password)

        if secret_manager_client is None:
            print('Failure while re-establishing Amazon Web Services session, report this error to the DRACC admin')
            raise Exception
        else:
            self.is_user = aws_cognito_authenticator.is_valid_user()
            self.user_dir_list = aws_cognito_authenticator.get_user_dir_list()
            self.center_name = aws_cognito_authenticator.get_center_name()

            return boto3.Session(region_name=S3_REGION,
                                 aws_access_key_id=self.get_access_key(secret_manager_client),
                                 aws_secret_access_key=self.get_secret_key(secret_manager_client))

    def is_valid_credentials(self):
        """
        Validate user config/credentials by making a get_caller_identity aws api call
        :return:
        """
        sts = self.common_session.client('sts')

        try:
            resp = sts.get_caller_identity()
            arn = resp.get('Arn')
            if arn.endswith(COGNITO_MORPHIC_UTIL_ADMIN):
                return True
        except Exception as e:
            if e is not KeyboardInterrupt:
                return False
            else:
                raise e

    def is_valid_user(self):
        return self.is_user

    def obj_exists(self, key):
        """
        return true if key exists, else false
        A folder/directory is an s3 object with key <uuid>/
        Note: s3://my-bucket/folder != s3://my-bucket/folder/
        Refer to https://www.peterbe.com/plog/fastest-way-to-find-out-if-a-file-exists-in-s3
        for comparison between client.list_objects_v2 and client.head_object to make this check.
        Also check https://stackoverflow.com/questions/33842944/check-if-a-key-exists-in-a-bucket-in-s3-using-boto3
        which suggests using Object.load() - which does a HEAD request, however, user doesn't have
        s3:GetObject permission by default, so this will fail for them.
        """
        response = self.new_session().client('s3').list_objects_v2(
            Bucket=self.bucket_name,
            Prefix=key,
        )
        for obj in response.get('Contents', []):
            if obj['Key'] == key:
                return True
        return False

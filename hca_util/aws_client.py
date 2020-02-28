import boto3
import json
from hca_util.settings import AWS_SECRET_NAME, IAM_USER_CONTRIBUTOR


class Aws:

    def __init__(self, user_profile):
        self.user_profile = user_profile
        self.common_session = self.new_session()
        self.is_contributor = False
        self.bucket_name = None

    def new_session(self):
        return boto3.Session(region_name=self.user_profile.region,
                             aws_access_key_id=self.user_profile.access_key,
                             aws_secret_access_key=self.user_profile.secret_key)

    def is_valid_credentials(self):
        """
        Validate user config/credentials by making a get_caller_identity aws api call
        :return:
        """
        sts = self.common_session.client('sts')

        try:
            resp = sts.get_caller_identity()
            arn = resp.get('Arn')
            if arn.endswith(f'user/{IAM_USER_CONTRIBUTOR}'):
                self.is_contributor = True
            return True
        except:
            return False

    def get_bucket_name(self):
        """
        Get bucket name from aws secrets
        :return:
        """
        # access policy can't be attached to a secret
        # GetSecretValue action should be allowed for user
        secret_mgr = self.common_session.client('secretsmanager')

        resp = secret_mgr.get_secret_value(SecretId=AWS_SECRET_NAME)
        secret_str = resp['SecretString']
        self.bucket_name = json.loads(secret_str)['s3-bucket']
        return self.bucket_name

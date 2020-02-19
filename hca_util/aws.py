import configparser
from pathlib import Path
import json


class Aws:
    HOME = str(Path.home())
    CONFIG_FILE = HOME + '/.aws/config'
    CREDENTIALS_FILE = HOME + '/.aws/credentials'

    # default profile use creds from [DEFAULT_PROFILE] section of ~/.aws/credentials
    # and config from [profile DEFAULT_PROFILE] section of ~/.aws/config
    DEFAULT_PROFILE = 'hca-util'
    DEFAULT_REGION = 'us-east-1'
    SECRET_NAME = 'hca/util/secret'

    def __init__(self, session):
        self.session = session
        self.s3 = session.client('s3')
        self.secret_mgr = session.client('secretsmanager')
        self.sts = session.client('sts')

    # you can't attach an access policy to a secret
    # allow GetSecretValue for the hca-contributor group
    # handle the exception in calling func
    def secret_mgr_get_bucket_name(self, secret_name):
        resp = self.secret_mgr.get_secret_value(SecretId=secret_name)
        secret_str = resp['SecretString']
        return json.loads(secret_str)['s3-bucket']

    def sts_get_caller_arn(self):
        try:
            resp = self.sts.get_caller_identity()
            arn = resp.get('Arn')
            return arn
        except Exception as e:
            print_exit(e)

    @staticmethod
    def print_exit(e):
        print(str(e))
        sys.exit(1)

    def configure(self, profile_name, access_key, secret_key):
        home = str(Path.home())
        aws_config_file = home + '/.aws/config'
        aws_credentials_file = home + '/.aws/credentials'

        """.aws/config
        [profile {profile_name}]
        region = us-east-1
        """

        # set comment_prefixes to a string which you will not use in the config file
        config = configparser.ConfigParser(comment_prefixes='/', allow_no_value=True)
        config.read(aws_config_file)

        if not config.has_section(f'profile {profile_name}'):
            config.add_section(f'profile {profile_name}')
        config.set(f'profile {profile_name}', 'region', 'us-east-1')

        with open(aws_config_file, 'w') as out:
            config.write(out)

        """.aws/credentials
        [{profile_name}]
        aws_access_key_id = {0}
        aws_secret_access_key = {1}
        """

        credentials = configparser.ConfigParser(comment_prefixes='/', allow_no_value=True)
        credentials.read(aws_credentials_file)

        if not credentials.has_section(f'{profile_name}'):
            credentials.add_section(f'{profile_name}')
        credentials.set(f'{profile_name}', 'aws_access_key_id', access_key)
        credentials.set(f'{profile_name}', 'aws_secret_access_key', secret_key)

        with open(aws_credentials_file, 'w') as out:
            credentials.write(out)

        print('Credentials saved.')

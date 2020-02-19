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

    def sts_get_caller_arn(self):
        try:
            resp = self.sts.get_caller_identity()
            arn = resp.get('Arn')
            return arn
        except Exception as e:
            print(str(e))
            sys.exit(1)

    @staticmethod
    def profile_exists(profile):
        # let's not bother checking CONFIG_FILE to see if region is set
        # we can always use default region
        credentials = configparser.ConfigParser(comment_prefixes='/', allow_no_value=True)
        credentials.read(Aws.CREDENTIALS_FILE)

        if credentials.has_section(profile):
            return True

        return False

    @staticmethod
    def get_profile(profile):
        credentials = configparser.ConfigParser()
        credentials.read(Aws.CREDENTIALS_FILE)

        profile_dict = {'access_key': '',
                        'secret_key': '',
                        'region': ''}

        if credentials.has_section(profile):
            profile_dict['access_key'] = credentials[profile].get('aws_access_key_id')
            profile_dict['secret_key'] = credentials[profile].get('aws_secret_access_key')

        config = configparser.ConfigParser()
        config.read(Aws.CONFIG_FILE)

        if config.has_section(f'profile {profile}'):
            profile_dict['region'] = config[f'profile {profile}'].get('region')

        if not profile_dict['region']:
            profile_dict['region'] = Aws.DEFAULT_REGION

        return profile_dict

    @staticmethod
    def set_profile(profile, region, access_key, secret_key):

        """.aws/config
        [profile {profile}]
        region = {region}
        """

        # set comment_prefixes to a string which you will not use in the config file
        config = configparser.ConfigParser(comment_prefixes='/', allow_no_value=True)
        config.read(Aws.CONFIG_FILE)

        if not config.has_section(f'profile {profile}'):
            config.add_section(f'profile {profile}')
        config.set(f'profile {profile}', 'region', region)

        with open(Aws.CONFIG_FILE, 'w') as out:
            config.write(out)

        """.aws/credentials
        [{profile}]
        aws_access_key_id = {0}
        aws_secret_access_key = {1}
        """

        credentials = configparser.ConfigParser(comment_prefixes='/', allow_no_value=True)
        credentials.read(Aws.CREDENTIALS_FILE)

        if not credentials.has_section(f'{profile}'):
            credentials.add_section(f'{profile}')
        credentials.set(f'{profile}', 'aws_access_key_id', access_key)
        credentials.set(f'{profile}', 'aws_secret_access_key', secret_key)

        with open(Aws.CREDENTIALS_FILE, 'w') as out:
            credentials.write(out)

        print('Credentials saved.')

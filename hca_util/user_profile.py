import os
import configparser
from pathlib import Path

HOME = str(Path.home())
CONFIG_FILE = HOME + '/.aws/config'
CREDENTIALS_FILE = HOME + '/.aws/credentials'

# default profile use creds from [DEFAULT_PROFILE] section of ~/.aws/credentials
# and config from [profile DEFAULT_PROFILE] section of ~/.aws/config
DEFAULT_PROFILE = 'hca-util'
DEFAULT_REGION = 'us-east-1'


def profile_exists(profile):
    # let's not bother checking CONFIG_FILE to see if region is set
    # we can always use default region
    credentials = configparser.ConfigParser(comment_prefixes='/', allow_no_value=True)
    credentials.read(CREDENTIALS_FILE)

    if credentials.has_section(profile):
        return True

    return False


def get_profile(profile):
    credentials = configparser.ConfigParser()
    credentials.read(CREDENTIALS_FILE)

    profile_dict = {'access_key': '',
                    'secret_key': '',
                    'region': ''}

    if credentials.has_section(profile):
        profile_dict['access_key'] = credentials[profile].get('aws_access_key_id')
        profile_dict['secret_key'] = credentials[profile].get('aws_secret_access_key')

    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)

    if config.has_section(f'profile {profile}'):
        profile_dict['region'] = config[f'profile {profile}'].get('region')

    if not profile_dict['region']:
        profile_dict['region'] = DEFAULT_REGION

    return profile_dict


def create_if_not_exists(file):
    """
    Create the file if it does not exist
    :param file:
    :return:
    """
    if not os.path.exists(file):
        open(file, 'w').close()


def set_profile(profile, region, access_key, secret_key):
    """.aws/config
    [profile {profile}]
    region = {region}
    """

    create_if_not_exists(CONFIG_FILE)

    # set comment_prefixes to a string which you will not use in the config file
    config = configparser.ConfigParser(comment_prefixes='/', allow_no_value=True)
    config.read(CONFIG_FILE)

    if not config.has_section(f'profile {profile}'):
        config.add_section(f'profile {profile}')
    config.set(f'profile {profile}', 'region', region)

    with open(CONFIG_FILE, 'w') as out:
        config.write(out)

    """.aws/credentials
    [{profile}]
    aws_access_key_id = {0}
    aws_secret_access_key = {1}
    """

    create_if_not_exists(CREDENTIALS_FILE)

    credentials = configparser.ConfigParser(comment_prefixes='/', allow_no_value=True)
    credentials.read(CREDENTIALS_FILE)

    if not credentials.has_section(f'{profile}'):
        credentials.add_section(f'{profile}')
    credentials.set(f'{profile}', 'aws_access_key_id', access_key)
    credentials.set(f'{profile}', 'aws_secret_access_key', secret_key)

    with open(CREDENTIALS_FILE, 'w') as out:
        credentials.write(out)

    print('Credentials saved.')

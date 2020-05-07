import os
import configparser
from ait.commons.util.common import create_if_not_exists
from ait.commons.util.settings import AWS_CONFIG_FILE, AWS_CREDENTIALS_FILE, DEFAULT_REGION


class UserProfile:
    def __init__(self):
        self.access_key = None
        self.secret_key = None
        self.region = None

    def __repr__(self):
        return 'UserProfile()'

    def __str__(self):
        return f'UserProfile (access_key={self.access_key}, secret_key={self.secret_key}, region={self.region})'


def profile_exists(profile):
    # let's not bother checking CONFIG_FILE to see if region is set
    # we can always use default region
    if not os.path.exists(AWS_CREDENTIALS_FILE):
        return False

    credentials = configparser.ConfigParser(comment_prefixes='/', allow_no_value=True)
    credentials.read(AWS_CREDENTIALS_FILE)

    if credentials.has_section(profile):
        return True

    return False


def get_profile(profile):
    credentials = configparser.ConfigParser()
    credentials.read(AWS_CREDENTIALS_FILE)

    user_profile = UserProfile()

    if credentials.has_section(profile):
        user_profile.access_key = credentials[profile].get('aws_access_key_id')
        user_profile.secret_key = credentials[profile].get('aws_secret_access_key')

    config = configparser.ConfigParser()
    config.read(AWS_CONFIG_FILE)

    if config.has_section(f'profile {profile}'):
        user_profile.region = config[f'profile {profile}'].get('region')

    if not user_profile.region:
        user_profile.region = DEFAULT_REGION

    return user_profile


def set_profile(profile, region, access_key, secret_key):
    """.aws/config
    [profile {profile}]
    region = {region}
    """

    create_if_not_exists(AWS_CONFIG_FILE)

    # set comment_prefixes to a string which you will not use in the config file
    config = configparser.ConfigParser(comment_prefixes='/', allow_no_value=True)
    config.read(AWS_CONFIG_FILE)

    if not config.has_section(f'profile {profile}'):
        config.add_section(f'profile {profile}')
    config.set(f'profile {profile}', 'region', region)

    with open(AWS_CONFIG_FILE, 'w') as out:
        config.write(out)

    """.aws/credentials
    [{profile}]
    aws_access_key_id = {0}
    aws_secret_access_key = {1}
    """

    create_if_not_exists(AWS_CREDENTIALS_FILE)

    credentials = configparser.ConfigParser(comment_prefixes='/', allow_no_value=True)
    credentials.read(AWS_CREDENTIALS_FILE)

    if not credentials.has_section(f'{profile}'):
        credentials.add_section(f'{profile}')
    credentials.set(f'{profile}', 'aws_access_key_id', access_key)
    credentials.set(f'{profile}', 'aws_secret_access_key', secret_key)

    with open(AWS_CREDENTIALS_FILE, 'w') as out:
        credentials.write(out)

    print('Credentials saved.')

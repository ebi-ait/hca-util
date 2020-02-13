import configparser
from pathlib import Path


def configure(access_key, secret_key):
    try:
        home = str(Path.home())
        aws_config_file = home + '/.aws/config'
        aws_credentials_file = home + '/.aws/credentials'

        """.aws/config
        [profile hca-util]
        region = us-east-1
        """

        # set comment_prefixes to a string which you will not use in the config file
        config = configparser.ConfigParser(comment_prefixes='/', allow_no_value=True)
        config.read(aws_config_file)

        if not config.has_section('profile hca-util'):
            config.add_section('profile hca-util')
        config.set('profile hca-util', 'region', 'us-east-1')

        with open(aws_config_file, 'w') as out:
            config.write(out)

        """.aws/credentials
        [hca-util]
        aws_access_key_id = {0}
        aws_secret_access_key = {1}
        """

        credentials = configparser.ConfigParser(comment_prefixes='/', allow_no_value=True)
        credentials.read(aws_credentials_file)

        if not credentials.has_section('hca-util'):
            credentials.add_section('hca-util')
        credentials.set('hca-util', 'aws_access_key_id', access_key)
        credentials.set('hca-util', 'aws_secret_access_key', secret_key)

        with open(aws_credentials_file, 'w') as out:
            credentials.write(out)

    except Exception as e:
        print(str(e))

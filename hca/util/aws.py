import configparser
from pathlib import Path


class Aws:

    def __init__(self, session):
        self.session = session
        self.s3 = session.client('s3')
        self.secret_mgr = session.client('secretsmanager')
        self.sts = session.client('sts')

    def s3_create_dir(self, bucket_name, dir_name):
        try:
            self.s3.put_object(Bucket=bucket_name, Key=(dir_name + '/'))
        except Exception as e:
            print_exit(e)

    # you can't attach an access policy to a secret
    # allow GetSecretValue for the hca-contributor group
    def secret_mgr_get_bucket_name(self, secret_name):
        try:
            resp = self.secret_mgr.get_secret_value(SecretId=secret_name)
            secret_str = resp['SecretString']
            return json.loads(secret_str)['s3-bucket']
        except Exception as e:
            # exit?? reconfig??
            print_exit(e)

    def sts_get_caller_arn(self):
        try:
            resp = self.sts.get_caller_identity()
            arn = resp.get('Arn')
            return arn
        except Exception as e:
            # exit?? reconfig??
            print_exit(e)

    @staticmethod
    def print_exit(e):
        print(str(e))
        sys.exit(1)

    @staticmethod
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
            sys.exit(1)

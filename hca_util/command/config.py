from hca_util.user_profile import set_profile, profile_exists, get_profile, DEFAULT_PROFILE, DEFAULT_REGION
from hca_util.aws_client import Aws


class CmdConfig:

    def __init__(self, access_key, secret_key):
        self.access_key = access_key
        self.secret_key = secret_key

    def run(self):

        try:
            set_profile(DEFAULT_PROFILE, DEFAULT_REGION, self.access_key, self.secret_key)

            # check new profile
            if profile_exists(DEFAULT_PROFILE):
                user_profile = get_profile(DEFAULT_PROFILE)
                aws = Aws(user_profile)

                if aws.is_valid_credentials():
                    print('Valid credentials')
                else:
                    print('Invalid credentials')
            else:
                print('Error setting profile')

        except Exception as e:
            print(f'An exception of type {e.__class__.__name__} occurred in cmd config.\nDetail: ' + str(e))

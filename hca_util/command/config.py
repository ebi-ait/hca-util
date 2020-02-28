from hca_util.user_profile import set_profile, profile_exists, get_profile
from hca_util.settings import DEFAULT_PROFILE, DEFAULT_REGION
from hca_util.aws_client import Aws
from hca_util.common import print_err


class CmdConfig:

    def __init__(self, args):
        self.args = args

    def run(self):

        try:
            set_profile(DEFAULT_PROFILE, DEFAULT_REGION, self.args.ACCESS_KEY, self.args.SECRET_KEY)

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
            print_err(e, 'config')

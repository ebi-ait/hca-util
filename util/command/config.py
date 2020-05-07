from util.aws_client import Aws
from util.common import format_err
from util.local_state import set_bucket
from settings import DEFAULT_PROFILE, DEFAULT_REGION
from util.user_profile import set_profile, profile_exists, get_profile


class CmdConfig:
    """
    both admin and user
    aws resource or client used in command - sts (to check valid credentials).
    """

    def __init__(self, args):
        self.args = args

    def run(self):

        try:
            profile = self.args.profile if self.args.profile else DEFAULT_PROFILE
            if self.args.bucket:
                set_bucket(self.args.bucket)

            if self.args.ACCESS_KEY and self.args.SECRET_KEY:  
                set_profile(profile, DEFAULT_REGION, self.args.ACCESS_KEY, self.args.SECRET_KEY)

            # check new profile
            if profile_exists(profile):
                user_profile = get_profile(profile)
                aws = Aws(user_profile)

                if aws.is_valid_credentials():
                    return True, 'Valid credentials' + ('' if aws.is_user else ' for admin use')
                else:
                    return False, 'Invalid credentials'
            else:
                return False, f'Profile \'{profile}\' not found. Please run config command with your access keys'

        except Exception as e:
            return False, format_err(e, 'config')

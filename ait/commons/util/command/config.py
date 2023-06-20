from ait.commons.util.aws_cognito_authenticator import AwsCognitoAuthenticator
from ait.commons.util.common import format_err
from ait.commons.util.local_state import set_bucket
from ait.commons.util.settings import DEFAULT_PROFILE


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

            if self.args.USERNAME and self.args.PASSWORD:
                aws_cognito_authenticator = AwsCognitoAuthenticator(self)

                valid_user = aws_cognito_authenticator.validate_cognito_identity(profile, self.args.USERNAME,
                                                                                 self.args.PASSWORD)

                # check if valid user
                if valid_user:
                    return True, 'Valid credentials'
                else:
                    return False, 'Invalid credentials'
        except Exception as e:
            return False, format_err(e, 'config')

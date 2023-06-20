import sys

import boto3

from ait.commons.util.settings import DEFAULT_PROFILE, DEFAULT_REGION
from ait.commons.util.user_profile import set_profile


class AwsCognitoAuthenticator:
    """
    both admin and user
    """

    def __init__(self, args):
        self.args = args
        self.is_user = False  # not admin
        self.user_dir_list = None
        self.center_name = None  # custom attribute DPC

    def validate_cognito_identity(self, profile, username, password):

        try:
            profile = profile if profile else DEFAULT_PROFILE

            if username and password:
                client = boto3.client("cognito-idp", region_name="eu-west-2", aws_access_key_id="NONE",
                                      aws_secret_access_key="NONE")

                response = client.initiate_auth(
                    ClientId="5ajn7j8kkbvoau0foonaah8tgp",
                    AuthFlow="USER_PASSWORD_AUTH",
                    AuthParameters={"USERNAME": username, "PASSWORD": password},
                )

                # Getting the user details.
                access_token = response["AuthenticationResult"]["AccessToken"]
                id_token = response["AuthenticationResult"]["IdToken"]

                response = client.get_user(AccessToken=access_token)
                username = response['Username']
                print('Current user is ' + username)

                if username.endswith('Admin') or username.endswith('admin'):
                    self.is_user = False
                else:
                    self.is_user = True

                identity = boto3.client('cognito-identity', region_name="eu-west-2")
                identity_id = identity.get_id(
                    IdentityPoolId='eu-west-2:c8ade43b-30c0-4315-a9cb-575c0377369e',
                    Logins={
                        'cognito-idp.eu-west-2.amazonaws.com/eu-west-2_uTVRCDMKG': id_token
                    }
                )['IdentityId']

                aws_cred = identity.get_credentials_for_identity(
                    IdentityId=identity_id,
                    Logins={
                        'cognito-idp.eu-west-2.amazonaws.com/eu-west-2_uTVRCDMKG': id_token
                    }
                )['Credentials']

                session_token = aws_cred['SessionToken']

                if session_token:
                    set_profile(profile, DEFAULT_REGION, aws_cred['AccessKeyId'], aws_cred['SecretKey'],
                                session_token, username, password)

                    return True
                else:
                    print('Un-authenticated user')
                    return False

        except Exception as e:
            return False

    def get_secret_manager_client(self, username, password):

        try:
            if username and password:
                client = boto3.client("cognito-idp", region_name="eu-west-2", aws_access_key_id="NONE",
                                      aws_secret_access_key="NONE")

                response = client.initiate_auth(
                    ClientId="5ajn7j8kkbvoau0foonaah8tgp",
                    AuthFlow="USER_PASSWORD_AUTH",
                    AuthParameters={"USERNAME": username, "PASSWORD": password},
                )

                # Getting the user details.
                access_token = response["AuthenticationResult"]["AccessToken"]
                id_token = response["AuthenticationResult"]["IdToken"]

                response = client.get_user(AccessToken=access_token)

                username = response['Username']
                print('Current user is ' + username)

                user_attribute_list = response['UserAttributes']

                if username.endswith('Admin') or username.endswith('admin'):
                    self.is_user = False
                else:
                    self.is_user = True

                for attr in user_attribute_list:
                    if attr['Name'] == 'custom:DPC':
                        self.center_name = attr['Value'].lower()

                    if attr['Name'] == 'custom:directory_access':
                        self.user_dir_list = attr['Value'].split(',')

                        if self.user_dir_list is not None:
                            self.user_dir_list = ['morphic-' + self.center_name + '/' + dataset_dir for dataset_dir in
                                                  self.user_dir_list]

                if self.is_user:
                    if self.center_name is None:
                        print('User does not have an assigned center name and therefore cannot perform any operations '
                              'with this system')
                        sys.exit(1)

                    if self.user_dir_list is None:
                        if self.is_user:
                            print('User does not have access to any upload areas or to perform any operations with this'
                                  'system')
                            sys.exit(1)

                identity = boto3.client('cognito-identity', region_name="eu-west-2")

                identity_id = identity.get_id(
                    IdentityPoolId='eu-west-2:c8ade43b-30c0-4315-a9cb-575c0377369e',
                    Logins={
                        'cognito-idp.eu-west-2.amazonaws.com/eu-west-2_uTVRCDMKG': id_token
                    }
                )['IdentityId']

                aws_cred = identity.get_credentials_for_identity(
                    IdentityId=identity_id,
                    Logins={
                        'cognito-idp.eu-west-2.amazonaws.com/eu-west-2_uTVRCDMKG': id_token
                    }
                )['Credentials']

                session_token = aws_cred['SessionToken']

                if session_token:
                    secret_mgr_client = boto3.client('secretsmanager', region_name="eu-west-2",
                                                     aws_access_key_id=aws_cred['AccessKeyId'],
                                                     aws_secret_access_key=aws_cred['SecretKey'],
                                                     aws_session_token=session_token)
                    return secret_mgr_client
                else:
                    print('Un-authenticated user')

                    return None

        except Exception as e:
            return None

    def is_valid_user(self):
        return self.is_user

    def get_user_dir_list(self):
        return self.user_dir_list

    def get_center_name(self):
        return self.center_name

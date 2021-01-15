import json

from botocore.exceptions import ClientError

from ait.commons.util.aws_client import Aws
from ait.commons.util.bucket_policy import DEFAULT_PERMS, allowDownloadStmt, denyDeleteStmt
from ait.commons.util.common import gen_uuid, format_err


class CmdCreate:
    """
    admin only
    aws resource or client used in command - s3 client (put_object), s3 resource (BucketPolicy)
    """

    def __init__(self, aws: Aws, args):
        self.aws = aws
        self.args = args

    def run(self):
        if not self.aws:
            return False, 'You need configure your profile first'

        if self.aws.is_user:
            return False, 'You don\'t have permission to use this command'

        area_name = self.args.NAME
        perms = self.args.p  # optional str, default 'ux'

        # generate random uuid prefix for area name
        area_id = gen_uuid()

        try:
            s3_client = self.aws.common_session.client('s3')
            # new upload areas to be created with tagging instead of metadata
            s3_client.put_object(Bucket=self.aws.bucket_name, Key=(area_id + '/'), Tagging=f'name={area_name}&perms={perms}')

            if perms == DEFAULT_PERMS:
                pass # default perms as set in user policy (ux) applies - no need for further actions (deny or allow)
            else:
                # get bucket policy
                bucket_policy = self.aws.common_session.resource('s3').BucketPolicy(self.aws.bucket_name)
                try:
                    policy_str = bucket_policy.policy
                except ClientError:
                    policy_str = ''

                if policy_str:
                    policy_json = json.loads(policy_str)
                else:  # no bucket policy
                    policy_json = json.loads('{ "Version": "2012-10-17", "Statement": [] }')

                allow_stmt = None
                deny_stmt = None

                for stmt in policy_json['Statement']:
                    if stmt['Sid'] == 'AllowDownload':
                        allow_stmt = stmt
                    elif stmt['Sid'] == 'DenyDelete':
                        deny_stmt = stmt
                
                if 'd' in perms: # e.g 'ud' or 'udx'
                    # allow download
                    self.update_perms(policy_json, allow_stmt, allowDownloadStmt(), area_id)

                if 'x' not in perms: # e.g. 'u' or 'ud'
                    # deny delete
                    self.update_perms(policy_json, deny_stmt, denyDeleteStmt(), area_id)

                try:
                    bucket_policy.put(Policy=json.dumps(policy_json))
                except ClientError:
                    pass

            return True, 'Created upload area with UUID ' + area_id + ' and name ' + area_name

        except Exception as e:
            return False, format_err(e, 'create')


    def update_perms(self, policy, stmt, template, area):
        if not stmt:
            stmt = template
            policy['Statement'].append(stmt)
        if isinstance(stmt['Resource'], str):
            stmt['Resource'] = [stmt['Resource']] + [f'arn:aws:s3:::{self.aws.bucket_name}/{area}/*']
        elif isinstance(stmt['Resource'], list):
            stmt['Resource'].append(f'arn:aws:s3:::{self.aws.bucket_name}/{area}/*')

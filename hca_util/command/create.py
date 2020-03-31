import json
from botocore.exceptions import ClientError
from hca_util.bucket_policy import new_policy_statement
from hca_util.common import gen_uuid
from hca_util.common import print_err


class CmdCreate:
    """
    admin only
    aws resource or client used in command - s3 client (put_object), s3 resource (BucketPolicy)
    """

    def __init__(self, aws, args):
        self.aws = aws
        self.args = args

    def run(self):

        if self.aws.is_user:
            return False, 'You don\'t have permission to use this command'

        area_name = self.args.NAME
        perms = self.args.p  # optional str, default 'ux'

        # generate random uuid prefix for area name
        area_id = gen_uuid()

        try:
            metadata = {'name': area_name, 'perms': perms}

            s3_client = self.aws.common_session.client('s3')
            s3_client.put_object(Bucket=self.aws.bucket_name, Key=(area_id + '/'), Metadata=metadata)

            # get bucket policy
            s3_resource = self.aws.common_session.resource('s3')
            try:
                bucket_policy = s3_resource.BucketPolicy(self.aws.bucket_name)
                policy_str = bucket_policy.policy
            except ClientError:
                policy_str = ''

            if policy_str:
                policy_json = json.loads(policy_str)
            else:  # no bucket policy
                policy_json = json.loads('{ "Version": "2012-10-17", "Statement": [] }')

            # add new statement for dir to existing bucket policy
            new_statement = new_policy_statement(self.aws.bucket_name, area_id, perms)
            policy_json['Statement'].append(new_statement)

            updated_policy = json.dumps(policy_json)

            bucket_policy.put(Policy=updated_policy)
            return True, 'Created upload area with UUID ' + area_id + ' and name ' + area_name

        except Exception as e:
            print_err(e, 'create')

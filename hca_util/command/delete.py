import json
from botocore.exceptions import ClientError
from hca_util.local_state import get_selected_dir
from hca_util.common import print_err
from hca_util.command.dir import CmdDir


class CmdDelete:
    """
    user: both wrangler and contributor, though contributor can't delete folder
    aws resource or client used in command - s3 resource (bucket.objects/ obj.delete)
    """

    def __init__(self, aws, args):
        self.aws = aws
        self.args = args

    def run(self):

        selected_dir = get_selected_dir()

        if not selected_dir:
            print('No directory selected')
            return

        try:
            s3_resource = self.aws.common_session.resource('s3')
            bucket = s3_resource.Bucket(self.aws.bucket_name)

            if self.args.d:  # delete dir
                if self.aws.is_contributor:
                    print('You don\'t have permission to use this command')
                    return

                confirm = input(f'Confirm delete {selected_dir}? Y/y to proceed: ')

                if confirm.lower() == 'y':
                    print('Deleting...')

                    for obj in bucket.objects.filter(Prefix=selected_dir):
                        print(obj.key)
                        obj.delete()

                    # delete bucket policy for HCAContributer-folder permissions
                    delete_dir_perms_from_bucket_policy(s3_resource, self.aws.bucket_name, selected_dir)

                    # clear selected dir
                    CmdDir.clear(False)
                return

            if self.args.a:  # delete all files
                print('Deleting...')
                for obj in bucket.objects.filter(Prefix=selected_dir):
                    # do not delete folder object
                    if obj.key == selected_dir:
                        continue
                    print(obj.key)
                    obj.delete()
                return

            if self.args.f:  # delete list of file(s)
                print('Deleting...')
                for f in self.args.f:
                    print('Deleting ' + selected_dir + f)
                    obj = bucket.Object(selected_dir + f)
                    obj.delete()
                return

        except Exception as e:
            print_err(e, 'delete')


def delete_dir_perms_from_bucket_policy(s3_res, bucket_name, dir_name):
    try:
        bucket_policy = s3_res.BucketPolicy(bucket_name)
        policy_str = bucket_policy.policy
    except ClientError:
        policy_str = ''

    if policy_str:
        policy_json = json.loads(policy_str)
        changed = False
        for stmt in policy_json['Statement']:
            if dir_name in stmt['Resource']:
                policy_json['Statement'].remove(stmt)
                changed = True
        if changed:
            updated_policy = json.dumps(policy_json)
            bucket_policy.put(Policy=updated_policy)

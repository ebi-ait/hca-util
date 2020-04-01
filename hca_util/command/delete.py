import json

from botocore.exceptions import ClientError

from hca_util.command.area import CmdArea
from hca_util.common import format_err
from hca_util.local_state import get_selected_area


class CmdDelete:
    """
    user: both wrangler and contributor, though contributor can't delete folder
    aws resource or client used in command - s3 resource (bucket.objects/ obj.delete)
    """

    def __init__(self, aws, args):
        self.aws = aws
        self.args = args

    def run(self):

        selected_area = get_selected_area()

        if not selected_area:
            return False, 'No area selected'

        try:
            s3_resource = self.aws.common_session.resource('s3')
            bucket = s3_resource.Bucket(self.aws.bucket_name)

            if self.args.d:  # delete area
                if self.aws.is_contributor:
                    return False, 'You don\'t have permission to use this command'

                confirm = input(f'Confirm delete {selected_area}? Y/y to proceed: ')

                if confirm.lower() == 'y':
                    print('Deleting...')

                    for obj in bucket.objects.filter(Prefix=selected_area):
                        print(obj.key)
                        obj.delete()

                    # delete bucket policy for HCAContributer-folder permissions
                    # only wrangler who has perms to set policy can do this
                    delete_dir_perms_from_bucket_policy(s3_resource, self.aws.bucket_name, selected_area)

                    # clear selected area
                    CmdArea.clear(False)
                return True, None

            if self.args.a:  # delete all files
                print('Deleting...')
                for obj in bucket.objects.filter(Prefix=selected_area):
                    # do not delete folder object
                    if obj.key == selected_area:
                        continue
                    print(obj.key)
                    obj.delete()
                return True, None

            if self.args.f:  # delete list of file(s)
                print('Deleting...')
                for f in self.args.f:
                    # you may have perm x but not d (to load or even do a head object)
                    # so use obj_exists

                    if self.aws.obj_exists(selected_area + f):

                        obj = s3_resource.ObjectSummary(self.aws.bucket_name, selected_area + f)
                        obj.delete()
                        return True, selected_area + f + '  Done.'
                    else:
                        return False, selected_area + f + '  File not found.'
                return

        except Exception as e:
            return False, format_err(e, 'delete')


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

import json

from botocore.exceptions import ClientError

from ait.commons.util.command.area import CmdArea
from ait.commons.util.common import format_err
from ait.commons.util.local_state import get_selected_area


class CmdDelete:
    """
    both admin and user, though user can't delete folder
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
            if self.args.d:  # delete area
                if self.aws.is_user:
                    return False, 'You don\'t have permission to use this command'

                confirm = input(f'Confirm delete upload area {selected_area}? Y/y to proceed: ')

                if confirm.lower() == 'y':
                    print('Deleting...')

                    deleted_keys = self.delete_upload_area(selected_area, incl_selected_area=True)
                    for k in deleted_keys:
                        print(k)

                    # delete bucket policy for user-folder permissions
                    # only admin who has perms to set policy can do this
                    self.clear_area_perms_from_bucket_policy(selected_area)

                    # clear selected area
                    CmdArea.clear(False)
                return True, None

            if self.args.a:  # delete all files
                
                confirm = input(f'Confirm delete all contents from {selected_area}? Y/y to proceed: ')
                
                if confirm.lower() == 'y':
                    print('Deleting...')

                    deleted_keys = self.delete_upload_area(selected_area, incl_selected_area=False)
                    for k in deleted_keys:
                        print(k)

                return True, None

            if self.args.PATH:  # list of files and dirs to delete
                print('Deleting...')
                for p in self.args.PATH:
                    # you may have perm x but not d (to load or even do a head object)
                    # so use obj_exists

                    prefix = selected_area + p
                    keys = self.all_keys(prefix)

                    if keys:
                        for k in keys:
                            self.delete_s3_object(k)
                            print(k + '  Done.')
                    else:
                        print(prefix + '  File not found.')
                return True, None
            else:
                return False, 'No path specified'

        except Exception as e:
            return False, format_err(e, 'delete')

    # based on obj_exists method
    def all_keys(self, prefix):
        keys = []
        response = self.aws.common_session.client('s3').list_objects_v2(
            Bucket=self.aws.bucket_name,
            Prefix=prefix,
        )
        for obj in response.get('Contents', []):
            keys.append(obj['Key'])
            
        return keys

    def delete_s3_object(self, key):
        s3_resource = self.aws.common_session.resource('s3')
        s3_obj = s3_resource.ObjectSummary(self.aws.bucket_name, key)
        s3_obj.delete()
        return key

    def delete_upload_area(self, selected_area, incl_selected_area=False):
        s3_resource = self.aws.common_session.resource('s3')
        bucket = s3_resource.Bucket(self.aws.bucket_name)
        deleted_keys = []
        objs_to_delete = bucket.objects.filter(Prefix=selected_area) if incl_selected_area else filter(lambda obj: obj.key != selected_area, bucket.objects.filter(Prefix=selected_area))
        for obj in objs_to_delete:
            obj.delete()
            deleted_keys.append(obj.key)

        return deleted_keys

    def clear_area_perms_from_bucket_policy(self, selected_area):
        s3_resource = self.aws.common_session.resource('s3')
        return CmdDelete.delete_dir_perms_from_bucket_policy(s3_resource, self.aws.bucket_name, selected_area)

    @staticmethod
    def delete_dir_perms_from_bucket_policy(s3_res, bucket_name, area_name):
        bucket_policy = s3_res.BucketPolicy(bucket_name)
        try:
            policy_str = bucket_policy.policy # throws NoSuchBucketPolicy
        except ClientError:
            policy_str = ''

        if policy_str:
            policy_json = json.loads(policy_str)
            
            for stmt in policy_json['Statement']:
                stmt_Resource = stmt['Resource']

                if isinstance(stmt_Resource, str):

                    if area_name in stmt['Resource']:
                        # remove statement affecting single resource
                        policy_json['Statement'].remove(stmt)
                        try:
                            bucket_policy.put(Policy=json.dumps(policy_json))  # throws MalformedPolicy (policy document exceeds the maximum allowed size of 20480 bytes)
                        except ClientError:
                            pass

                elif isinstance(stmt_Resource, list):

                    for res in stmt_Resource:
                        if area_name in res:
                            # remove resource from statement
                            policy_json['Statement']['Resource'].remove(res)
                            try:
                                bucket_policy.put(Policy=json.dumps(policy_json))
                            except ClientError:
                                pass


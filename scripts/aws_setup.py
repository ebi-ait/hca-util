# Script to setup AWS resources to use hca-util
# It does the following:
# create 2 iam users - user, admin
# create corresponding groups for users
# assign default policies to groups

# TODO: complete this script
# TODO: cleanup script to release resources when tool is taken down
# TODO: s3 setup details

import boto3

def setup():
    pass

def teardown():
    pass

BUCKET_NAME = ''


# create_bucket
# attach default policy

iam_client = boto3.client('iam')

IAM_USER = 'TestUser'
IAM_ADMIN = 'TestAdmin'

# create_user
user = iam_client.create_user(UserName=IAM_USER)
admin = iam_client.create_user(UserName=IAM_ADMIN)

# create_group
user_grp = iam_client.create_group(GroupName=IAM_USER.lower() + '-grp')
admin_grp = iam_client.create_group(GroupName=IAM_ADMIN.lower() + '-grp')

#add_user_to_group()
#attach_group_policy()



# cleanup
delete_user
delete_group
delete_group_policy
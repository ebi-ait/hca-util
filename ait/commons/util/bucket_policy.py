from ait.commons.util.settings import AWS_ACCOUNT, IAM_USER

"""
Upload area permissions
Abbrev  Desc.       S3 action           S3 operation/API request
                    (object ops perms)
u       upload      s3:PutObject        # PUT Object, POST Object, Initiate Multipart Upload, Upload Part, Complete Multipart Upload, PUT Object - Copy
d       download    s3:GetObject        # GET Object, HEAD Object, SELECT Object Content
x       delete      s3:DeleteObject     # DELETE Object

Possible combinations are 'u', 'ud', 'ux', 'udx'

Default permissions on new upload area is 'ux'

User groups:
admin           (at the moment) full s3 access
(normal) user   default: ListBucket except top/root level dir, plus per upload area perms (one of above combination), plus s3:GetObjectTagging
"""

ALLOWED_PERMS = ['u', 'ud', 'ux', 'udx']
DEFAULT_PERMS = 'ux'

s3_permissions = {'u': 's3:PutObject',
                  'd': 's3:GetObject',
                  'x': 's3:DeleteObject'}


def user_policy_statement_template():
    return {
        'Action': [],
        'Effect': 'Allow',
        'Resource': 'arn:aws:s3:::BUCKET_NAME/AREA_NAME/*',
        'Principal': {
            'AWS': [
                f'arn:aws:iam::{AWS_ACCOUNT}:user/{IAM_USER}'
            ]
        }
    }.copy()


def new_policy_statement(bucket, area, perms=None):
    statement = user_policy_statement_template()
    # add permissions/actions
    if perms is None or perms not in ALLOWED_PERMS:
        perms = DEFAULT_PERMS
    for p in perms:
        statement['Action'].append(s3_permissions.get(p))
    # additional action needed for user to see tagging (area name and perms)
    statement['Action'].append("s3:GetObjectTagging")
    res = statement['Resource']
    statement['Resource'] = res.replace('BUCKET_NAME', bucket).replace('AREA_NAME', area)
    return statement

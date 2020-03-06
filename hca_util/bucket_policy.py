"""
Permissions include
u for upload
d for download
x for delete
Possible combinations are 'u', 'ud', 'ux', 'udx'
default permissions on new directory is 'ux'

"""
ALLOWED_PERMS = ['u', 'ud', 'ux', 'udx']
DEFAULT_PERMS = 'ux'

# user groups:
# hca-wrangler     s3 full access
# hca-contributor  hca-util bucket (ListBucket except top-level/root directory)

# Permissions for Object operations
#                       permissions        s3 operations
s3_permissions = {'u': 's3:PutObject',     # PUT Object, POST Object, Initiate Multipart Upload, Upload Part, Complete Multipart Upload, PUT Object - Copy
                  'd': 's3:GetObject',     # GET Object, HEAD Object, SELECT Object Content
                  'x': 's3:DeleteObject'}  # DELETE Object


def get_policy_statement_template():
    return {
        'Action': [],
        'Effect': 'Allow',
        'Resource': 'arn:aws:s3:::BUCKET_NAME/DIR_NAME/*',
        'Principal': {
            'AWS': [
                'arn:aws:iam::871979166454:user/HCAContributor'
            ]
        }
    }.copy()


def new_policy_statement(bucket, dir, perms=None):
    statement = get_policy_statement_template()
    # add permissions/actions
    if perms is None or perms not in ALLOWED_PERMS:
        perms = DEFAULT_PERMS
    for p in perms:
        statement['Action'].append(s3_permissions.get(p))
        res = statement['Resource']
        statement['Resource'] = res.replace('BUCKET_NAME', bucket).replace('DIR_NAME', dir)
    return statement

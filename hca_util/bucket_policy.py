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

s3_permissions = {'u': 's3:PutObject',
                  'd': 's3:GetObject',
                  'x': 's3:DeleteObject'}


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

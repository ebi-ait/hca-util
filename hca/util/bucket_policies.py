# default = ux

# u - upload
# d - download
# x - delete

allowed_perms_combinations = ['u', 'ud', 'ux', 'udx']

s3_permissions = {'u': 's3:PutObject',
                  'd': 's3:GetObject',
                  'x': 's3:DeleteObject'}


def get_bucket_policy(acc_id, user, perms, bucket, dir):
    return bucket_policy.replace('ACCOUNT_ID', acc_id) \
        .replace('USER', user) \
        .replace('ACTIONS', str(get_permissions(perms))) \
        .replace('BUCKET_NAME', bucket) \
        .replace('DIR_NAME', dir)


def get_permissions(ps):
    perms_list = []
    for p in ps:
        if s3_permissions.get(p):
            perms_list.append(s3_permissions.get(p))
    return perms_list


bucket_policy = """{
    'Version': '2012-10-17',
    'Statement': [{
        'Effect': 'Allow',
        'Principal': {"AWS": "arn:aws:iam::ACCOUNT_ID:USER"},
        'Action': ACTIONS,
        'Resource': 'arn:aws:s3:::BUCKET_NAME/DIR_NAME/*'
    }]
}"""

# Set the new policy
#s3 = boto3.client('s3')
#s3.put_bucket_policy(Bucket=bucket_name, Policy=bucket_policy)

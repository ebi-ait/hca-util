from hca_util.local_state import set_selected_dir
from hca_util.common import print_err


class CmdSelect:
    """
    user: both wrangler and contributor
    aws resource or client used in command - s3 client (list_objects_v2)
    """

    def __init__(self, aws, args):
        self.aws = aws
        self.args = args

    def run(self):

        try:
            s3_client = self.aws.common_session.client('s3')
            bucket = self.aws.bucket_name
            key = self.args.DIR if self.args.DIR.endswith('/') else f'{self.args.DIR}/'

            if key_exists(s3_client, bucket, key):
                set_selected_dir(key)
                print('Selected ' + key)
            else:
                print("Directory does not exist")

        except Exception as e:
            print_err(e, 'select')


def key_exists(client, bucket, key):
    """
    return true if key exists, else false
    A folder/directory is an s3 object with key <uuid>/
    Note: s3://my-bucket/folder != s3://my-bucket/folder/
    Refer to https://www.peterbe.com/plog/fastest-way-to-find-out-if-a-file-exists-in-s3
    for comparison between client.list_objects_v2 and client.head_object to make this check.
    Also check https://stackoverflow.com/questions/33842944/check-if-a-key-exists-in-a-bucket-in-s3-using-boto3
    which suggests using Object.load() - which does a HEAD request, however, HCAContributor doesn't have
    s3:GetObject permission by default, so this will fail for them.
    """
    response = client.list_objects_v2(
        Bucket=bucket,
        Prefix=key,
    )
    for obj in response.get('Contents', []):
        if obj['Key'] == key:
            return True
    return False

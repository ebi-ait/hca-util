import boto3

isContributor = False


def new_session(user_profile):
    return boto3.Session(region_name=user_profile['region'],
                         aws_access_key_id=user_profile['access_key'],
                         aws_secret_access_key=user_profile['secret_key'])


def is_valid_credentials():
    global isContributor
    sts = new_session().client('sts')

    try:
        resp = sts.get_caller_identity()
        arn = resp.get('Arn')
        if arn.endswith('user/HCAContributor'):
            isContributor = True
    except Exception as e:
        print(str(e))
        sys.exit(1)
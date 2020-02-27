


class Aws:
    SECRET_NAME = 'hca/util/secret'

    def __init__(self, session):
        self.session = session
        self.s3 = session.client('s3')
        self.secret_mgr = session.client('secretsmanager')
        self.sts = session.client('sts')

    def sts_get_caller_arn(self):
        try:
            resp = self.sts.get_caller_identity()
            arn = resp.get('Arn')
            return arn
        except Exception as e:
            print(str(e))
            sys.exit(1)


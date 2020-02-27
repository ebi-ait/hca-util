from .command import HcaCmd


class CmdConfig(HcaCmd):

    def cmd_config(self, argv):
        """
        we may not have a session yet, if setup() wasn't successful.
        or we may have.
        In any case, we have to call setup() again after we have new config/creds.
        :param argv:
        :return:
        """

        if len(argv) == 2:
            access_key = argv[0]
            secret_key = argv[1]
            try:
                Aws.set_profile(self.profile, self.region, access_key, secret_key)
                self.setup()

            except Exception as e:
                print(f'An exception of type {e.__class__.__name__} occurred in cmd config.\nDetail: ' + str(e))
        else:
            print('Invalid args. See `help config`')
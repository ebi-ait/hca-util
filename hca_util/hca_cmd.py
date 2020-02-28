from hca_util.user_profile import profile_exists, get_profile, UserProfile
from hca_util.aws_client import Aws
from hca_util.command.config import CmdConfig
from hca_util.command.create import CmdCreate

class HcaCmd():
    """
    steps to perform before executing command
    if cmd is config, skip steps, run config
    else
        check user profile (default or specified via --profile)
        instantiate an aws client
        check valid credentials (via sts get caller identity)
        flag is_contributor
        get bucket name (from secret mgr)
    """

    def __init__(self, args):

        if args.command == 'config':

            CmdConfig(args.ACCESS_KEY, args.SECRET_KEY).run()

        else:

            if profile_exists(args.profile):
                self.user_profile = get_profile(args.profile)
                self.aws = Aws(self.user_profile)

                if self.aws.is_valid_credentials():
                    # print('Valid credentials')
                    try:
                        self.aws.get_bucket_name()
                        self.execute(args)

                    except:
                        print('Unable to get bucket')

                else:
                    print('Invalid credentials')

            else:
                print(f'Profile \'{args.profile}\' not found')

    def execute(self, args):
        if args.command == 'create':
            CmdCreate(self.aws, args).run()

        elif args.command == 'select':
            print('cmd_select ' + args.DIR)
        elif args.command == 'clear':
            print('cmd_clear')
        elif args.command == 'list':
            list_bucket = args.b # optional bool, default False
            print('cmd_list ' + str(list_bucket))
        elif args.command == 'dir':
            print('cmd_dir')
        elif args.command == 'upload':
            # choice 1
            all_files = args.a # optional bool
            # choice 2
            files = args.f # optional list of <_io.TextIOWrapper name='f1' mode='r' encoding='UTF-8'>
            print('cmd_upload ' + str(all_files) + ' ' + str(files))
            if files:
                for f in files:
                    print(f.name)

        elif args.command == 'download':
            # choice 1
            all_files = args.a # optional bool
            # choice 2
            files = args.f # optional list of files
            print('cmd_download ' + str(all_files) + ' ' + str(files))
            if files:
                for f in files:
                    print(f)

        elif args.command == 'delete':
            # choice 1
            all_files = args.a # optional bool
            # choice 2
            files = args.f # optional list of files
            # choice 3
            delete_dir = args.d # optional bool
            print('cmd_delete ' + str(all_files) + ' ' + str(files) + ' ' + str(delete_dir))
            if files:
                for f in files:
                    print(f)
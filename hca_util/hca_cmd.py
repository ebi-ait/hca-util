from hca_util.user_profile import profile_exists, get_profile, UserProfile
from hca_util.aws_client import Aws
from hca_util.command.config import CmdConfig
from hca_util.command.create import CmdCreate
from hca_util.command.select import CmdSelect
from hca_util.command.list import CmdList
from hca_util.command.dir import CmdDir
from hca_util.command.upload import CmdUpload
from hca_util.command.download import CmdDownload


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
            success, msg = CmdConfig(args).run()
            print(msg)

        elif args.command == 'dir':
            CmdDir.run()

        elif args.command == 'clear':
            a = args.a  # clear all
            CmdDir.clear(a)

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
            success, msg = CmdCreate(self.aws, args).run()
            print(msg)

        elif args.command == 'select':
            CmdSelect(self.aws, args).run()

        elif args.command == 'list':
            CmdList(self.aws, args).run()

        elif args.command == 'upload':
            CmdUpload(self.aws, args).run()

        elif args.command == 'download':
            CmdDownload(self.aws, args).run()

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
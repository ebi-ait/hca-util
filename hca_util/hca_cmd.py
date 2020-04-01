from hca_util.user_profile import profile_exists, get_profile
from hca_util.aws_client import Aws
from hca_util.local_state import get_bucket
from hca_util.command.config import CmdConfig
from hca_util.command.create import CmdCreate
from hca_util.command.select import CmdSelect
from hca_util.command.list import CmdList
# from hca_util.command.dir import CmdDir
from hca_util.command.upload import CmdUpload
from hca_util.command.download import CmdDownload
from hca_util.command.delete import CmdDelete
import os

class HcaCmd:
    """
    steps to perform before executing command
    if cmd is config, skip steps, run config
    else
        check user profile (default or specified via --profile)
        instantiate an aws client
        check valid credentials (via sts get caller identity)
        flag is_user
        get bucket name (from secret mgr)
    """

    def __init__(self, args):

        if args.command == 'config':
            success, msg = CmdConfig(args).run()
            print(msg)

            """
            elif args.command == 'dir':
                success, msg = CmdDir.run()
                print(msg)
            """

            """
            elif args.command == 'clear':
                a = args.a  # clear all
                success, msg = CmdDir.clear(a)
                print(msg)
            """

        else:

            if profile_exists(args.profile):
                self.user_profile = get_profile(args.profile)
                self.aws = Aws(self.user_profile)

                if self.aws.is_valid_credentials():
                    # get bucket from local state if set
                    bucket = get_bucket()
                    if bucket:
                        self.aws.bucket_name = bucket
                    else:
                        try:
                            self.aws.get_bucket_name()
                        except:
                            print('Unable to get bucket')

                    self.execute(args)

                else:
                    print('Invalid credentials')

            else:
                print(f'Profile \'{args.profile}\' not found. Please run config command with your access keys')

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
            CmdDelete(self.aws, args).run()

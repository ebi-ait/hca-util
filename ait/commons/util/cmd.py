import os
import sys
from datetime import date
import requests

from ait.commons.util.aws_client import Aws
from ait.commons.util.command.config import CmdConfig
from ait.commons.util.command.create import CmdCreate
from ait.commons.util.command.delete import CmdDelete
from ait.commons.util.command.download import CmdDownload
from ait.commons.util.command.list import CmdList
from ait.commons.util.command.select import CmdSelect
from ait.commons.util.command.upload import CmdUpload
from ait.commons.util.command.sync import CmdSync
from ait.commons.util.local_state import get_bucket, set_attr, get_attr
from ait.commons.util.user_profile import profile_exists, get_profile
from ait.commons.util.settings import NAME, VERSION


class Cmd:
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

        self.check_version()

        if args.command == 'config':
            success, msg = CmdConfig(args).run()
            print(msg)

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
                            sys.exit(1)

                    self.execute(args)

                else:
                    print('Invalid credentials')
                    sys.exit(1)

            else:
                print(f'Profile \'{args.profile}\' not found. Please run config command with your access keys')
                sys.exit(1)
                

    def check_version(self):

        today = date.today()
        last_checked = get_attr('version_checked')

        #print(f'today: {today}, last_checked: {last_checked}')

        if not last_checked or last_checked < today:

            resp = requests.get(f'https://pypi.org/pypi/{NAME}/json')
            latest_version = resp.json()['info']['version']

            if VERSION < latest_version:
                print(f'INFO: A new version of {NAME} is available. Run `pip install {NAME} --upgrade` to upgrade.')
            
            set_attr('version_checked', today)
    

    def execute(self, args):
        if args.command == 'create':
            success, msg = CmdCreate(self.aws, args).run()
            self.exit(success, msg)

        elif args.command == 'select':
            success, msg = CmdSelect(self.aws, args).run()
            self.exit(success, msg)

        elif args.command == 'list':
            success, msg = CmdList(self.aws, args).run()
            self.exit(success, msg)

        elif args.command == 'upload':
            success, msg = CmdUpload(self.aws, args).run()
            self.exit(success, msg)

        elif args.command == 'download':
            success, msg = CmdDownload(self.aws, args).run()
            self.exit(success, msg)

        elif args.command == 'delete':
            success, msg = CmdDelete(self.aws, args).run()
            self.exit(success, msg)

        elif args.command == 'sync':
            success, msg = CmdSync(self.aws, args).run()
            self.exit(success, msg)

    def exit(self, success, message):
        if message:
            print(message)

        if success:
            sys.exit(0)
        else:
            sys.exit(1)

from cmd import Cmd
import shlex
from hca_util.hca_util import *
from hca_util.aws import *


h_upload="""usage: upload F1 [f2] [f3] ...
\tMulti-files upload to selected directory. File names with space need to be within quotes
usage: upload .
\tUpload all files from current user directory"""

h_delete="""usage: delete F1 [f2] [f3] ...
\tDelete specified file(s) from selected directory
usage: delete .
\tDelete all files from selected directory
usage: delete
\tDelete selected directory (authorised user only)"""

h_download="""usage: download F1 [f2] [f3] ...
\tDownload specified file(s) from selected directory to local machine
usage: download .
\tDownload all files from selected directory to local machine"""

h_exit="""usage: exit (or quit)
\tExit the tool. Shorthand: x, q, or Ctrl-D"""


class HcaCmd(Cmd):
    prompt = 'hca> '
    intro = 'Type ? to list commands'

    def __init__(self, args):
        super().__init__() # call parent class constructor

        profile=Aws.DEFAULT_PROFILE
        region=Aws.DEFAULT_REGION

        if args.profile is not None:
            profile = args.profile
            print('Using profile: ' + profile)

        if args.region is not None:
            region = args.region
            print('Using region: ' + region)

        self.util = HcaUtil(profile, region)

    # commands
    def do_config(self, inp):
        self.util.cmd_config(shlex.split(inp))

    def do_create(self, inp):
        self.util.cmd_create(shlex.split(inp))

    def do_list(self, inp):
        self.util.cmd_list(shlex.split(inp))

    def do_select(self, inp):
        self.util.cmd_select(shlex.split(inp))

    def do_dir(self, inp):
        self.util.cmd_dir(shlex.split(inp))

    def do_upload(self, inp):
        self.util.cmd_upload(shlex.split(inp))

    def do_delete(self, inp):
        self.util.cmd_delete(shlex.split(inp))

    def do_download(self, inp):
        self.util.cmd_download(shlex.split(inp))

    def do_exit(self, inp):
        print('Bye')
        return True

    def default(self, inp):
        if inp == 'x' or inp == 'q' or inp == 'quit':
            return self.do_exit(inp)

        print(f'No such command. Try `help`')

    # help info
    def help_config(self):
        print(h_config)

    def help_create(self):
        print(h_create)

    def help_list(self):
        print(h_list)

    def help_select(self):
        print(h_select)

    def help_dir(self):
        print(h_dir)

    def help_upload(self):
        print(h_upload)

    def help_delete(self):
        print(h_delete)

    def help_download(self):
        print(h_download)

    def help_exit(self):
        print(h_exit)


#    do_EOF = do_exit
#    help_EOF = help_exit


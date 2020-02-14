from cmd import Cmd
from hca_util import *

h_config="""usage: config ACCESS_KEY SECRET_KEY
\tConfigure your machine with credentials"""

h_create="""usage: create <project_name>
\tCreate an upload directory for project (wrangler only)
\tProject name is optional
\tIf specified, needs to be between 1-12 alphanumeric characters with no space"""

h_list="""usage: list
\tList contents of bucket (wrangler only)
usage: list DIR_NAME
\tList contents of directory"""

h_select="""usage: select DIR_NAME
\tSelect active directory for upload and download"""

h_dir="""usage: dir
\tShow selected directory"""

h_upload="""usage: upload F1 <f2> <f3> ...
\tMulti-files upload to selected directory
usage: upload .
\tUpload all files from current user directory"""

h_delete="""usage: delete F1 <f2> <f3> ...
\tDelete file(s) within selected directory
usage: delete DIR_NAME
\tDelete specified directory"""

h_download="""usage: download F1 <f2> <f3> ...
\tDownload specified files from remote to current user directory
usage: download .
\tDownload all files from remote directory"""


class HcaCmd(Cmd):
    prompt = 'hca> '
    intro = 'Type ? to list commands'

    util = HcaUtil()

    # commands
    def do_config(self, inp):
        self.util.cmd_config(inp.split())

    def do_create(self, inp):
        self.util.cmd_create(inp.split())

    def do_list(self, inp):
        self.util.cmd_list(inp.split())

    def do_select(self, inp):
        self.util.cmd_select(inp.split())

    def do_dir(self, inp):
        self.util.cmd_dir(inp.split())

    def do_upload(self, inp):
        self.util.cmd_upload(inp.split())

    def do_delete(self, inp):
        self.util.cmd_delete(inp.split())

    def do_download(self, inp):
        self.util.cmd_download(inp.split())

    def do_exit(self, inp):
        print('Bye')
        return True

    def default(self, inp):
        if inp == 'x' or inp == 'q':
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
        print('usage: exit\n\tExit the tool. Shorthand: x q Ctrl-D.')


    do_EOF = do_exit
    help_EOF = help_exit

if __name__ == '__main__':
    HcaCmd().cmdloop()

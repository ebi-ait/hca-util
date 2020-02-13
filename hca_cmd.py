from cmd import Cmd

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

h_download="""usage: download F1 <f2> <f3> ...
\tDownload specified files from remote to current user directory
usage: download .
\tDownload all files from remote directory"""


class HcaUtil:
    session = None

    # default constructor
    def __init__(self):
        print('HcaUtil')

    def cmd_config(self, argv):
        print('cmd config')


class HcaCmd(Cmd):
    prompt = 'hca> '
    intro = 'Type ? to list commands'

    util = HcaUtil()

    def do_config(self, inp):
        self.util.cmd_config(inp)

    def do_create(self, inp):
        print("create '{}'".format(inp))

    def do_list(self, inp):
        print("list '{}'".format(inp))

    def do_select(self, inp):
        print("select '{}'".format(inp))

    def do_dir(self, inp):
        print("dir '{}'".format(inp))

    def do_upload(self, inp):
        print("upload '{}'".format(inp))

    def do_download(self, inp):
        print("download '{}'".format(inp))

    def do_exit(self, inp):
        print('Bye')
        return True

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

    def help_download(self):
        print(h_download)

    def help_exit(self):
        print('usage: exit\n\tExit the tool. Shorthand: x q Ctrl-D.')

    def default(self, inp):
        if inp == 'x' or inp == 'q':
            return self.do_exit(inp)

        print(f'No such command. Try `help`')


    do_EOF = do_exit
    help_EOF = help_exit

if __name__ == '__main__':
    HcaCmd().cmdloop()

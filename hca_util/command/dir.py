from .command import HcaCmd


class CmdDir(HcaCmd):

    def cmd_dir(self, argv):
        """Returns currently selected dir or None."""
        print(self.selected_dir)
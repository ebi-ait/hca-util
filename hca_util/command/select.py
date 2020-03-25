from hca_util.local_state import get_selected_area, set_selected_area
from hca_util.common import print_err


class CmdSelect:
    """
    user: both wrangler and contributor
    aws resource or client used in command - s3 client (list_objects_v2)
    """

    def __init__(self, aws, args):
        self.aws = aws
        self.args = args

    def run(self):
        try:
            if self.args.AREA:
                key = self.args.AREA if self.args.AREA.endswith('/') else f'{self.args.AREA}/'

                if self.aws.obj_exists(key):
                    set_selected_area(key)
                    print('Selected upload area ' + key)
                else:
                    print("Upload area does not exist")
            else:
                print('Currently selected upload area is ' + get_selected_area())

        except Exception as e:
            print_err(e, 'select')

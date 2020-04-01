from hca_util.common import format_err
from hca_util.local_state import get_selected_area, set_selected_area


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
                    return True, 'Selected upload area is ' + key
                else:
                    return False, "Upload area does not exist"
            else:
                selected_area = get_selected_area()
                if selected_area:
                    return True, 'Currently selected upload area is ' + get_selected_area()
                else:
                    return False, 'No upload area currently selected'

        except Exception as e:
            return False, format_err(e, 'select')

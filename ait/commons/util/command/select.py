from ait.commons.util.common import format_err
from ait.commons.util.local_state import get_selected_area, set_selected_area


class CmdSelect:
    """
    admin and user
    aws resource or client used in command - 
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
                    return True, f'Selected upload area is {key}'
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

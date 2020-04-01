from hca_util.common import serialize, deserialize
from hca_util.settings import LOCAL_STATE_FILE


class LocalState:

    def __init__(self):
        self.bucket = None # default
        self.selected_area = None
        self.known_areas = []
        # potential other local state vars
        self.tmp_access_key = None
        self.tmp_secret_key = None
        self.token = None

    def select_area(self, area_name):
        self.selected_area = area_name

        if area_name not in self.known_areas:
            self.known_areas.append(area_name)

    def unselect_area(self):
        self.selected_area = None

    def __str__(self):
        if self.selected_area:
            s = f'Selected {self.selected_area}'
        else:
            s = 'No area selected'

        s += '\nKnown areas:\n'
        known_areas_minus_selected = [d for d in self.known_areas if d != self.selected_area]

        if known_areas_minus_selected:
            s += '\n'.join(map(str, known_areas_minus_selected))
        else:
            s += 'None'

        return s

def get_local_state():
    obj = deserialize(LOCAL_STATE_FILE)
    if obj and isinstance(obj, LocalState):
        return obj
    return LocalState()


def set_local_state(obj):
    serialize(LOCAL_STATE_FILE, obj)


def get_selected_area():
    obj = deserialize(LOCAL_STATE_FILE)
    if obj and isinstance(obj, LocalState):
        return obj.selected_area
    return None


def set_selected_area(area_name):
    obj = deserialize(LOCAL_STATE_FILE)
    if obj is None or not isinstance(obj, LocalState):
        obj = LocalState()
    obj.select_area(area_name)
    serialize(LOCAL_STATE_FILE, obj)


def get_bucket():
    obj = deserialize(LOCAL_STATE_FILE)
    if obj and isinstance(obj, LocalState):
        return obj.bucket
    return None

    
def set_bucket(bucket):
    obj = deserialize(LOCAL_STATE_FILE)
    if obj is None or not isinstance(obj, LocalState):
        obj = LocalState()
    obj.bucket(bucket)
    serialize(LOCAL_STATE_FILE, obj)

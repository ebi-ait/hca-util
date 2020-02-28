from hca_util.common import serialize, deserialize
from hca_util.settings import LOCAL_STATE_FILE


class LocalState:

    def __init__(self):
        self.selected_dir = None
        self.known_dirs = []
        self.tmp_access_key = None
        self.tmp_secret_key = None
        self.token = None

    def select_dir(self, dir_name):
        self.selected_dir = dir_name

        if dir_name not in self.known_dirs:
            self.known_dirs.append(dir_name)

    def unselect_dir(self):
        self.selected_dir = None

    def __str__(self):
        s = 'Selected ' + str(self.selected_dir) + '\nKnown dirs:\n'
        other_dirs = [d for d in self.known_dirs if d != self.selected_dir]
        if not other_dirs:  # empty list
            s += 'None'
        else:
            s += '\n'.join(map(str, other_dirs))

        return s


def set_selected_dir(dir_name):
    obj = deserialize(LOCAL_STATE_FILE)
    if obj is None or not isinstance(obj, LocalState):
        obj = LocalState()
    obj.select_dir(dir_name)
    serialize(LOCAL_STATE_FILE, obj)


def get_local_state():

    obj = deserialize(LOCAL_STATE_FILE)
    if obj and isinstance(obj, LocalState):
        return obj
    return LocalState()


def set_local_state(obj):
    serialize(LOCAL_STATE_FILE, obj)


def get_selected_dir():
    obj = deserialize(LOCAL_STATE_FILE)
    if obj and isinstance(obj, LocalState):
        return obj.selected_dir
    return None

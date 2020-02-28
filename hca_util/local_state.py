from hca_util.common import serialize, deserialize
from hca_util.settings import LOCAL_STATE_FILE


class LocalState:

    def __init__(self):
        self.selected_dir = None
        self.known_dirs = []
        self.tmp_access_key = None
        self.tmp_secret_key = None
        self.token = None

    def add_dir(self, dir):
        if dir not in self.known_dirs:
            self.known_dirs.append(dir)

    def del_dir(self, dir):
        if dir in self.known_dirs:
            self.known_dirs.remove(dir)

    def reset_dirs(self):
        self.known_dirs = []

    def select_dir(self, dir):
        self.selected_dir = dir
        self.addDir(dir)

    def unselect_dir(self):
        self.selected_dir = None

    def __str__(self):
        print('Selected ' + self.selected_dir)


def set_selected_dir(dir_name):
    obj = deserialize(LOCAL_STATE_FILE)
    if obj is None or not isinstance(obj, LocalState):
        obj = LocalState()
    obj.selected_dir = dir_name
    serialize(LOCAL_STATE_FILE, obj)


def get_selected_dir():
    obj = deserialize(LOCAL_STATE_FILE)
    if obj and isinstance(obj, LocalState):
        return obj.selected_dir
    return None

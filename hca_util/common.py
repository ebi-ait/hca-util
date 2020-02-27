# common functions

import uuid
import pickle

MAX_LEN_PROJECT_NAME = 36


def gen_uuid():
    return str(uuid.uuid4())


def is_valid_uuid(val):
    try:
        uuid.UUID(str(val))
        return True
    except ValueError:
        return False


def is_valid_project_name(name):
    """Project name has to be between 1 and MAX_LEN chars and contains only alphanum chars"""
    if name.isalnum() and 0 < len(name) <= MAX_LEN_PROJECT_NAME:
        return True
    else:
        return False


def is_valid_dir_name(dir_name):
    """Directory name format: uuid with or without /
    """
    if len(dir_name) < 36:
        return False
    elif len(dir_name) == 36:  # uuid without /
        return is_valid_uuid(dir_name)
    elif len(dir_name) == 37 and dir_name.endswith('/'):  # uuid with /
        uuid_part = dir_name[0:36]
        return is_valid_uuid(uuid_part)
    return False


def serialize(name, obj):
    """Returns True if serialized."""
    try:
        pickle_out = open(name, 'wb')
        pickle.dump(obj, pickle_out)
        pickle_out.close()
        return True
    except Exception as e:
        print(str(e))
        return False


def deserialize(name):
    """Returns None if can't deserialize or not found."""
    try:
        pickle_in = open(name, 'rb')
        obj = pickle.load(pickle_in)
        pickle_in.close()
    except (OSError, IOError) as e:
        obj = None
    return obj

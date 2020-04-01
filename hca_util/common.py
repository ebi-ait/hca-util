# common functions

import os
import uuid
import pickle

from hca_util.settings import DEBUG_MODE

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


def is_valid_area_name(area_name):
    """Area name format: uuid with or without /
    """
    if len(area_name) < 36:
        return False
    elif len(area_name) == 36:  # uuid without /
        return is_valid_uuid(area_name)
    elif len(area_name) == 37 and area_name.endswith('/'):  # uuid with /
        uuid_part = area_name[0:36]
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


def create_if_not_exists(file):
    """
    Create the file if it does not exist
    :param file:
    :return:
    """
    if not os.path.exists(file):
        basedir = os.path.dirname(file)
        if not os.path.exists(basedir):
            os.makedirs(basedir)
        open(file, 'w').close()


def print_err(e, cmd):
    """
    Print user-friendly error message or exception details depending on DEBUG MODE
    :param e:
    :param cmd:
    :return:
    """
    err = str(e)
    if 'Forbidden' in err or 'AccessDenied' in err:
        print('You don\'t have permission to use this command')
        return
    if DEBUG_MODE:
        print(f'An exception of type {e.__class__.__name__} occurred in command {cmd}.\nDetail: ' + str(e))
    else:
        print(f'An error occurred in command: {cmd}')

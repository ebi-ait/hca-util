# common functions

import uuid
import pickle


def gen_uuid():
    return str(uuid.uuid4())


def is_valid_uuid(val):
    try:
        uuid.UUID(str(val))
        return True
    except ValueError:
        return False


def serialize(name, obj):
    pickle_out = open(name, 'wb')
    pickle.dump(obj, pickle_out)
    pickle_out.close()


def deserialize(name):
    pickle_in = open(name, 'rb')
    obj = pickle.load(pickle_in)
    pickle_in.close()
    return obj

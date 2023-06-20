MORPHIC_UTIL = True
MAX_LEN_PROJECT_NAME = 36

if MORPHIC_UTIL:
    # import morphic_util specific settings
    from ait.commons.util.settings.morphic_util import *
else:
    # default to hca_util settings
    from ait.commons.util.settings.hca_util import *

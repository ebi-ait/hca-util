COVID_UTIL = False

if COVID_UTIL:
    # import covid_util specific settings
    from ait.commons.util.settings.covid_util import *
else:
    # default to hca_util settings
    from ait.commons.util.settings.hca_util import *

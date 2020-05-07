COVID_UTIL = False

if COVID_UTIL:
    # import covid_util specific settings
    from settings.covid_util import *
else:
    # default to hca_util settings
    from settings.hca_util import *

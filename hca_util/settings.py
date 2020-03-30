from pathlib import Path

# when true, displays exception details; otherwise user-friendly error message
DEBUG_MODE = True

# user home directory
USER_HOME = str(Path.home())

# aws config and credentials files
AWS_CONFIG_FILE = USER_HOME + '/.aws/config'
AWS_CREDENTIALS_FILE = USER_HOME + '/.aws/credentials'

AWS_SECRET_NAME = 'covid/util/secret'

# default profile uses credentials from [DEFAULT_PROFILE] section of AWS_CREDENTIALS_FILE
# and config from [profile DEFAULT_PROFILE] section of AWS_CONFIG_FILE
DEFAULT_PROFILE = 'covid-util'
DEFAULT_REGION = 'us-east-1'

# local state for user
LOCAL_STATE_FILE = USER_HOME + '/.covid-util'

# contributor IAM user name
IAM_USER_CONTRIBUTOR = 'COVIDUser'

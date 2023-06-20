from pathlib import Path

NAME = 'morphic-util'
VERSION = '0.0.4'
DESC = 'CLI tool for uploading data to Morphic AWS S3 bucket'
AUTHOR = 'hca-ingest-dev'
AUTHOR_EMAIL = 'hca-ingest-dev@ebi.ac.uk'

# when true, displays exception details; otherwise user-friendly error message
DEBUG_MODE = False

DIR_SUPPORT = False

MAX_DIR_DEPTH = 5

# user home directory
USER_HOME = str(Path.home())

# aws config and credentials files
AWS_CONFIG_FILE = USER_HOME + '/.aws/config'
AWS_CREDENTIALS_FILE = USER_HOME + '/.aws/credentials'

AWS_SECRET_NAME = 'hca/util/secret'

# default profile uses credentials from [DEFAULT_PROFILE] section of AWS_CREDENTIALS_FILE
# and config from [profile DEFAULT_PROFILE] section of AWS_CONFIG_FILE
DEFAULT_PROFILE = 'hca-util'
DEFAULT_REGION = 'eu-west-2'

# local state for user
LOCAL_STATE_FILE = USER_HOME + '/.hca-util'

# 2 IAM user types: admin and (normal) user
# in the context of hca, admin=wrangler and user=contributor
IAM_USER = 'dipayan1985'
IAM_ADMIN = 'dipayan1985Admin'

AWS_ACCOUNT = '362836482250'

AWS_SECRET_NAME_AK_BUCKET = 'AK-bucket'
AWS_SECRET_NAME_SK_BUCKET = 'SK-bucket'
AWS_SECRET_NAME_MORPHIC_BUCKET = 's3-bucket'

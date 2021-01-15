from ait.commons.util.settings import AWS_ACCOUNT, IAM_USER

"""
User groups:
1. admin currently has full s3 access
2. other user has restricted access including (specified in user policy)

a) list upload area contents
    {
      "Sid": "AllowListBucketExceptRootDirectory",
      "Effect": "Allow",
      "Action": "s3:ListBucket",
      "Resource": "arn:aws:s3:::<bucket>",
      "Condition": {
        "StringLike": {
          "s3:prefix": [
            "*/*"
          ]
        }
      }
    }

b) default upload and delete (ux) permission on upload areas

    {
      "Sid": "DefaultUploadAreaAccess",
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:DeleteObject",
        "s3:GetObjectTagging"
      ],
      "Resource": "arn:aws:s3:::<bucket>/*/*"
    }

    (and get obj tagging permission)


Upload area permissions
Abbrev  Desc.       S3 action           S3 operation/API request
                    (object ops perms)
u       upload      s3:PutObject        # PUT Object, POST Object, Initiate Multipart Upload, Upload Part, Complete Multipart Upload, PUT Object - Copy
d       download    s3:GetObject        # GET Object, HEAD Object, SELECT Object Content
x       delete      s3:DeleteObject     # DELETE Object

Possible combinations are 'u', 'ud', 'ux', 'udx'

"""

ALLOWED_PERMS = ['u', 'ud', 'ux', 'udx']
DEFAULT_PERMS = 'ux'

# constraints - in bucket policy
# ux       denyDelete                  -> u
# ux       allowDownload               -> udx
# ux       allowDownload + denyDelete  -> ud

def allowDownloadStmt():
    return {
    "Sid": "AllowDownload",
    "Effect": "Allow",
    "Action": "s3:GetObject",
    "Resource": [],
    "Principal": { "AWS": [f"arn:aws:iam::{AWS_ACCOUNT}:user/{IAM_USER}"] }
}

def denyDeleteStmt():
    return {
    "Sid": "DenyDelete",
    "Effect": "Deny",
    "Action": "s3:DeleteObject",
    "Resource": [],
    "Principal": { "AWS": [f"arn:aws:iam::{AWS_ACCOUNT}:user/{IAM_USER}"] }
}

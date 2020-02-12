# hca_util

This tool is intended to allow HCA wranglers and contributors to upload and download data to/from the HCA S3 bucket.

The following are the main 3 steps users need to run through:
- Set up AWS with security credentials
- Install the tool
- Use tool to upload and download data

The following assumes the user has basic command-line knowledge and has `python3.x` installed on their machine as the only prerequisite.


## Set up AWS with security credentials

Contributors will be provided with a pair of access and secret keys which they need to configure AWS.

Install and configure AWS CLI

`pip install awscli`

If first time using AWS, either run `aws configure` as follows:
```
aws configure
Enter Access key <USER_ACCESS_KEY>
Enter Secret <USER_SECRET_ACCESS_KEY>
Enter us-east-1
Enter json
```
 
Or, create and edit `.aws/credentials` and add the credentials as follows:
```
[default]
aws_access_key_id = <USER_ACCESS_KEY>
aws_secret_access_key = <USER_SECRET_ACCESS_KEY>
```

If the user has an existing AWS profile, for e.g. if they have previously configured S3/AWS, 
then add a new HCA profile to the `.aws/credentials` file.
```
[default]
aws_access_key_id = ...
aws_secret_access_key = ...
[hca]
aws_access_key_id = <USER_ACCESS_KEY>
aws_secret_access_key = <USER_SECRET_ACCESS_KEY>
```
Set the environment variable `AWS_PROFILE` to `hca` to enable it before using the tool.
```
export AWS_PROFILE=hca
```


 ## Install the tool
 
The tool is in the repository here: https://github.com/ebi-ait/hca_util
 
You can either clone the repository (`git clone https://github.com/ebi-ait/hca_util.git`) if you have git installed, or just copy the files `hca_util.py` and `requirements.txt` to a local folder.
 
Navigate where the files are and run `pip install` as follows to install the deps.
 
 ```
cd hca_util
pip install -r requirements.txt
```

 
 ## Use tool to upload and download data
 
 Run `./hca_util.py` to see the options/commands available. Note only wranglers with their elevated access can create directory and list all directories.
 
 ```
    hca_util.py create             Create an upload directory (wrangler only)
    hca_util.py list               List contents of bucket (wrangler only)
    hca_util.py select <dir_name>  Select directory
    hca_util.py list <dir_name>    List contents of directory
    hca_util.py dir                Show selected directory
    hca_util.py upload <f1> [<f2>..]   Upload specified file or files. Error if no directory selected
    hca_util.py upload .           Upload all files in current directory. Error if no directory selected
    hca_util.py download           Download all files from selected directory
    hca_util.py download <f1>[<f2>..] Download specified files from selected directory
```
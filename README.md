# hca_util

This tool is intended to allow HCA wranglers and contributors to upload and download data to/from the HCA S3 bucket.

The following are the main 3 steps users need to run through:
- Set up AWS with security credentials
- Install the tool
- Use tool to upload and download data

## Set up AWS with security credentials

Contributors will be provided with a pair of access and secret keys which they need to configure AWS.

Prerequisite: it is assumed `python3.x` is already installed on the machine.

Install and configure AWS CLI

`pip install awscli`

First time using AWS:

Either run `aws configure`
 
 
 Or create and edit `.aws/credentials` and add the following lines:
 
 ## Install the tool
 
 The tool is in the repository here: https://github.com/ebi-ait/hca_util
 
 You can either clone the repository (`git clone https://github.com/ebi-ait/hca_util.git`) if you have git installed, or just copy the files `hca_util.py` an `requirements.txt` to a local folder.
 
Navigate where the files are and run `pip install` as follows to install the deps.
 
 ```
cd hca_util
pip install -r requirements.txt
```
 
 ## Use tool to upload and download data
 
 Run `./hca_util.py` to see the options/commands available.
 
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
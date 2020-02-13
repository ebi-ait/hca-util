# hca-util

This tool is intended to allow HCA wranglers and contributors to upload and download data to/from the HCA S3 bucket.

https://github.com/ebi-ait/hca-util

## Prerequisites
Users need to have
1. Basic command-line knowledge
2. Python3.x installed on their machine
3. Credentials to access data in the S3 bucket (access and secret keys)

## Install and configure
1. Get the tool from PyPi
2. Run the `hca-util` tool
3. Run `config` command specifying your credentials

    
    #1   $ pip install hca-util
    #2   $ hca-util
         Type ? to list commands
         hca>
    #3   hca> config ACCESS_KEY SECRET_KEY

Step 2 opens an interactive prompt.

Step 3 adds a new _hca-util_ profile to your local AWS configuration which the tool uses.


## Use the tool to upload and download data
The following commands are currently possible.

    command                         description
    =======                         ===========
    config ACCESS_KEY SECRET_KEY    Configure your machine with credentials
    create <project_name>           Create an upload directory for project (wrangler only)
                                    Project name is optional
                                    If specified, needs to be between 1-12 alphanumeric characters with no space
    list                            List contents of bucket (wrangler only)
    list DIR_NAME                   List contents of directory
    select DIR_NAME                 Select active directory for upload and download
    dir                             Show selected directory
    upload F1 <f2> <f3> ...         Multi-files upload to selected directory
    upload .                        Upload all files from current user directory
    download F1 <f2> <f3> ...       Download specified files from remote to current user directory
    download .                      Download all files from remote directory



Type ? or `help` to list commands. 

Type `help <command>` to display help info about a command.

Note only wranglers with their elevated access can create directory and list all directories.

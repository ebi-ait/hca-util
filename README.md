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

        $ pip install hca-util

2. Run the `hca-util` tool

        $ hca-util
        Type ? to list commands
        hca>

3. Run `config` command specifying your credentials

        hca> config ACCESS_KEY SECRET_KEY

Step 2 opens an interactive prompt.

Step 3 adds a new *hca-util* profile to your local AWS configuration which the tool uses.


## Use the tool to upload and download data
The following commands are currently possible.

    command                         description
    =======                         ===========
    config ACCESS_KEY SECRET_KEY    Configure your machine with credentials
    
    create [project_name] [-udx]    Create an upload directory for project (authorised user only)
                                    If specified, project name needs to be between 1-36 alphanumeric characters with no space
                                    If specified, allowed permissions include 'u', 'ud', 'ux' and 'udx'; otherwise default 'ux'
                                    u - upload, d - download, x - delete
                                    
    list                            List contents of bucket (authorised user only)
    list DIR_NAME                   List contents of directory
    
    select DIR_NAME                 Set active directory for upload and download
    dir                             Show selected directory
    
    upload F1 [f2] [f3] ...         Multi-files upload to selected directory
    upload .                        Upload all files from current user directory
    
    delete F1 [f2] [f3] ...         Delete specified file(s) from selected directory
    delete .                        Delete all files from selected directory
    delete                          Delete selected directory (authorised user only)
    
    download F1 [f2] [f3] ...       Download specified file(s) from selected directory to local machine
    download .                      Download all files from selected directory to local machine
    
    exit (or quit)                  Exit the tool. Shorthand: x, q, or Ctrl-D

Type ? or `help` to list commands. 

Type `help <command>` to display help info about a command.

Note only authorised users (for e.g. wranglers, devs) with their elevated access can create directory and list all directories.


## For Developers

Run 
```
python -m hca_util.__main__
```

Run tests
```
python -m tests.test_hca_util
```

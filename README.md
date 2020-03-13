# hca-util

CLI tool for file transfer (upload and download) to/from AWS S3.

https://github.com/ebi-ait/hca-util

# Users

## Prerequisites
Users need to have
1. Basic command-line knowledge
2. Python3.x installed on their machine
3. Credentials to access data in the S3 bucket (access and secret keys)

## Install
Get `hca-util` from PyPi.

    $ pip install hca-util

                           
## Usage

You use the tool by specifying the command you want to run and any mandatory (positional) or optional arguments.

Using the `-h` option to display help information:

    $ hca-util -h
    usage: hca-util [-h] [--profile PROFILE]
                       {config,create,select,dir,clear,list,upload,download,delete}

help for specific command:

        hca-util <command> -h
    
    
## List of commands

The following is a list of commands available to use. Note some commands or options/flags are available to authorised users (for e.g. wranglers, admin) only.

    config              configure AWS credentials
    create              create an upload directory (authorised user only)
    select              select active directory
    dir                 display active (selected) directory
    clear               clear current selection
    list                list contents of selected directory
    upload              upload files to selected directory
    download            download files from selected directory
    delete              delete files from selected directory


## `config` command

To configure your AWS credentials

    $ hca-util config -h
    usage: hca-util config [-h] [--profile PROFILE] ACCESS_KEY SECRET_KEY
    
    positional arguments:
      ACCESS_KEY         AWS Access Key ID
      SECRET_KEY         AWS Secret Access Key
    
    optional arguments:
      -h, --help         show this help message and exit
      --profile PROFILE  use PROFILE instead of default 'hca-util' profile

By default, this tool looks for and uses the profile name *hca-util*, if it exists, or it can be set by the `config` command.

You can always specify a different profile each time you run a command using the optional argument `--profile PROFILE`.

## `create` command

    $ hca-util create -h
    usage: hca-util create [-h] [-n name] [-p {u,ud,ux,udx}]
                              [--profile PROFILE]
    
    optional arguments:
      -h, --help         show this help message and exit
      -n name            optional project name for new directory
      -p {u,ud,ux,udx}   allowed actions (permissions) on new directory. u for
                         upload, x for delete and d for download. Default is ux
      --profile PROFILE  use PROFILE instead of default 'hca-util' profile

## `select` command

    $ hca-util select -h
    usage: hca-util select [-h] [--profile PROFILE] DIR
    
    positional arguments:
      DIR                directory uuid
    
    optional arguments:
      -h, --help         show this help message and exit
      --profile PROFILE  use PROFILE instead of default 'hca-util' profile


## `dir` command

    $ hca-util dir -h
    usage: hca-util dir [-h]
    
    optional arguments:
      -h, --help  show this help message and exit
      

## `clear` command

    $ hca-util clear -h
    usage: hca-util clear [-h] [-a]
    
    optional arguments:
      -h, --help  show this help message and exit
      -a          clear all - selection and known dirs


## `list` command

    $ hca-util list -h
    usage: hca-util list [-h] [-b] [--profile PROFILE]
    
    optional arguments:
      -h, --help         show this help message and exit
      -b                 list all directories in bucket (authorised user only)
      --profile PROFILE  use PROFILE instead of default 'hca-util' profile





## `upload` command

    $ hca-util upload -h
    usage: hca-util upload [-h] (-a | -f file [file ...]) [-o]
    
    optional arguments:
      -h, --help          show this help message and exit
      -a                  upload all files from current user directory
      -f file [file ...]  upload specified file(s)
      -o                  overwrite files with same names


## `download` command

    $ hca-util download -h
    usage: hca-util download [-h] (-a | -f file [file ...])
    
    optional arguments:
      -h, --help          show this help message and exit
      -a                  download all files from selected directory
      -f file [file ...]  download specified file(s) only



## `delete` command

    $ hca-util delete -h
    usage: hca-util delete [-h] (-a | -f file [file ...] | -d)
    
    optional arguments:
      -h, --help          show this help message and exit
      -a                  delete all files from selected directory
      -f file [file ...]  delete specified file(s) only
      -d                  delete directory and contents (authorised user only)


# Developers

Run 
```
python -m hca_util.__main__
```

Run tests
```
python -m tests.test_hca_util
```

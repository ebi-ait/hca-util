# hca-util

CLI tool for uploading data to the Human Cell Atlas AWS S3 buckets.

# Users

## Prerequisites
Users need to have
1. Basic command-line knowledge
2. Python3.x installed on their machine
3. Credentials to access data in the S3 bucket (access and secret keys)

## Install
The [hca-util](https://pypi.org/project/hca-util/) tool is available to install from PyPi.

```shell script
$ pip install hca-util
```

Note there is a version of this tool published as [covid-util](https://pypi.org/project/covid-util/) in PyPi for uploading data to the European COVID-19 data platform. This version uses its own separate data storage and access credentials. 
                           
## Usage

Display help and list of commands.

```shell script
$ hca-util -h
usage: hca-util [-h] [--version] [--profile PROFILE] {config,create,select,list,upload,download,delete} ...

hca-util

optional arguments:
  -h, --help            show this help message and exit
  --version, -v         show program's version number and exit
  --profile PROFILE     use PROFILE instead of default 'hca-util' profile

command:
  {config,create,select,list,upload,download,delete}
    config              configure AWS credentials
    create              create an upload area (authorised users only)
    select              select or show the active upload area
    list                list contents of the area
    upload              upload files to the area
    download            download files from the area
    delete              delete files from the area
```

In the above, optional arguments are between `[]` and choices between `{}`.

The basic usage is as follows:

```shell script
$ hca-util cmd ARG1 ARG2 -o1 -o2
```

Use the tool by specifying a command (`cmd` - see list below) to run, any mandatory (positional) arguments (e.g. `ARG1` and `ARG2` - see positional args for each command), and any optional arguments (e.g. `-o1` and `o2` - see options for each command).

## Commands

Help with specific command:

```shell script
$ hca-util <cmd> -h
```

Some commands or options/flags are restricted to authorised users (admin) only.

## `config` command

Configure AWS credentials

```shell script
$ hca-util config ACCESS_KEY SECRET_KEY

positional arguments:
  ACCESS_KEY         AWS Access Key ID
  SECRET_KEY         AWS Secret Access Key
```

The tool uses the profile name _hca-util_ in local AWS config files.

Once configured, the set up can be checked by running the command again, this time without credentials (`hca-util config`), to verify if the previously entered credentials are valid or not.

## `create` command

Create an upload area **(authorised users only)**

```shell script
$ hca-util create NAME [-p {u,ud,ux,udx}]


positional arguments:
  NAME               name for the new area

optional arguments:
  -p {u,ud,ux,udx}   allowed actions (permissions) on new area. u for
                     upload, x for delete and d for download. Default is ux
```

## `select` command

Show or select the active upload area

```shell script
$ hca-util select AREA

positional arguments:
  AREA                area uuid. 
```

If AREA is not specified, the selected area is shown.

## `list` command

List contents of selected area

```shell script
$ hca-util list [-b]

optional arguments:
  -b                 list all areas in bucket **(authorised users only)**
```

## `upload` command

Upload files to the selected area

```shell script
$ hca-util upload PATH [PATH ...] [-o]

positional arguments:
  PATH               valid file or directory

optional arguments:
  -o                  overwrite files with same names
```


## `download` command

Download files from the selected area

```shell script
$ hca-util download (-a | -f file [file ...])

optional arguments:
  -a                  download all files from selected area
  -f file [file ...]  download specified file(s) only
```

## `delete` command

Delete files from the selected area

```shell script
$ hca-util delete [-a | -d] [PATH [PATH ...]]

positional arguments:
  PATH               path to file or directory to delete

optional arguments:
  -a                 delete all files from the area
  -d                 delete upload area and contents (authorised users only)
```

## `sync` command

Transfer files from the selected area to Ingest upload area

```shell script
$ hca-util sync INGEST_UPLOAD_AREA

positional arguments:
  INGEST_UPLOAD_AREA  Ingest upload area
```

INGEST_UPLOAD_AREA format: `s3://org-hca-data-archive-upload-_ENV_/_UUID_/`


# Developers
Download dependencies
```
pip install -r requirements.txt
```

Run 

```shell script
python3 -m ait.commons.util
```

Run tests

```shell script
nosetests
```

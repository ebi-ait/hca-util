# hca-util

CLI tool for uploading and downloading files from an HCA upload area.

https://github.com/ebi-ait/hca-util

# Users

## Prerequisites
Users need to have
1. Basic command-line knowledge
2. Python3.x installed on their machine
3. Credentials to access data in the S3 bucket (access and secret keys)

## Install
Get `hca-util` from PyPi.

```shell script
$ pip install hca-util
```
                           
## Usage

Display help

```shell script
$ hca-util -h
usage: hca-util [-h] [--profile PROFILE]
                   {config,create,select,dir,clear,list,upload,download,delete}
```

In the above, optional arguments are between `[]` and choices between `{}`.

The basic usage is as follows:

```shell script
$ hca-util cmd ARG1 ARG2 -o1 -o2
```

Use the tool by specifying a command (`cmd` - see list below) to run, any mandatory (positional) arguments (e.g. `ARG1` and `ARG2` - see positional args for each command), and any optional arguments (e.g. `-o1` and `o2` - see options for each command).

## List of commands

help for a specific command:

```shell script
$ hca-util <command> -h
```

Some commands or options/flags are restricted to authorised users (for e.g. wranglers, admin) only.

## `config` command

Configure AWS credentials

```shell script
$ hca-util config ACCESS_KEY SECRET_KEY

positional arguments:
  ACCESS_KEY         AWS Access Key ID
  SECRET_KEY         AWS Secret Access Key
```

By default, this tool looks for and uses the profile name _hca-util_, if it exists, or it can be set by the `config` command.

Running a command with the `--profile` argument uses the specified profile instead of the default _hca-util_ profile.

## `create` command

Create an upload area **(authorised users only)**

```shell script
$ hca-util create [-n name] [-p {u,ud,ux,udx}]

optional arguments:
  -n name            optional project name for new area
  -p {u,ud,ux,udx}   allowed actions (permissions) on new area. u for
                     upload, x for delete and d for download. Default is ux
```

## `select` command

Select or show the active upload area

```shell script
$ hca-util select AREA

positional arguments:
  AREA                area uuid. If not present then selected area is shown
```

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
$ hca-util upload (-a | -f file [file ...]) [-o]

optional arguments:
  -a                  upload all files from current user directory
  -f file [file ...]  upload specified file(s)
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
$ hca-util delete (-a | -f file [file ...] | -d)

optional arguments:
  -a                  delete all files from selected area
  -f file [file ...]  delete specified file(s) only
  -d                  delete area and contents **(authorised users only)**
```

# Developers

Run 

```shell script
python -m hca_util.__main__
```

Run tests

```shell script
python -m tests.test_hca_util
```

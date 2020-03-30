# __main__.py

import argparse
import os
import sys

from hca_util.settings import DEFAULT_PROFILE, DEBUG_MODE
from hca_util.common import is_valid_project_name, is_valid_area_name
from hca_util.hca_cmd import HcaCmd
from hca_util.bucket_policy import ALLOWED_PERMS, DEFAULT_PERMS


def valid_project_name(string):
    if not is_valid_project_name(string):
        msg = 'invalid - needs to be between 1-36 alphanumeric characters with no space'
        raise argparse.ArgumentTypeError(msg)
    return string


def valid_area(string):
    if not is_valid_area_name(string):
        msg = 'invalid - needs to be <uuid> or <uuid>/'
        raise argparse.ArgumentTypeError(msg)
    return string


def parse_args(args):
    parser = argparse.ArgumentParser(description='covid-util')

    cmd_parser = parser.add_subparsers(title='command', dest='command')
    cmd_parser.required = True

    parser_config = cmd_parser.add_parser('config', help='configure AWS credentials')
    parser_config.add_argument('ACCESS_KEY', help='AWS Access Key ID')
    parser_config.add_argument('SECRET_KEY', help='AWS Secret Access Key')
    parser_config.add_argument('--bucket', help='use BUCKET instead of default bucket')

    parser_create = cmd_parser.add_parser('create', help='create an upload area (authorised users only)')
    parser_create.add_argument('NAME', help='name for the new area', type=valid_project_name)
    parser_create.add_argument('-p', choices=ALLOWED_PERMS, default=DEFAULT_PERMS, help=f'allowed actions ('
                                                                                        f'permissions) on new '
                                                                                        f'area. u for upload, '
                                                                                        f'x for delete and d for '
                                                                                        f'download. Default is '
                                                                                        f'{DEFAULT_PERMS}')

    parser_select = cmd_parser.add_parser('select', help='select or show the active upload area')
    parser_select.add_argument('AREA', help='area uuid', type=valid_area, nargs='?')

    # cmd_parser.add_parser('dir', help='display active (selected) directory')

    # parser_clear = cmd_parser.add_parser('clear', help='clear current selection')
    # parser_clear.add_argument('-a', action='store_true', help='clear all - selection and known dirs')

    parser_list = cmd_parser.add_parser('list', help='list contents of the area')
    parser_list.add_argument('-b', action='store_true', help='list all areas in the S3 bucket (authorised users only)')

    parser_upload = cmd_parser.add_parser('upload', help='upload files to the area')
    group_upload = parser_upload.add_mutually_exclusive_group(required=True)

    group_upload.add_argument('-a', action='store_true', help='upload all files')
    group_upload.add_argument('-f', metavar='file', nargs='+',
                              help='upload specified file(s)', type=argparse.FileType('r'))
    parser_upload.add_argument('-o', action='store_true', help='overwrite files with same names')

    parser_download = cmd_parser.add_parser('download', help='download files from the area')
    group_download = parser_download.add_mutually_exclusive_group(required=True)

    group_download.add_argument('-a', action='store_true', help='download all files')
    group_download.add_argument('-f', metavar='file', nargs='+', help='download specified file(s) only')

    parser_delete = cmd_parser.add_parser('delete', help='delete files from the area')
    group_delete = parser_delete.add_mutually_exclusive_group(required=True)

    group_delete.add_argument('-a', action='store_true', help='delete all files from the area')
    group_delete.add_argument('-f', metavar='file', nargs='+', help='delete specified file(s) only')
    group_delete.add_argument('-d', action='store_true', help='delete upload area and contents (authorised users only)')

    ps = [parser]
    if DEBUG_MODE:
        ps = [parser, parser_config, parser_create, parser_select, parser_list, parser_upload, parser_download, parser_delete]

    for p in ps:
        p.add_argument(
            '--profile',
            help=f'use PROFILE instead of default \'{DEFAULT_PROFILE}\' profile',
            default=DEFAULT_PROFILE
        )

    # parser.add_argument(
    #     '--region',
    #     help=f'use REGION instead of default \'{DEFAULT_REGION}\' region',
    #     default=DEFAULT_REGION
    # )

    return parser.parse_args(args)


def main():
    try:
        parsed_args = parse_args(sys.argv[1:])
        HcaCmd(parsed_args)
    except KeyboardInterrupt:
        # If SIGINT is triggered whilst threads are active (upload/download) we kill the entire process to give the
        # user an instant exist, rather than have to hammer on ctrl+c multiple times with various obscure messages.
        #
        # However, os_.exit() is nasty because it allows the Python interpreter to do no cleanup
        # One alternative is to make our transfer threads daemon. However, there are then other non-daemon threads
        # employed by boto for the multi-part transfer. Here, configuring boto to only use the main thread for transfer
        # works but with unmeasured effects on transfer speed. Alternatively, it might be possible to call
        # boto3 client.abort_multipart_upload() but don't know for sure and in any case this requires more work to
        # keep hold of upload IDs, etc.
        #
        # So for now risking the kill though might want to revisit this decision.
        os._exit(0)

if __name__ == '__main__':
	main()

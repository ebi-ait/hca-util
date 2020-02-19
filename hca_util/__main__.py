# __main__.py

import argparse
from hca_util.hca_cmd import HcaCmd
from hca_util.aws import *


def main():
    parser = argparse.ArgumentParser(description='hca-util')
    parser.add_argument(
        '--profile',
        help=f'use PROFILE instead of default \'{Aws.DEFAULT_PROFILE}\' profile'
    )
    parser.add_argument(
        '--region',
        help=f'use REGION instead of default \'{Aws.DEFAULT_REGION}\' region'
    )
    args = parser.parse_args()
    HcaCmd(args).cmdloop()


if __name__ == '__main__':
    main()

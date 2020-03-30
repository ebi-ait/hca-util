import os
import sys
import unittest
from hca_util.__main__ import parse_args
from hca_util.hca_cmd import HcaCmd
from hca_util.command.config import CmdConfig
from hca_util.command.create import CmdCreate
from hca_util.command.select import CmdSelect
from hca_util.command.list import CmdList
from hca_util.command.area import CmdArea

# TODO: change language here wrangler -> admin, contributor -> user

contributor_profile = 'HCAContributor'
wrangler_profile = 'HCAWrangler'

contributor_access = os.environ['HCA_UTIL_CONTRIBUTOR_ACCESS']
contributor_secret = os.environ['HCA_UTIL_CONTRIBUTOR_SECRET']

wrangler_access = os.environ['HCA_UTIL_WRANGLER_ACCESS']
wrangler_secret = os.environ['HCA_UTIL_WRANGLER_SECRET']


class TestHcaUtil(unittest.TestCase):

    # test: contributor can't delete folder
    # test: don't repeat upload

    def test_cmd_config_invalid_creds(self):
        args = ['config', 'xyz', 'abc']
        success, msg = CmdConfig(parse_args(args)).run()
        self.assertFalse(success)
        self.assertEqual(msg, 'Invalid credentials')

    def test_cmd_config_valid_creds_contributor(self):
        self.valid_creds(contributor_access, contributor_secret, 'HCAContributor')

    def test_cmd_config_valid_creds_wrangler(self):
        self.valid_creds(wrangler_access, wrangler_secret, 'HCAWrangler')

    def valid_creds(self, access, secret, profile):
        args = ['config', access, secret, '--profile', profile]
        success, msg = CmdConfig(parse_args(args)).run()
        self.assertTrue(success)
        self.assertEqual(msg, 'Valid credentials')

    def test_cmd_clear(self):
        #args = ['clear']
        #HcaCmd(parse_args(args))
        #self.assertEqual(sys.stdout, 'Selection cleared\n')
        pass


    def test_cmd_select_noargs(self):
        pass

    def test_cmd_select_invalid(self):
        pass

    def test_cmd_select_valid_notexists(self):
        pass

    def test_cmd_select_valid_noperms(self):
        pass

    def test_cmd_select_valid_ok(self):
        pass

    # tests with contributor profile
    def test_one(self):
        pass

    # test - create (wrangler)
    dir_u = None
    dir_ud = None
    dir_ux = None
    dir_udx = None

    def test_create_dirs(self):
        """
        Test creating dir with all permission types:
        u  - upload only
        ud - upload and download
        ux - upload and delete
        udx - upload, download and delete
        :return:
        """
        pass

    def test_dirs_wrangler_access(self):
        self.dirs_access(wrangler_profile)

    def test_dirs_contributor_access(self):
        self.dirs_access(contributor_profile)

    def dirs_access(self, user):
        """
        Test user (contributor & wrangler) permissions to carry out command on folder with specified perms
                  - contributor -   -  wrangler   -
        cmd       u   ud  ux  udx   u   ud  ux  udx
        ---       -   --  --  ---   -   --  --  ---
        select    Y   Y   Y   Y     Y   Y   Y   Y
        list      Y   Y   Y   Y     Y   Y   Y   Y
        upload    Y   Y   Y   Y     Y   Y   Y   Y
        download  N   Y   N   Y     Y   Y   Y   Y
        delete    N   N   Y   Y     Y   Y   Y   Y

        5x8=40 total conditions
        :return:
        """
        pass

    def test_delete_folder(self):
        """
        Test to delete folder, also serves as clean up after test runs
        :return:
        """
        pass


if __name__ == '__main__':
    unittest.main()

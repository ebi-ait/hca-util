import unittest

from hca_util.hca_util import *


USER_CONTRIB = "HCAContributor"
USER_WRANGLER = "HCAWrangler"


class TestHcaUtil(unittest.TestCase):

    # tests with wrangler profile
    def test_setup_wrangler_profile(self):
        util = HcaUtil(profile='HCAWrangler')
        self.assertEqual(util.setup_ok, True)
        self.assertTrue(util.bucket_name)

    def test_setup_invalid_profile(self):
        util = HcaUtil(profile='invalid')
        self.assertEqual(util.setup_ok, False)
        self.assertFalse(util.bucket_name)

    def test_setup_default_profile(self):
        util = HcaUtil()
        self.assertEqual(util.setup_ok, True)
        self.assertTrue(util.bucket_name)

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
        self.dirs_access(USER_WRANGLER)

    def test_dirs_contributor_access(self):
        self.dirs_access(USER_CONTRIB)

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

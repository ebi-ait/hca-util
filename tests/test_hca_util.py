import unittest

from hca_util.hca_util import *


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


if __name__ == '__main__':
    unittest.main()

import os
import unittest

from hca_util.__main__ import parse_args
from hca_util.command.config import CmdConfig

user_profile = 'HCAContributor'
admin_profile = 'HCAWrangler'

user_access = os.environ.get('HCA_UTIL_USER_ACCESS')
user_secret = os.environ.get('HCA_UTIL_USER_SECRET')

admin_access = os.environ.get('HCA_UTIL_ADMIN_ACCESS')
admin_secret = os.environ.get('HCA_UTIL_ADMIN_SECRET')


class TestConfig(unittest.TestCase):
    def test_config_valid_user_creds(self):
        args = ['config', user_access, user_secret, '--profile', user_profile]
        success, msg = CmdConfig(parse_args(args)).run()
        self.assertEqual(msg, 'Valid credentials')
        self.assertTrue(success)

    def test_config_valid_admin_creds(self):
        args = ['config', admin_access, admin_secret, '--profile', admin_profile]
        success, msg = CmdConfig(parse_args(args)).run()
        self.assertTrue(success)
        self.assertEqual(msg, 'Valid credentials')

    def test_config_invalid_creds(self):
        args = ['config', 'invalid-key', 'invalid-secret']
        success, msg = CmdConfig(parse_args(args)).run()
        self.assertFalse(success)
        self.assertEqual(msg, 'Invalid credentials')

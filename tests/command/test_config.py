import os
import unittest

from util.__main__ import parse_args
from util.command.config import CmdConfig
from settings import IAM_USER, IAM_ADMIN


user_access = os.environ.get('USER_ACCESS')
user_secret = os.environ.get('USER_SECRET')

admin_access = os.environ.get('ADMIN_ACCESS')
admin_secret = os.environ.get('ADMIN_SECRET')


class TestConfig(unittest.TestCase):
    def test_config_valid_user_creds(self):
        args = ['config', user_access, user_secret, '--profile', IAM_USER]
        success, msg = CmdConfig(parse_args(args)).run()
        self.assertEqual(msg, 'Valid credentials')
        self.assertTrue(success)

    def test_config_valid_admin_creds(self):
        args = ['config', admin_access, admin_secret, '--profile', IAM_ADMIN]
        success, msg = CmdConfig(parse_args(args)).run()
        self.assertTrue(success)
        self.assertEqual(msg, 'Valid credentials')

    def test_config_invalid_creds(self):
        args = ['config', 'invalid-key', 'invalid-secret']
        success, msg = CmdConfig(parse_args(args)).run()
        self.assertFalse(success)
        self.assertEqual(msg, 'Invalid credentials')

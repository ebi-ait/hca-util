import os
import unittest
from unittest.mock import patch

from ait.commons.util.settings import COGNITO_MORPHIC_UTIL_USER, COGNITO_MORPHIC_UTIL_ADMIN
from ait.commons.util.__main__ import parse_args
from ait.commons.util.command.config import CmdConfig

user_access = os.environ.get('USER_ACCESS')
user_secret = os.environ.get('USER_SECRET')

admin_access = os.environ.get('ADMIN_ACCESS')
admin_secret = os.environ.get('ADMIN_SECRET')


class TestConfig(unittest.TestCase):
    def test_config_valid_user_creds(self):
        args = ['config', user_access, user_secret, '--profile', COGNITO_MORPHIC_UTIL_USER]
        success, msg = CmdConfig(parse_args(args)).run()
        self.assertEqual(msg, 'Valid credentials')
        self.assertTrue(success)

    def test_config_invalid_user_creds(self):
        args = ['config', 'invalid-key', 'invalid-secret', '--profile', COGNITO_MORPHIC_UTIL_USER]
        success, msg = CmdConfig(parse_args(args)).run()
        self.assertEqual(msg, 'Invalid credentials')
        self.assertFalse(success)

    def test_config_valid_admin_creds(self):
        args = ['config', admin_access, admin_secret, '--profile', COGNITO_MORPHIC_UTIL_ADMIN]
        success, msg = CmdConfig(parse_args(args)).run()
        self.assertTrue(success)
        self.assertEqual(msg, 'Valid credentials')

    def test_config_invalid_admin_creds(self):
        args = ['config', 'invalid-key', 'invalid-secret', '--profile', COGNITO_MORPHIC_UTIL_ADMIN]
        success, msg = CmdConfig(parse_args(args)).run()
        self.assertEqual(msg, 'Invalid credentials')
        self.assertFalse(success)

    def test_config_invalid_creds(self):
        args = ['config', 'invalid-key', 'invalid-secret']
        success, msg = CmdConfig(parse_args(args)).run()
        self.assertFalse(success)
        self.assertEqual(msg, 'Invalid credentials')

    def test_config_valid_user_creds(self):
        args = ['config', user_access, user_secret]
        success, msg = CmdConfig(parse_args(args)).run()
        self.assertTrue(success)
        self.assertEqual(msg, 'Valid credentials')

    def test_config_valid_admin_creds(self):
        args = ['config', admin_access, admin_secret]
        success, msg = CmdConfig(parse_args(args)).run()
        self.assertTrue(success)
        self.assertEqual(msg, 'Valid credentials for admin use')

    @patch('ait.commons.util.command.config.set_bucket')
    def test_config_with_bucket(self, set_bucket):
        args = ['config', user_access, user_secret, '--bucket', 'bucket']
        success, msg = CmdConfig(parse_args(args)).run()
        self.assertTrue(success)

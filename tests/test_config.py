import os
import subprocess
import unittest
from unittest.mock import MagicMock, Mock

from hca_util.hca_cmd import HcaCmd

from hca_util.__main__ import parse_args
from hca_util.command.config import CmdConfig
from hca_util.command.create import CmdCreate

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

    def test_create_upload_area_no_config(self):
        args = ['create', 'testUploadArea']
        success, msg = CmdCreate(None, parse_args(args)).run()
        self.assertFalse(success)
        self.assertEqual(msg, 'You need configure your profile first')

    def test_create_upload_area_has_valid_config_for_contributor(self):
        aws_mock = MagicMock()
        aws_mock.is_contributor = True
        # create upload area
        args = ['create', 'testUploadArea']
        success, msg = CmdCreate(aws_mock, parse_args(args)).run()
        self.assertFalse(success)
        self.assertEqual(msg, 'You don\'t have permission to use this command')

    def test_create_upload_area_has_valid_config_for_admin(self):
        aws_mock = MagicMock()
        session = MagicMock()
        client = MagicMock()
        resource = MagicMock()
        bucket_policy = MagicMock()

        client.put_object = Mock()
        resource.BucketPolicy = Mock(return_value=bucket_policy)
        bucket_policy.policy = None

        session.client = Mock(return_value=client)
        session.resource = Mock(return_value=resource)

        aws_mock.is_contributor = False
        aws_mock.common_session = session
        aws_mock.bucket_name = 'bucket-name'
        # create upload area
        args = ['create', 'testUploadArea']
        success, msg = CmdCreate(aws_mock, parse_args(args)).run()

        self.assertTrue(success)


    def test_select_valid(self):
        pass

    def test_select_invalid(self):
        pass

    def test_select_inexisting(self):
        pass

    def test_select_not_permitted(self):
        pass

    # tests with user profile
    def test_one(self):
        pass

    # test - create (admin)
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

    def test_dirs_admin_access(self):
        self.dirs_access(admin_profile)

    def test_dirs_user_access(self):
        self.dirs_access(user_profile)

    def dirs_access(self, user):
        """
        Test admin vs user permissions to carry out command on folder with specified perms
                  -  user  -          -  admin  -
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

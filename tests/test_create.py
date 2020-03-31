import unittest
from unittest.mock import MagicMock, Mock

from hca_util.__main__ import parse_args
from hca_util.command.create import CmdCreate


class TestCreate(unittest.TestCase):
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
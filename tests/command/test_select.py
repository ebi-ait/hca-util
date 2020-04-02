import unittest
from unittest.mock import MagicMock, Mock

from hca_util.__main__ import parse_args
from hca_util.command.select import CmdSelect


class TestSelect(unittest.TestCase):
    def setUp(self) -> None:
        self.aws_mock = MagicMock()

        self.client = MagicMock()
        self.client.put_object = Mock()

        bucket_policy = MagicMock()
        bucket_policy.policy = None

        resource = MagicMock()
        resource.BucketPolicy = Mock(return_value=bucket_policy)

        session = MagicMock()
        session.client = Mock(return_value=self.client)
        session.resource = Mock(return_value=resource)

        self.aws_mock.is_user = True
        self.aws_mock.common_session = session
        self.aws_mock.bucket_name = 'bucket-name'
        self.aws_mock.obj_exists = Mock(return_value=True)

        self.upload_area_uuid = '00000000-0000-0000-0000-000000000000'

    def test_select_upload_area_nonexisting(self):
        # given
        self.aws_mock.obj_exists = Mock(return_value=False)
        args = ['select', self.upload_area_uuid]

        # when
        success, msg = CmdSelect(self.aws_mock, parse_args(args)).run()

        # then
        self.assertFalse(success)
        self.assertEqual(msg, 'Upload area does not exist')

    def test_select_upload_area_existing(self):
        # given
        args = ['select', self.upload_area_uuid]

        # when
        success, msg = CmdSelect(self.aws_mock, parse_args(args)).run()

        # then
        self.assertTrue(success)
        self.assertEqual(msg, f'Selected upload area is {self.upload_area_uuid}/')

    def test_select_upload_area_no_area_given(self):
        # given
        CmdSelect(self.aws_mock, parse_args(['select', self.upload_area_uuid])).run()
        args = ['select']

        # when
        success, msg = CmdSelect(self.aws_mock, parse_args(args)).run()

        # then
        self.assertTrue(success)
        self.assertEqual(msg, f'Currently selected upload area is {self.upload_area_uuid}/')

    def test_select_upload_area_wrong_permissions(self):
        # given
        CmdSelect(self.aws_mock, parse_args(['select', self.upload_area_uuid])).run()
        args = ['select']

        # when
        success, msg = CmdSelect(self.aws_mock, parse_args(args)).run()

        # then
        self.assertTrue(success)
        self.assertEqual(msg, f'Currently selected upload area is {self.upload_area_uuid}/')

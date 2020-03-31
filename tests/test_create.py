import unittest
from unittest.mock import MagicMock, Mock, patch

from hca_util.hca_cmd import HcaCmd

from hca_util.__main__ import parse_args
from hca_util.command.create import CmdCreate


class TestCreate(unittest.TestCase):
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

        self.aws_mock.is_contributor = False
        self.aws_mock.common_session = session
        self.aws_mock.bucket_name = 'bucket-name'

    def test_create_upload_area_no_config(self):
        # given
        args = ['create', 'testUploadArea']

        # when
        success, msg = CmdCreate(None, parse_args(args)).run()

        # then
        self.assertFalse(success)
        self.assertEqual(msg, 'You need configure your profile first')

    def test_user_create_upload_area_has_valid_config(self):
        # given
        self.aws_mock.is_contributor = True

        args = ['create', 'testUploadArea']

        # when
        success, msg = CmdCreate(self.aws_mock, parse_args(args)).run()

        # then
        self.assertFalse(success)
        self.assertEqual(msg, 'You don\'t have permission to use this command')

    @patch('uuid.uuid4')
    def test_admin_create_upload_area(self, uuid):
        # given
        uuid.return_value = 'uuid'

        args = ['create', 'testUploadArea']

        # when
        success, msg = CmdCreate(self.aws_mock, parse_args(args)).run()

        # then
        self.assertTrue(success)

        metadata = {'name': 'testUploadArea', 'perms': 'ux'}
        self.client.put_object.assert_called_once_with(Bucket='bucket-name', Key='uuid/', Metadata=metadata)

    @patch('uuid.uuid4')
    def test_admin_create_upload_area_with_permissions(self, uuid):
        # given
        uuid.return_value = 'uuid'
        upload_area_name = 'testUploadArea'
        permission = 'udx'

        args = ['create', upload_area_name, '-p', permission]

        # when
        success, msg = CmdCreate(self.aws_mock, parse_args(args)).run()

        # then
        self.assertTrue(success)

        metadata = {'name': upload_area_name, 'perms': permission}
        self.client.put_object.assert_called_once_with(Bucket='bucket-name', Key='uuid/', Metadata=metadata)

    def test_admin_create_upload_area_no_name(self):
        # given
        args = ['create']

        # when
        with self.assertRaises(SystemExit) as error:
            parsed_args = parse_args(args)
            self.assertFalse(parsed_args)

        self.assertEqual(error.exception.code, 2)

    @patch('hca_util.aws_client.Aws')
    def test_create_upload_area_with_invalid_credentials(self, aws_mock):
        # given
        aws_mock.is_valid_credentials = False

        args = ['create', 'uploadArea']

        # when
        with self.assertRaises(SystemExit) as error:
            HcaCmd(parse_args(args))

        self.assertEqual(error.exception.code, 1)

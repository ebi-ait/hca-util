import unittest
from unittest.mock import MagicMock, Mock, patch

from ait.commons.util.__main__ import parse_args
from ait.commons.util.cmd import Cmd
from ait.commons.util.command.create import CmdCreate


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

        self.aws_mock.is_user = False
        self.aws_mock.common_session = session
        self.aws_mock.bucket_name = 'bucket-name'

    def test_create_upload_area_no_config_display_error(self):
        # given
        args = ['create', 'testUploadArea']

        # when
        success, msg = CmdCreate(None, parse_args(args)).run()

        # then
        self.assertFalse(success)
        self.assertEqual(msg, 'You need configure your profile first')

    def test_create_upload_area_no_config_exits_error(self):
        # given
        args = ['create', 'testUploadArea']

        # when
        with self.assertRaises(SystemExit) as error:
            Cmd(parse_args(args))

        # then
        self.assertEqual(error.exception.code, 1)

    def test_user_create_upload_area_has_valid_config(self):
        # given
        self.aws_mock.is_user = True

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

        tags = 'name=testUploadArea&perms=ux'
        self.client.put_object.assert_called_once_with(Bucket='bucket-name', Key='uuid/', Tagging=tags)

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

        tags = f'name={upload_area_name}&perms={permission}'
        self.client.put_object.assert_called_once_with(Bucket='bucket-name', Key='uuid/', Tagging=tags)

    def test_admin_create_upload_area_no_name(self):
        # given
        args = ['create']

        # when
        with self.assertRaises(SystemExit) as error:
            parsed_args = parse_args(args)
            success, msg = CmdCreate(self.aws_mock, parsed_args).run()
            self.assertFalse(parsed_args)
            self.assertFalse(success)
            self.assertFalse(msg)

        self.assertEqual(error.exception.code, 2)

    @patch('ait.commons.util.aws_client.Aws')
    def test_create_upload_area_with_invalid_credentials(self, aws_mock):
        # given
        aws_mock.is_valid_credentials = False

        args = ['create', 'uploadArea']

        # when
        with self.assertRaises(SystemExit) as error:
            Cmd(parse_args(args))

        # then
        self.assertEqual(error.exception.code, 1)

    @patch('uuid.uuid4')
    def test_admin_create_upload_area_has_exception(self, uuid):
        # given
        uuid.return_value = 'uuid'

        args = ['create', 'testUploadArea']
        self.client.put_object.side_effect = Mock(side_effect=Exception('Test'))

        # when
        success, msg = CmdCreate(self.aws_mock, parse_args(args)).run()

        # then
        self.assertFalse(success)

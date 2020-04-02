from unittest import TestCase
from unittest.mock import MagicMock, Mock, patch

from hca_util.__main__ import parse_args
from hca_util.command.upload import CmdUpload


class TestUpload(TestCase):
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

    def test_upload_inexisting_file(self):
        # given
        args = ['upload', 'inexisting-file.txt']

        # when
        with self.assertRaises(SystemExit) as error:
            parsed_args = parse_args(args)
            success, msg = CmdUpload(self.aws_mock, parsed_args)
            self.assertFalse(parsed_args)
            self.assertFalse(success)
            self.assertFalse(msg)

        self.assertEqual(error.exception.code, 2)

    @patch('hca_util.command.upload.get_selected_area')
    def test_upload_file_no_upload_area_selected(self, get_selected_area):
        # given
        get_selected_area.return_value = None
        args = MagicMock()

        # when
        success, msg = CmdUpload(self.aws_mock, args).run()

        # then
        self.assertFalse(success)
        self.assertEqual(msg, 'No area selected')

    @patch('hca_util.command.upload.get_selected_area')
    @patch('os.path.getsize')
    @patch('hca_util.command.upload.transfer')
    def test_upload_file_in_selected_upload_area(self, transfer, get_size, get_selected_area):
        # given
        get_selected_area.return_value = 'selected'
        get_size.return_value = 'size'

        args = MagicMock()
        args.PATH = ['filename']
        args.a = None

        # when
        success, msg = CmdUpload(self.aws_mock, args).run()
        # then
        self.assertTrue(success)
        transfer.assert_called_once()

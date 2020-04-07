from unittest import TestCase
from unittest.mock import patch, MagicMock, Mock

from util.command.download import CmdDownload


def mock_transfer(_, fs):
    for f in fs:
        f.successful = True
        f.complete = True


class TestDownload(TestCase):
    def setUp(self) -> None:
        self.aws_mock = MagicMock()

        self.client = MagicMock()
        self.client.put_object = Mock()

        bucket_policy = MagicMock()
        bucket_policy.policy = None

        bucket = Mock()
        bucket.upload_file = Mock()
        bucket.objects = Mock()
        self.bucket = bucket

        self.upload_file = bucket.upload_file
        self.download_file = bucket.download_file

        resource = MagicMock()
        resource.BucketPolicy = Mock(return_value=bucket_policy)
        resource.Bucket = Mock(return_value=bucket)

        session = MagicMock()
        session.client = Mock(return_value=self.client)
        session.resource = Mock(return_value=resource)

        self.aws_mock.is_user = False
        self.aws_mock.common_session = session
        self.aws_mock.bucket_name = 'bucket-name'
        self.aws_mock.new_session.return_value = session

    @patch('util.command.download.get_selected_area')
    def test_download_no_upload_area_selected(self, get_selected_area):
        # given
        get_selected_area.return_value = None
        args = MagicMock()

        # when
        success, msg = CmdDownload(self.aws_mock, args).run()

        # then
        self.assertFalse(success)
        self.assertEqual(msg, 'No area selected')

    @patch('util.command.download.get_selected_area')
    @patch('util.command.download.os')
    @patch('util.command.download.TransferProgress')
    def test_download_all_files_from_selected_upload_area(self, transfer_progress, os, get_selected_area):
        # given
        get_selected_area.return_value = 'selected'

        def mock_transfer_progress(f):
            f.successful = True
            f.complete = True

        transfer_progress.side_effect = mock_transfer_progress

        obj = Mock()
        obj.key = 'selected'

        obj2 = Mock()
        obj2.key = 'filename'
        obj2.size = 2

        obj3 = Mock()
        obj3.key = 'filename2'
        obj3.size = 2

        self.bucket.objects.filter.return_value = [obj, obj2, obj3]

        os.getcwd.return_value = 'cwd'

        args = MagicMock()
        args.a = True

        # when
        cmd = CmdDownload(self.aws_mock, args)
        success, msg = cmd.run()

        # then
        self.assertTrue(success)
        downloaded_files = [f.key for f in cmd.files]
        self.assertEqual(downloaded_files, ['filename', 'filename2'])
        self.assertEqual(self.download_file.call_count, 2, 'should download all files')

    @patch('util.command.download.get_selected_area')
    @patch('util.command.download.os')
    @patch('util.command.download.TransferProgress')
    def test_download_file_from_selected_upload_area(self, transfer_progress, os, get_selected_area):
        # given
        get_selected_area.return_value = 'selected/'

        def mock_transfer_progress(f):
            f.successful = True
            f.complete = True

        transfer_progress.side_effect = mock_transfer_progress

        obj = Mock()
        obj.key = 'selected/'

        obj2 = Mock()
        obj2.key = 'filename'
        obj2.size = 2

        obj3 = Mock()
        obj3.key = 'filename2'
        obj3.size = 2

        self.bucket.objects.filter.return_value = [obj, obj2, obj3]

        os.getcwd.return_value = 'cwd'

        args = MagicMock()
        args.a = False
        args.f = ['filename']

        # when
        cmd = CmdDownload(self.aws_mock, args)
        success, msg = cmd.run()

        # then
        self.assertTrue(success)
        downloaded_files = [f.key for f in cmd.files]
        self.assertEqual(downloaded_files, ['selected/filename'])
        self.assertEqual(self.download_file.call_count, 1, 'should download file')

    @patch('util.command.download.get_selected_area')
    @patch('util.command.download.os')
    @patch('util.command.download.TransferProgress')
    def test_download_empty_file_from_selected_upload_area(self, transfer_progress, os, get_selected_area):
        # given
        get_selected_area.return_value = 'selected'

        def mock_transfer_progress(f):
            f.successful = True
            f.complete = True

        transfer_progress.side_effect = mock_transfer_progress

        obj = Mock()
        obj.key = 'selected'

        obj2 = Mock()
        obj2.key = 'filename'
        obj2.size = 0
        self.bucket.objects.filter.return_value = [obj, obj2]

        os.getcwd.return_value = 'cwd'

        args = MagicMock()
        args.a = True

        # when
        cmd = CmdDownload(self.aws_mock, args)
        success, msg = cmd.run()

        # then
        self.assertTrue(success)
        downloaded_files = [f.key for f in cmd.files]
        self.assertEqual(downloaded_files, ['filename'])

        self.download_file.assert_called_once()


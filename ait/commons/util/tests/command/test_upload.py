from unittest import TestCase
from unittest.mock import MagicMock, Mock, patch

from ait.commons.util.__main__ import parse_args
from ait.commons.util.command.upload import CmdUpload
from ait.commons.util.settings import DIR_SUPPORT


def mock_transfer(_, fs):
    for f in fs:
        f.successful = True


class TestUpload(TestCase):
    def setUp(self) -> None:
        self.aws_mock = MagicMock()

        self.client = MagicMock()
        self.client.put_object = Mock()

        bucket_policy = MagicMock()
        bucket_policy.policy = None

        bucket = Mock()
        bucket.upload_file = Mock()
        self.upload_file = bucket.upload_file

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

        self.path_map = {
            'file0': {
                'isfile': True,
                'isdir': False,
                'getsize': 2
            },
            'dir1': {
                'isfile': False,
                'isdir': True,
                'listdir': ['file1', 'file2', '.file', '__file', 'dir2']
            },
            'dir1/file1': {
                'isfile': True,
                'isdir': False,
                'getsize': 10
            },
            'dir1/file2': {
                'isfile': True,
                'isdir': False,
                'getsize': 0
            },
            'dir1/dir2/file3': {
                'isfile': True,
                'isdir': False,
                'getsize': 5
            },
            'dir1/dir2': {
                'isfile': False,
                'isdir': True,
                'listdir': ['file3']
            }
        }

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

    @patch('ait.commons.util.command.upload.get_selected_area')
    def test_upload_file_no_upload_area_selected(self, get_selected_area):
        # given
        get_selected_area.return_value = None
        args = MagicMock()

        # when
        success, msg = CmdUpload(self.aws_mock, args).run()

        # then
        self.assertFalse(success)
        self.assertEqual(msg, 'No area selected')

    @patch('ait.commons.util.command.upload.get_selected_area')
    @patch('ait.commons.util.command.upload.os.path')
    @patch('ait.commons.util.command.upload.transfer')
    def test_upload_file_to_selected_upload_area(self, transfer, os_path, get_selected_area):
        # given
        get_selected_area.return_value = 'selected'

        os_path.get_size.return_value = 'size'
        os_path.isfile.return_value = True
        os_path.isdir.return_value = False
        os_path.basename.return_value = 'filename'
        os_path.abspath = lambda path: 'abs' + path

        transfer.side_effect = mock_transfer

        args = MagicMock()
        args.PATH = ['filename']

        # when
        cmd = CmdUpload(self.aws_mock, args)
        success, msg = cmd.run()

        # then
        self.assertTrue(success)
        transfer.assert_called_once()
        uploaded_files = [f.path for f in cmd.files]
        self.assertEqual(uploaded_files, ['absfilename'])

    @patch('ait.commons.util.command.upload.get_selected_area')
    @patch('ait.commons.util.command.upload.os.path')
    @patch('ait.commons.util.command.upload.transfer')
    def test_upload_file_to_selected_upload_area_duplicate_path(self, transfer, os_path, get_selected_area):
        # given
        get_selected_area.return_value = 'selected'

        os_path.get_size.return_value = 'size'
        os_path.isfile.return_value = True
        os_path.isdir.return_value = False
        os_path.basename.return_value = 'filename'
        os_path.abspath = lambda path: 'abs' + path

        transfer.side_effect = mock_transfer

        args = MagicMock()
        args.PATH = ['filename', 'filename']

        # when
        cmd = CmdUpload(self.aws_mock, args)
        success, msg = cmd.run()

        # then
        self.assertTrue(success)
        transfer.assert_called_once()
        uploaded_files = [f.path for f in cmd.files]
        self.assertEqual(uploaded_files, ['absfilename'])

    @patch('ait.commons.util.command.upload.get_selected_area')
    @patch('ait.commons.util.command.upload.os')
    @patch('ait.commons.util.command.upload.transfer')
    def test_upload_dir_to_selected_upload_area(self, transfer, os, get_selected_area):
        # given
        get_selected_area.return_value = 'selected'
        path_map = self.path_map

        os.path.getsize = lambda path: path_map[path].get('getsize')
        os.path.isfile = lambda path: path_map[path].get('isfile')
        os.path.isdir = lambda path: path_map[path].get('isdir')
        os.path.abspath = lambda path: path
        os.path.join = lambda path, file: f'{path}/{file}'

        os.listdir = lambda path: path_map[path].get('listdir')

        transfer.side_effect = mock_transfer

        args = Mock()
        args.PATH = ['dir1']
        args.r = None

        # when
        cmd = CmdUpload(self.aws_mock, args)
        success, msg = cmd.run()

        # then
        self.assertTrue(success)
        transfer.assert_called_once()
        uploaded_files = [f.path for f in cmd.files]
        self.assertEqual(uploaded_files, ['dir1/file1', 'dir1/file2'])

    @patch('ait.commons.util.command.upload.get_selected_area')
    @patch('ait.commons.util.command.upload.os')
    @patch('ait.commons.util.command.upload.transfer')
    def test_upload_dir_to_selected_upload_area_recursive(self, transfer, os, get_selected_area):
        # given
        get_selected_area.return_value = 'selected'
        path_map = self.path_map

        os.path.getsize = lambda path: path_map[path].get('getsize')
        os.path.isfile = lambda path: path_map[path].get('isfile')
        os.path.isdir = lambda path: path_map[path].get('isdir')
        os.path.abspath = lambda path: path
        os.path.join = lambda path, file: f'{path}/{file}'

        os.listdir = lambda path: path_map[path].get('listdir')

        transfer.side_effect = mock_transfer

        args = Mock()
        args.PATH = ['dir1']
        args.a = None
        args.r = True

        # when
        cmd = CmdUpload(self.aws_mock, args)
        success, msg = cmd.run()

        # then
        self.assertTrue(success)
        transfer.assert_called_once()
        uploaded_files = [f.path for f in cmd.files]
        expected_files = ['dir1/file1', 'dir1/file2', 'dir1/dir2/file3'] if DIR_SUPPORT else ['dir1/file1', 'dir1/file2']
        self.assertEqual(uploaded_files, expected_files)

    @patch('ait.commons.util.command.upload.get_selected_area')
    @patch('ait.commons.util.command.upload.os')
    @patch('ait.commons.util.command.upload.transfer')
    def test_upload_dir_to_selected_upload_area_recursive_one_file_failure(self, transfer, os, get_selected_area):
        # given
        get_selected_area.return_value = 'selected'
        path_map = self.path_map

        os.path.getsize = lambda path: path_map[path].get('getsize')
        os.path.isfile = lambda path: path_map[path].get('isfile')
        os.path.isdir = lambda path: path_map[path].get('isdir')
        os.path.abspath = lambda path: path
        os.path.join = lambda path, file: f'{path}/{file}'

        os.listdir = lambda path: path_map[path].get('listdir')

        def mock_transfer_with_failure(_, fs):
            failed_file = ['dir1/file1']
            for f in fs:
                if f.path not in failed_file:
                    f.successful = True

        transfer.side_effect = mock_transfer_with_failure

        args = Mock()
        args.PATH = ['dir1']
        args.a = None
        args.r = True

        # when
        cmd = CmdUpload(self.aws_mock, args)
        success, msg = cmd.run()

        # then
        self.assertFalse(success)
        transfer.assert_called_once()
        uploaded_files = [f.path for f in cmd.files]
        expected_files = ['dir1/file2', 'dir1/dir2/file3'] if DIR_SUPPORT else ['dir1/file2']

        self.assertEqual(uploaded_files, expected_files)

    @patch('ait.commons.util.command.upload.get_selected_area')
    @patch('ait.commons.util.command.upload.os')
    @patch('ait.commons.util.command.upload.TransferProgress')
    def test_upload_dir_to_selected_upload_area_no_overwrite(self, transfer_progress, os, get_selected_area):
        # given
        get_selected_area.return_value = 'selected/'
        path_map = self.path_map

        os.path.getsize = lambda path: path_map[path].get('getsize')
        os.path.isfile = lambda path: path_map[path].get('isfile')
        os.path.isdir = lambda path: path_map[path].get('isdir')
        os.path.abspath = lambda path: path
        os.path.join = lambda path, file: f'{path}/{file}'

        os.listdir = lambda path: path_map[path].get('listdir')

        def mock_file_transfer(f):
            f.successful = True
            f.complete = True

        transfer_progress.side_effect = mock_file_transfer

        args = Mock()
        args.PATH = ['dir1']
        args.r = True
        args.o = False

        existing_key_map = {
            'selected/file1': True,
            'selected/file2': False,
            'selected/file3': False
        }

        self.aws_mock.obj_exists = lambda key: existing_key_map.get(key, False)

        # when
        cmd = CmdUpload(self.aws_mock, args)
        success, msg = cmd.run()

        # then
        self.assertTrue(success)

        uploaded_files_map = {}
        for f in cmd.files:
            uploaded_files_map[f.path] = f

        expected_files = ['dir1/file1', 'dir1/file2', 'dir1/dir2/file3'] if DIR_SUPPORT else ['dir1/file1', 'dir1/file2']
        expected_count = 2 if DIR_SUPPORT else 1

        self.assertEqual(list(uploaded_files_map.keys()), expected_files)
        self.assertEqual(self.upload_file.call_count, expected_count, 'Should not overwrite files')

    @patch('ait.commons.util.command.upload.get_selected_area')
    @patch('ait.commons.util.command.upload.os')
    @patch('ait.commons.util.command.upload.TransferProgress')
    def test_upload_dir_to_selected_upload_area_with_overwrite(self, transfer_progress, os, get_selected_area):
        # given
        get_selected_area.return_value = 'selected/'
        path_map = self.path_map

        os.path.getsize = lambda path: path_map[path].get('getsize')
        os.path.isfile = lambda path: path_map[path].get('isfile')
        os.path.isdir = lambda path: path_map[path].get('isdir')
        os.path.abspath = lambda path: path
        os.path.join = lambda path, file: f'{path}/{file}'

        os.listdir = lambda path: path_map[path].get('listdir')

        def mock_file_transfer(f):
            f.successful = True
            f.complete = True

        transfer_progress.side_effect = mock_file_transfer

        args = Mock()
        args.PATH = ['dir1']
        args.r = True
        args.o = True

        existing_key_map = {
            'selected/file1': True,
            'selected/file2': False,
            'selected/file3': False
        }

        self.aws_mock.obj_exists = lambda key: existing_key_map.get(key, False)

        # when
        cmd = CmdUpload(self.aws_mock, args)
        success, msg = cmd.run()

        # then
        self.assertTrue(success)

        uploaded_files_map = {}
        for f in cmd.files:
            uploaded_files_map[f.path] = f
        expected_files = ['dir1/file1', 'dir1/file2', 'dir1/dir2/file3'] if DIR_SUPPORT else ['dir1/file1', 'dir1/file2']
        expected_count = 3 if DIR_SUPPORT else 2
        self.assertEqual(list(uploaded_files_map.keys()), expected_files)
        self.assertEqual(self.upload_file.call_count, expected_count, 'Should overwrite files')

    @patch('ait.commons.util.command.upload.get_selected_area')
    @patch('ait.commons.util.command.upload.os')
    @patch('ait.commons.util.command.upload.TransferProgress')
    def test_upload_file_to_selected_upload_area_no_overwrite(self, transfer_progress, os, get_selected_area):
        # given
        get_selected_area.return_value = 'selected/'
        path_map = self.path_map

        os.path.getsize = lambda path: path_map[path].get('getsize')
        os.path.isfile = lambda path: path_map[path].get('isfile')
        os.path.isdir = lambda path: path_map[path].get('isdir')
        os.path.abspath = lambda path: path
        os.path.join = lambda path, file: f'{path}/{file}'

        os.path.basename.return_value = 'file0'

        os.listdir = lambda path: path_map[path].get('listdir')

        def mock_transfer_progress(f):
            f.successful = True
            f.complete = True

        transfer_progress.side_effect = mock_transfer_progress

        args = Mock()
        args.PATH = ['file0']
        args.r = True
        args.o = False

        existing_key_map = {
            'selected/file0': True
        }

        self.aws_mock.obj_exists = lambda key: existing_key_map.get(key, False)

        # when
        cmd = CmdUpload(self.aws_mock, args)
        success, msg = cmd.run()

        # then
        self.assertTrue(success)

        uploaded_files_map = {}
        for f in cmd.files:
            uploaded_files_map[f.path] = f

        self.assertEqual(list(uploaded_files_map.keys()), ['file0'])
        self.assertEqual(self.upload_file.call_count, 0, 'Should not overwrite files')

    @patch('ait.commons.util.command.upload.get_selected_area')
    @patch('ait.commons.util.command.upload.os')
    @patch('ait.commons.util.command.upload.TransferProgress')
    def test_upload_file_to_selected_upload_area_with_overwrite(self, transfer_progress, os, get_selected_area):
        # given
        get_selected_area.return_value = 'selected/'
        path_map = self.path_map

        os.path.getsize = lambda path: path_map[path].get('getsize')
        os.path.isfile = lambda path: path_map[path].get('isfile')
        os.path.isdir = lambda path: path_map[path].get('isdir')
        os.path.abspath = lambda path: path
        os.path.join = lambda path, file: f'{path}/{file}'

        os.path.basename.return_value = 'file0'

        os.listdir = lambda path: path_map[path].get('listdir')

        def mock_transfer_progress(f):
            f.successful = True
            f.complete = True

        transfer_progress.side_effect = mock_transfer_progress

        args = Mock()
        args.PATH = ['file0']
        args.r = True
        args.o = True

        existing_key_map = {
            'selected/file0': True
        }

        self.aws_mock.obj_exists = lambda key: existing_key_map.get(key, False)

        # when
        cmd = CmdUpload(self.aws_mock, args)
        success, msg = cmd.run()

        # then
        self.assertTrue(success)

        uploaded_files_map = {}
        for f in cmd.files:
            uploaded_files_map[f.path] = f

        self.assertEqual(list(uploaded_files_map.keys()), ['file0'])
        self.assertEqual(self.upload_file.call_count, 1, 'Should overwrite files')

    @patch('ait.commons.util.command.upload.get_selected_area')
    @patch('ait.commons.util.command.upload.os')
    @patch('ait.commons.util.command.upload.TransferProgress')
    def test_upload_file_to_selected_upload_area_with_exception(self, transfer_progress, os, get_selected_area):
        # given
        get_selected_area.return_value = 'selected/'
        path_map = self.path_map

        os.path.getsize = lambda path: path_map[path].get('getsize')
        os.path.isfile = lambda path: path_map[path].get('isfile')
        os.path.isdir = lambda path: path_map[path].get('isdir')
        os.path.abspath = lambda path: path
        os.path.join = lambda path, file: f'{path}/{file}'

        os.path.basename.return_value = 'file0'

        os.listdir = lambda path: path_map[path].get('listdir')

        def mock_transfer_progress(f):
            f.successful = True
            f.complete = True

        transfer_progress.side_effect = mock_transfer_progress
        self.upload_file.side_effect = Mock(side_effect=Exception('Test'))

        args = Mock()
        args.PATH = ['file0']
        args.r = True
        args.o = False

        existing_key_map = {
            'selected/file0': False
        }

        self.aws_mock.obj_exists = lambda key: existing_key_map.get(key, False)

        # when
        cmd = CmdUpload(self.aws_mock, args)
        success, msg = cmd.run()

        # then
        self.assertFalse(success)

        uploaded_files_map = {}
        for f in cmd.files:
            uploaded_files_map[f.path] = f

        self.assertEqual(list(uploaded_files_map.keys()), [])

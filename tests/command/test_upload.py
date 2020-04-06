from unittest import TestCase
from unittest.mock import MagicMock, Mock, patch

from util.__main__ import parse_args
from util.command.upload import CmdUpload


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

    @patch('util.command.upload.get_selected_area')
    def test_upload_file_no_upload_area_selected(self, get_selected_area):
        # given
        get_selected_area.return_value = None
        args = MagicMock()

        # when
        success, msg = CmdUpload(self.aws_mock, args).run()

        # then
        self.assertFalse(success)
        self.assertEqual(msg, 'No area selected')

    @patch('util.command.upload.get_selected_area')
    @patch('util.command.upload.os.path')
    @patch('util.command.upload.transfer')
    def test_upload_file_in_selected_upload_area(self, transfer, os_path, get_selected_area):
        # given
        get_selected_area.return_value = 'selected'

        os_path.get_size.return_value = 'size'
        os_path.isfile.return_value = True
        os_path.isdir.return_value = False
        os_path.basename.return_value = 'filename'
        os_path.abspath = lambda path: 'abs' + path

        args = MagicMock()
        args.PATH = ['filename']
        args.a = None

        # when
        cmd = CmdUpload(self.aws_mock, args)
        success, msg = cmd.run()

        # then
        self.assertTrue(success)
        transfer.assert_called_once()
        uploaded_files = [f.path for f in cmd.files]
        self.assertEqual(uploaded_files, ['absfilename'])

    @patch('util.command.upload.get_selected_area')
    @patch('util.command.upload.os')
    @patch('util.command.upload.transfer')
    def test_upload_dir_in_selected_upload_area(self, transfer, os, get_selected_area):
        # given
        get_selected_area.return_value = 'selected'
        path_map = {
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
                'getsize': 5
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
        os.path.getsize = lambda path: path_map[path].get('getsize')
        os.path.isfile = lambda path: path_map[path].get('isfile')
        os.path.isdir = lambda path: path_map[path].get('isdir')
        os.path.abspath = lambda path: path
        os.path.join = lambda path, file: f'{path}/{file}'

        os.listdir = lambda path: path_map[path].get('listdir')

        args = Mock()
        args.PATH = ['dir1']
        args.a = None
        args.r = None

        # when
        cmd = CmdUpload(self.aws_mock, args)
        success, msg = cmd.run()

        # then
        self.assertTrue(success)
        transfer.assert_called_once()
        uploaded_files = [f.path for f in cmd.files]
        self.assertEqual(uploaded_files, ['dir1/file1', 'dir1/file2'])

    @patch('util.command.upload.get_selected_area')
    @patch('util.command.upload.os')
    @patch('util.command.upload.transfer')
    def test_upload_dir_in_selected_upload_area_recursive(self, transfer, os, get_selected_area):
        # given
        get_selected_area.return_value = 'selected'
        path_map = {
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
                'getsize': 5
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
        os.path.getsize = lambda path: path_map[path].get('getsize')
        os.path.isfile = lambda path: path_map[path].get('isfile')
        os.path.isdir = lambda path: path_map[path].get('isdir')
        os.path.abspath = lambda path: path
        os.path.join = lambda path, file: f'{path}/{file}'

        os.listdir = lambda path: path_map[path].get('listdir')

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
        self.assertEqual(uploaded_files, ['dir1/file1', 'dir1/file2', 'dir1/dir2/file3'])

from os.path import basename
from unittest import TestCase
from unittest.mock import MagicMock, Mock, patch

from ait.commons.util.__main__ import parse_args
from ait.commons.util.command.upload import CmdUpload
from ait.commons.util.settings import DIR_SUPPORT


class TestUpload(TestCase):
    def setUp(self) -> None:
        self.uploaded_files = []
        self.aws_mock = MagicMock()

        self.client = MagicMock()
        self.client.put_object = Mock()

        bucket_policy = MagicMock()
        bucket_policy.policy = None

        bucket = Mock()
        bucket.upload_file = Mock()
        self.upload_file = bucket.upload_file
        self.upload_file.side_effect = self.mock_transfer

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
                'listdir': ['file1', 'file2', 'empty', '.file', '__file', 'dir2']
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
            'dir1/empty': {
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

    def mock_transfer(self, **kwargs):
        if 'Filename' in kwargs:
            filename = kwargs.get('Filename')
            self.uploaded_files.append(filename)
            print(f'Uploaded {filename}')

    @staticmethod
    def patch_os_using_path_map(os, path_map):
        os.path.getsize = lambda path: path_map[path].get('getsize')
        os.path.isfile = lambda path: path_map[path].get('isfile')
        os.path.isdir = lambda path: path_map[path].get('isdir')
        os.path.abspath = lambda path: path
        os.path.join = lambda path, file: f'{path}/{file}'
        os.path.basename = lambda path: basename(path)
        os.listdir = lambda path: path_map[path].get('listdir')

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
    @patch('ait.commons.util.command.upload.os')
    @patch('ait.commons.util.command.upload.filetype.guess')
    def test_upload_file_to_selected_upload_area(self, filetype, os, get_selected_area):
        # given
        get_selected_area.return_value = 'selected'
        filetype.return_value = None
        self.patch_os_using_path_map(os, self.path_map)

        args = MagicMock()
        args.PATH = ['dir1/dir2']

        # when
        cmd = CmdUpload(self.aws_mock, args)
        success, msg = cmd.run()

        # then
        self.assertTrue(success)
        self.assertEqual(['dir1/dir2/file3'], self.uploaded_files)

    @patch('ait.commons.util.command.upload.get_selected_area')
    @patch('ait.commons.util.command.upload.os')
    @patch('ait.commons.util.command.upload.filetype.guess')
    def test_upload_file_to_selected_upload_area_duplicate_path(self, filetype, os, get_selected_area):
        # given
        get_selected_area.return_value = 'selected'
        filetype.return_value = None
        self.patch_os_using_path_map(os, self.path_map)

        args = MagicMock()
        args.PATH = ['file0', 'file0']

        # when
        cmd = CmdUpload(self.aws_mock, args)
        success, msg = cmd.run()

        # then
        self.assertTrue(success)
        self.assertEqual(['file0'], self.uploaded_files)

    @patch('ait.commons.util.command.upload.get_selected_area')
    @patch('ait.commons.util.command.upload.os')
    @patch('ait.commons.util.command.upload.filetype.guess')
    def test_upload_dir_to_selected_upload_area(self, filetype, os, get_selected_area):
        # given
        get_selected_area.return_value = 'selected'
        filetype.return_value = None
        self.patch_os_using_path_map(os, self.path_map)

        args = Mock()
        args.PATH = ['dir1']
        args.r = None

        # when
        cmd = CmdUpload(self.aws_mock, args)
        success, msg = cmd.run()

        # then
        self.assertTrue(success)
        self.assertEqual(['dir1/file1', 'dir1/file2'], self.uploaded_files)

    @patch('ait.commons.util.command.upload.get_selected_area')
    @patch('ait.commons.util.command.upload.os')
    @patch('ait.commons.util.command.upload.filetype.guess')
    def test_upload_dir_to_selected_upload_area_recursive(self, filetype, os, get_selected_area):
        # given
        get_selected_area.return_value = 'selected'
        filetype.return_value = None
        self.patch_os_using_path_map(os, self.path_map)

        args = Mock()
        args.PATH = ['dir1']
        args.a = None
        args.r = True

        # when
        cmd = CmdUpload(self.aws_mock, args)
        success, msg = cmd.run()

        # then
        self.assertTrue(success)
        expected_files = ['dir1/file1', 'dir1/file2', 'dir1/dir2/file3'] if DIR_SUPPORT else ['dir1/file1', 'dir1/file2']
        self.assertEqual(expected_files, self.uploaded_files)

    @patch('ait.commons.util.command.upload.get_selected_area')
    @patch('ait.commons.util.command.upload.os')
    @patch('ait.commons.util.command.upload.filetype.guess')
    def test_upload_dir_to_selected_upload_area_recursive_one_file_failure(self, filetype, os, get_selected_area):
        # given
        get_selected_area.return_value = 'selected'
        filetype.return_value = None
        self.patch_os_using_path_map(os, self.path_map)
        failed_files = ['dir1/file1']

        def mock_transfer_with_failure(**kwargs):
            if 'Filename' in kwargs:
                filename = kwargs.get('Filename')
                if filename in failed_files:
                    raise Exception('File Failed to upload')
                else:
                    self.uploaded_files.append(filename)
                    print(f'Uploaded {filename}')

        self.upload_file.side_effect = mock_transfer_with_failure

        args = Mock()
        args.PATH = ['dir1']
        args.a = None
        args.r = True

        # when
        cmd = CmdUpload(self.aws_mock, args)
        success, msg = cmd.run()

        # then
        self.assertFalse(success)
        expected_files = ['dir1/file2', 'dir1/dir2/file3'] if DIR_SUPPORT else ['dir1/file2']
        self.assertEqual(expected_files, self.uploaded_files)

    @patch('ait.commons.util.command.upload.get_selected_area')
    @patch('ait.commons.util.command.upload.os')
    @patch('ait.commons.util.command.upload.filetype.guess')
    def test_upload_dir_to_selected_upload_area_no_overwrite(self, filetype, os, get_selected_area):
        # given
        get_selected_area.return_value = 'selected/'
        filetype.return_value = None
        self.patch_os_using_path_map(os, self.path_map)

        self.upload_file.side_effect = self.mock_transfer

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
        expected_files = ['dir1/file2', 'dir1/dir2/file3'] if DIR_SUPPORT else ['dir1/file2']
        expected_count = 2 if DIR_SUPPORT else 1
        self.assertEqual(expected_files, self.uploaded_files)
        self.assertEqual(expected_count, self.upload_file.call_count, 'Should not overwrite files')

    @patch('ait.commons.util.command.upload.get_selected_area')
    @patch('ait.commons.util.command.upload.os')
    @patch('ait.commons.util.command.upload.filetype.guess')
    def test_upload_dir_to_selected_upload_area_with_overwrite(self, filetype, os, get_selected_area):
        # given
        get_selected_area.return_value = 'selected/'
        filetype.return_value = None
        self.patch_os_using_path_map(os, self.path_map)

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
        expected_files = ['dir1/file1', 'dir1/file2', 'dir1/dir2/file3'] if DIR_SUPPORT else ['dir1/file1', 'dir1/file2']
        expected_count = 3 if DIR_SUPPORT else 2
        self.assertEqual(expected_files, self.uploaded_files)
        self.assertEqual(expected_count, self.upload_file.call_count, 'Should overwrite files')

    @patch('ait.commons.util.command.upload.get_selected_area')
    @patch('ait.commons.util.command.upload.os')
    @patch('ait.commons.util.command.upload.filetype.guess')
    def test_upload_file_to_selected_upload_area_no_overwrite(self, filetype, os, get_selected_area):
        # given
        get_selected_area.return_value = 'selected/'
        filetype.return_value = None
        self.patch_os_using_path_map(os, self.path_map)

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

        self.assertEqual([], self.uploaded_files)
        self.upload_file.assert_not_called()

    @patch('ait.commons.util.command.upload.get_selected_area')
    @patch('ait.commons.util.command.upload.os')
    @patch('ait.commons.util.command.upload.filetype.guess')
    def test_upload_file_to_selected_upload_area_with_overwrite(self, filetype, os, get_selected_area):
        # given
        get_selected_area.return_value = 'selected/'
        filetype.return_value = None
        self.patch_os_using_path_map(os, self.path_map)

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
        self.assertEqual(['file0'], self.uploaded_files)
        self.upload_file.assert_called_once()

    @patch('ait.commons.util.command.upload.get_selected_area')
    @patch('ait.commons.util.command.upload.os')
    @patch('ait.commons.util.command.upload.filetype.guess')
    def test_upload_file_to_selected_upload_area_with_exception(self, filetype, os, get_selected_area):
        # given
        get_selected_area.return_value = 'selected/'
        filetype.return_value = None
        self.patch_os_using_path_map(os, self.path_map)
        self.upload_file.side_effect = Mock(side_effect=Exception('Test'))

        args = Mock()
        args.PATH = ['file0']
        args.r = True
        args.o = False

        self.aws_mock.obj_exists.return_value = False

        # when
        cmd = CmdUpload(self.aws_mock, args)
        success, msg = cmd.run()

        # then
        self.assertFalse(success)
        self.upload_file.assert_called_once()

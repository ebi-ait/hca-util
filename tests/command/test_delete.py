import unittest
from unittest.mock import MagicMock, Mock, patch
from io import StringIO

from util.command.delete import CmdDelete


class MyTestCase(unittest.TestCase):
    @patch("util.command.delete.CmdDelete.clear_area_perms_from_bucket_policy")
    @patch("util.command.delete.CmdDelete.all_keys")
    @patch("util.command.delete.get_selected_area")
    def test_admin_delete_existing_files_and_dirs(self, mock_selected_area, mock_all_keys, mock_clear_area_perms):
        mock_area = "mock-area/"
        mock_files_to_delete = ["mock-file-1", "mock-file-2", "mock-dir-1"]
        mock_files_in_area = ["mock-file-1", "mock-file-2", "mock-file-3", "mock-dir-1/mock-file-4",
                              "mock-dir-1/mock-file-5", "mock-dir-2/mock-file-6"]
        mock_args = Mock()
        mock_args.d = False
        mock_args.a = False
        mock_args.PATH = mock_files_to_delete
        mock_aws = MagicMock()
        mock_aws.is_contributor = False

        mock_selected_area.return_value = mock_area
        mock_all_keys.side_effect = lambda prefix: list(
            filter(lambda k: k.startswith(prefix), map(lambda f: mock_area + f, mock_files_in_area))
        )

        mock_clear_area_perms.return_value = None
        cmd_delete = CmdDelete(mock_aws, mock_args)

        with patch("builtins.input", return_value="Y"), patch('sys.stdout', new=StringIO()) as cmd_output:
            cmd_delete.run()
            cmd_output_lines = cmd_output.getvalue().split("\n")
            self.assertTrue("Deleting" in cmd_output_lines[0])
            self.assertTrue("mock-file-1" in cmd_output_lines[1] and "not found" not in cmd_output_lines[1])
            self.assertTrue("mock-file-2" in cmd_output_lines[2] and "not found" not in cmd_output_lines[2])
            self.assertTrue("mock-file-4" in cmd_output_lines[3] and "not found" not in cmd_output_lines[3])
            self.assertTrue("mock-file-5" in cmd_output_lines[4] and "not found" not in cmd_output_lines[4])

            for line in cmd_output_lines:
                self.assertTrue("mock-file-3" not in line and "mock-file-6" not in line)

    @patch("util.command.delete.CmdDelete.all_keys")
    @patch("util.command.delete.get_selected_area")
    def test_admin_delete_non_existent_file_and_dir(self, mock_selected_area, mock_all_keys):
        mock_area = "mock-area/"
        mock_files_to_delete = ["non-existent-file-1", "mock-dir-1/non-existent-file-2", "mock-dir-2/non-existent-subdir-1/"]
        mock_files_in_area = ["mock-file-1", "mock-file-2", "mock-file-3", "mock-dir-1/mock-file-4",
                              "mock-dir-1/mock-file-5", "mock-dir-2/mock-file-6"]
        mock_args = Mock()
        mock_args.d = False
        mock_args.a = False
        mock_args.PATH = mock_files_to_delete
        mock_aws = MagicMock()
        mock_aws.is_contributor = False

        mock_selected_area.return_value = mock_area
        mock_all_keys.side_effect = lambda prefix: list(
            filter(lambda k: k.startswith(prefix), map(lambda f: mock_area + f, mock_files_in_area))
        )

        cmd_delete = CmdDelete(mock_aws, mock_args)

        with patch("builtins.input", return_value="Y"), patch('sys.stdout', new=StringIO()) as cmd_output:
            cmd_delete.run()
            cmd_output_lines = cmd_output.getvalue().split("\n")
            self.assertTrue("Deleting" in cmd_output_lines[0])
            self.assertTrue("non-existent-file-1" in cmd_output_lines[1] and "not found" in cmd_output_lines[1])
            self.assertTrue("non-existent-file-2" in cmd_output_lines[2] and "not found" in cmd_output_lines[2])
            self.assertTrue("non-existent-subdir-1" in cmd_output_lines[3] and "not found" in cmd_output_lines[3])

    @patch("util.command.delete.CmdDelete.clear_area_perms_from_bucket_policy")
    @patch("util.command.delete.CmdDelete.delete_upload_area")
    @patch("util.command.delete.get_selected_area")
    def test_admin_delete_all_files(self, mock_selected_area, mock_delete_upload_area, mock_clear_area_perms):
        mock_area = "mock-area"
        mock_files_to_delete = ["mock-file-1", "mock-file-2", "mock-file-3"]
        mock_args = Mock()
        mock_args.d = False
        mock_args.a = True
        mock_aws = MagicMock()
        mock_aws.is_contributor = False

        mock_selected_area.return_value = "mock-area"
        mock_delete_upload_area.return_value = list(map(lambda file: f'{mock_area}/{file}', mock_files_to_delete))
        mock_clear_area_perms.return_value = None
        cmd_delete = CmdDelete(mock_aws, mock_args)

        with patch("builtins.input", return_value="Y"), patch('sys.stdout', new=StringIO()) as cmd_output:
            cmd_delete.run()
            cmd_output_lines = cmd_output.getvalue().split("\n")
            self.assertTrue("Deleting" in cmd_output_lines[0])
            self.assertTrue("mock-file-1" in cmd_output_lines[1])
            self.assertTrue("mock-file-2" in cmd_output_lines[2])

    @patch("util.command.delete.CmdDelete.clear_area_perms_from_bucket_policy")
    @patch("util.command.delete.CmdDelete.delete_upload_area")
    @patch("util.command.delete.get_selected_area")
    def test_admin_delete_area(self, mock_selected_area, mock_delete_upload_area, mock_clear_area_perms):
        mock_area = "mock-area"
        mock_files_to_delete = ["mock-file-1", "mock-file-2", "mock-file-3"]
        mock_args = Mock()
        mock_args.d = True
        mock_aws = MagicMock()
        mock_aws.is_user = False

        mock_selected_area.return_value = "mock-area"
        mock_delete_upload_area.return_value = list(map(lambda file: f'{mock_area}/{file}', mock_files_to_delete)) + [mock_area]
        mock_clear_area_perms.return_value = None
        cmd_delete = CmdDelete(mock_aws, mock_args)

        with patch("builtins.input", return_value="Y"), patch('sys.stdout', new=StringIO()) as cmd_output:
            cmd_delete.run()
            cmd_output_lines = cmd_output.getvalue().split("\n")
            self.assertTrue("Deleting" in cmd_output_lines[0])
            self.assertTrue("mock-file-1" in cmd_output_lines[1])
            self.assertTrue("mock-file-2" in cmd_output_lines[2])
            self.assertTrue("mock-area" in cmd_output_lines[3])

    @patch("util.command.delete.get_selected_area")
    def test_user_cannot_delete_area(self, mock_selected_area):
        mock_args = Mock()
        mock_args.d = True
        mock_aws = MagicMock()
        mock_aws.is_user = True
        mock_selected_area.return_value = "mock-area"

        cmd_delete = CmdDelete(mock_aws, mock_args)

        res, output = cmd_delete.run()
        self.assertTrue("You don't have permission to use this command" in output)


if __name__ == '__main__':
    unittest.main()

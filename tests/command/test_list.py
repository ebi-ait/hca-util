import unittest
from unittest.mock import MagicMock, Mock, patch
from io import StringIO

from util.command.list import CmdList


class TestList(unittest.TestCase):
    @patch("util.command.list.CmdList.list_area_contents")
    @patch("util.command.list.get_selected_area")
    def test_user_can_list_upload_area_contents(self, mock_selected_area, mock_list_area_contents):
        mock_selected_area.return_value = "/"
        mock_area_contents = ["f1", "f2", "dir1/", "dir1/f1", "dir1/f2", "dir2/", "dir2/f1", "dir2/f2"]
        mock_list_area_contents.return_value = mock_area_contents
        mock_aws = MagicMock()
        test_args = Mock()
        test_args.b = None

        with patch('sys.stdout', new=StringIO()) as cmd_output:
            cmd_list = CmdList(mock_aws, test_args)
            cmd_list.run()
            cmd_output_lines = cmd_output.getvalue().split("\n")
            for mock_area_key in mock_area_contents:
                self.assertTrue(mock_area_key in cmd_output_lines)

            self.assertTrue("6 items" in cmd_output_lines)

    @patch("util.command.list.get_selected_area")
    def test_user_message_when_no_area_selected(self, mock_selected_area):
        mock_selected_area.return_value = None

        mock_aws = MagicMock()
        test_args = Mock()
        test_args.b = None

        cmd_list = CmdList(mock_aws, test_args)
        cmd_response = cmd_list.run()
        self.assertTrue(cmd_response[0] is False and cmd_response[1] == 'No area selected')

    def test_user_cannot_list_upload_areas_in_bucket(self):
        mock_aws = MagicMock()
        test_args = Mock()
        mock_aws.is_user = True

        cmd_list = CmdList(mock_aws, test_args)
        cmd_response = cmd_list.run()

        self.assertTrue(cmd_response[0] is False and cmd_response[1] == 'You don\'t have permission to use this command')

    @patch("util.command.list.CmdList.list_bucket_areas")
    def test_admin_can_list_upload_areas_in_bucket(self, mock_list_bucket_areas):
        mock_list_bucket_areas.return_value = [
            dict(key="mock-area-1", perms="u", name="mymockarea1"),
            dict(key="mock-area-2", perms=None, name="mymockarea2"),
            dict(key="mock-area-3", perms="ud", name=None)
        ]
        mock_aws = MagicMock()
        mock_aws.is_user = False
        test_args = Mock()

        with patch('sys.stdout', new=StringIO()) as cmd_output:
            cmd_list = CmdList(mock_aws, test_args)
            cmd_response = cmd_list.run()
            cmd_output_lines = cmd_output.getvalue().split("\n")
            self.assertTrue("mock-area-1" in cmd_output_lines[0])
            self.assertTrue(" u " in cmd_output_lines[0])
            self.assertTrue("mymockarea1" in cmd_output_lines[0])

            self.assertTrue("mock-area-3" in cmd_output_lines[2])
            self.assertTrue(" ud " in cmd_output_lines[2])

            self.assertTrue("3 items" in cmd_output_lines)

if __name__ == '__main__':
    unittest.main()

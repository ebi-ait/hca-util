import os
import sys
from unittest import TestCase

from tests.e2e.test_e2e_admin import search_uuid, run

sys.path.append(os.getcwd())


USER_PROFILE = 'test-util-user'
USER_ACCESS = os.environ.get('USER_ACCESS')
USER_SECRET = os.environ.get('USER_SECRET')

ADMIN_PROFILE = 'test-util-admin'
ADMIN_ACCESS = os.environ.get('ADMIN_ACCESS')
ADMIN_SECRET = os.environ.get('ADMIN_SECRET')

NAME = 'util'
CLI = f'python3 -m {NAME}'


class TestUserE2E(TestCase):
    def setUp(self) -> None:
        self.filename = 'test-user-file.txt'
        self.upload_area = 'testuseruploadarea'
        self.upload_area_uuid = None

    def test_e2e_user(self):
        profile = f'--profile {ADMIN_PROFILE}'
        upload_area = self.upload_area
        filename = self.filename

        print(f'# Configuring {NAME} admin\n')
        self._assert_successful_run(f'{CLI} config {ADMIN_ACCESS} {ADMIN_SECRET} {profile}', verbose=False)

        print('# Creating Upload Area\n')
        output = self._assert_successful_run(f'{CLI} create {self.upload_area} -p udx {profile}')
        self.upload_area_uuid = search_uuid(output)
        upload_area_uuid = self.upload_area_uuid
        self.assertTrue(self.upload_area_uuid, 'The upload area uuid could not be found from the output')

        print(f'# Configuring {CLI} user\n')
        profile = f'--profile {USER_PROFILE}'
        self._assert_successful_run(f'{CLI} config {USER_ACCESS} {USER_SECRET} {profile}', verbose=False)

        print('# Selecting Upload Area\n')
        self._assert_successful_run(f'{CLI} select {upload_area_uuid} {profile}')

        print('# Uploading file\n')
        self._assert_successful_run(f'touch {filename}')
        self._assert_successful_run(f'{CLI} upload {filename} {profile}')

        print('# Listing file\n')
        output = self._assert_successful_run(f'{CLI} list {profile}')
        self.assertTrue(filename in output, f'file {filename} was not uploaded to {upload_area}, output: {output}')

        os.remove(filename)
        print('# Downloading file\n')
        self._assert_successful_run(f'{CLI} download {filename} {profile}')

        self.assertTrue(os.path.exists(self.filename), f'File {filename} should have been downloaded.')

        print('# Deleting file\n')
        self._assert_successful_run(f'{CLI} delete {filename} {profile}')

        print('# Listing file to check if it is deleted\n')
        output = self._assert_successful_run(f'{CLI} list {profile}')
        self.assertFalse(filename in output, f'file {filename} was not deleted to {upload_area}, output: {output}')

        print('# Deleting upload area\n')
        exit_code, output, error = run(f'{CLI} delete -d {profile}', input="y\n")
        self.assertEqual(exit_code, 1, f'user has no permission to delete upload area, output: {output}, error:{error}')

        print('# Listing upload area to check if it is deleted\n')
        select_upload, output, error = run(f'{CLI} select {upload_area_uuid} {profile}')
        self.assertEqual(select_upload, 0,
                         f'upload area {upload_area_uuid} should not be deleted, output: {output}, error:{error}')

        print('# Deleting upload area\n')
        profile = f'--profile {ADMIN_PROFILE}'
        self._assert_successful_run(f'{CLI} delete -d {profile}', input="y\n")
        self.upload_area_uuid = None

        print('# Listing upload area to check if it is deleted\n')
        select_upload, output, error = run(f'{CLI} select {upload_area_uuid} {profile}')
        self.assertEqual(select_upload, 1,
                         f'upload area {upload_area_uuid} is not deleted, output: {output}, error:{error}')

    def _assert_successful_run(self, command: str, **kwargs):
        exit_code, output, error = run(command, **kwargs)
        self.assertEqual(0, exit_code, f'output: {output}, error:{error}')
        return output

    def tearDown(self) -> None:
        if os.path.exists(self.filename):
            print(f'Deleting file {self.filename}')
            os.remove(self.filename)
            print(f'File {self.filename} deleted')

        if self.upload_area_uuid:
            print(f'Deleting upload area {self.upload_area_uuid}')
            profile = f'--profile {ADMIN_PROFILE}'
            exit_code, output, error = run(f'{CLI} delete -d {profile}', input="y\n")

            if exit_code == 0:
                print(f'Upload area {self.upload_area_uuid} deleted!')
            else:
                print(output)
                print(error)

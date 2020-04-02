import os
import sys
from unittest import TestCase

from tests.e2e.test_e2e_admin import search_uuid, run

sys.path.append(os.getcwd())

user_profile = 'test-hca-util-user'
user_access = os.environ.get('HCA_UTIL_USER_ACCESS')
user_secret = os.environ.get('HCA_UTIL_USER_SECRET')

admin_profile = 'test-hca-util'
admin_access = os.environ.get('HCA_UTIL_ADMIN_ACCESS')
admin_secret = os.environ.get('HCA_UTIL_ADMIN_SECRET')

name = 'hca_util'
cli = f'python3 -m {name}'


class TestUserE2E(TestCase):
    def test_e2e_user(self):
        profile = f'--profile {admin_profile}'

        print(f'# Configuring {cli} admin\n')
        self._assert_successful_run(f'{cli} config {admin_access} {admin_secret} {profile}', verbose=False)

        print('# Creating Upload Area\n')
        upload_area = 'testuseruploadarea'
        output = self._assert_successful_run(f'{cli} create {upload_area} {profile}')

        upload_area_uuid = search_uuid(output)
        self.assertTrue(upload_area_uuid, 'The upload area uuid could not be found from the output')

        profile = f'--profile {user_profile}'
        print(f'# Configuring {cli} user\n')
        self._assert_successful_run(f'{cli} config {user_access} {user_secret} {profile}', verbose=False)

        print('# Selecting Upload Area\n')
        self._assert_successful_run(f'{cli} select {upload_area_uuid} {profile}')

        filename = 'test-user-file.txt'
        self._assert_successful_run(f'touch {filename}')

        print('# Uploading file\n')
        self._assert_successful_run(f'{cli} upload -f {filename} {profile}')

        print('# Listing file\n')
        output = self._assert_successful_run(f'{cli} list {profile}')
        self.assertTrue(filename in output, f'file {filename} was not uploaded to {upload_area}, output: {output}')

        print('# Deleting file\n')
        self._assert_successful_run(f'{cli} delete -f {filename} {profile}')

        print('# Listing file to check if it is deleted\n')
        output = self._assert_successful_run(f'{cli} list {profile}')
        self.assertFalse(filename in output, f'file {filename} was not deleted to {upload_area}, output: {output}')

        print('# Deleting upload area\n')
        exit_code, output, error = run(f'{cli} delete -d {profile}', input="y\n")
        self.assertEqual(exit_code, 1, f'user has no permission to delete upload area, output: {output}, error:{error}')

        print('# Listing upload area to check if it is deleted\n')
        select_upload, output, error = run(f'{cli} select {upload_area_uuid} {profile}')
        self.assertEqual(select_upload, 0,
                         f'upload area {upload_area_uuid} should not be deleted, output: {output}, error:{error}')

        profile = f'--profile {admin_profile}'
        print('# Deleting upload area\n')
        self._assert_successful_run(f'{cli} delete -d {profile}', input="y\n")

        print('# Listing upload area to check if it is deleted\n')
        select_upload, output, error = run(f'{cli} select {upload_area_uuid} {profile}')
        self.assertEqual(select_upload, 1,
                         f'upload area {upload_area_uuid} is not deleted, output: {output}, error:{error}')

        # cleanup
        self._assert_successful_run(f'rm {filename}')

    def _assert_successful_run(self, command: str, **kwargs):
        exit_code, output, error = run(command, **kwargs)
        self.assertEqual(0, exit_code, f'output: {output}, error:{error}')
        return output

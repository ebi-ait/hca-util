import os
from unittest import TestCase

from tests.e2e.test_utils import search_uuid, run

admin_access = os.environ.get('HCA_UTIL_ADMIN_ACCESS')
admin_secret = os.environ.get('HCA_UTIL_ADMIN_SECRET')

admin_profile = 'test-hca-util'

name = 'hca_util'
cli = f'python3 -m {name}'


class TestAdminE2E(TestCase):
    def test_e2e_admin(self):
        profile = f'--profile {admin_profile}'

        print(f'# Configuring {cli}\n')
        self._assert_successful_run(f'{cli} config {admin_access} {admin_secret} {profile}', verbose=False)

        print('# Creating Upload Area\n')
        upload_area = 'testadminuploadarea'
        output = self._assert_successful_run(f'{cli} create {upload_area} {profile}')

        upload_area_uuid = search_uuid(output)
        self.assertTrue(upload_area_uuid, 'The upload area uuid could not be found from the output')

        print('# Selecting Upload Area\n')
        self._assert_successful_run(f'{cli} select {upload_area_uuid} {profile}')

        filename = 'test-admin-file.txt'
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
        self._assert_successful_run(f'{cli} delete -d {profile}', input="y\n")

        print('# Listing upload area to check if it is deleted\n')
        select_upload, output, error = run(f'{cli} select {upload_area_uuid} {profile}')

        self.assertEqual(1, select_upload,
                         f'upload area {upload_area_uuid} is not deleted, output: {output}, error:{error}')

        # cleanup
        self._assert_successful_run(f'rm {filename}')

    def _assert_successful_run(self, command: str, **kwargs):
        exit_code, output, error = run(command, **kwargs)
        self.assertEqual(0, exit_code, f'output: {output}, error:{error}')
        return output

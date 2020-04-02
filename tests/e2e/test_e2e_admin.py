import os
from unittest import TestCase

from tests.e2e.test_utils import search_uuid, run


ADMIN_ACCESS = os.environ.get('ADMIN_ACCESS')
ADMIN_SECRET = os.environ.get('ADMIN_SECRET')

ADMIN_PROFILE = 'test-hca-util'

NAME = 'hca_util'
CLI = f'python3 -m {NAME}'


class TestAdminE2E(TestCase):
    def setUp(self) -> None:
        self.filename = 'test-admin-file.txt'
        self.upload_area = 'testadminuploadarea'
        self.upload_area_uuid = None

    def test_e2e_admin(self):
        profile = f'--profile {ADMIN_PROFILE}'
        filename = self.filename
        upload_area = self.upload_area

        print(f'# Configuring {CLI}\n')
        self._assert_successful_run(f'{CLI} config {ADMIN_ACCESS} {ADMIN_SECRET} {profile}', verbose=False)

        print('# Creating Upload Area\n')

        output = self._assert_successful_run(f'{CLI} create {upload_area} {profile}')

        upload_area_uuid = search_uuid(output)
        self.upload_area_uuid = upload_area_uuid
        self.assertTrue(upload_area_uuid, 'The upload area uuid could not be found from the output')

        print('# Selecting Upload Area\n')
        self._assert_successful_run(f'{CLI} select {upload_area_uuid} {profile}')

        print('# Uploading file\n')

        self._assert_successful_run(f'touch {filename}')
        self._assert_successful_run(f'{CLI} upload {filename} {profile}')


        print('# Listing file\n')
        output = self._assert_successful_run(f'{CLI} list {profile}')
        self.assertTrue(filename in output, f'file {filename} was not uploaded to {upload_area}, output: {output}')

        print('# Deleting file\n')
        self._assert_successful_run(f'{CLI} delete {filename} {profile}')

        print('# Listing file to check if it is deleted\n')
        output = self._assert_successful_run(f'{CLI} list {profile}')
        self.assertFalse(filename in output, f'file {filename} was not deleted to {upload_area}, output: {output}')

        print('# Deleting upload area\n')
        self._assert_successful_run(f'{CLI} delete -d {profile}', input="y\n")
        self.upload_area_uuid = None

        print('# Listing upload area to check if it is deleted\n')
        select_upload, output, error = run(f'{CLI} select {upload_area_uuid} {profile}')

        self.assertEqual(1, select_upload,
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

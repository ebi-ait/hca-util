import os
import sys
import time
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
        self.downloaded_dir = None
        self.downloaded_file = None
        self.dir = 'test-dir'
        self.filename2 = 'test-user-file2.txt'

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
        os.system(f'echo "t" > {filename}')
        self._assert_successful_run(f'{CLI} upload {filename} {profile}')

        time.sleep(3)

        print('# Uploading dir\n')
        os.system(f'mkdir {self.dir}')
        os.system(f'echo "t" > {self.dir}/{self.filename2}')
        self._assert_successful_run(f'{CLI} upload {self.dir} -r {profile}')

        time.sleep(3)

        print('# Listing file\n')
        output = self._assert_successful_run(f'{CLI} list {profile}')
        self.assertTrue(filename in output, f'file {filename} was not uploaded to {upload_area}, output: {output}')
        self.assertTrue(self.filename2 in output,
                        f'file {self.filename2} was not uploaded to {upload_area}, output: {output}')

        print('# Downloading all\n')
        # os.remove(filename)
        self._assert_successful_run(f'{CLI} download -a {profile}')  # TODO should be specific file

        time.sleep(3)

        self._assert_successful_run(f'ls')
        cwd = os.getcwd()

        self.downloaded_dir = f'{cwd}/{upload_area_uuid}'
        self.downloaded_file = f'{cwd}/{upload_area_uuid}/{self.filename}'
        self.downloaded_file2 = f'{cwd}/{upload_area_uuid}/{self.filename2}'

        self.assertTrue(os.path.exists(self.downloaded_dir), f'Upload area {upload_area_uuid} dir should be downloaded')
        self.assertTrue(os.path.exists(self.downloaded_file), f'File {filename} should have been downloaded.')
        self.assertTrue(os.path.exists(self.downloaded_file2), f'File {filename} should have been downloaded.')

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

        tries = 1
        while exit_code != 0 and tries != 5:
            print('Retrying command...')
            time.sleep(3)
            exit_code, output, error = run(command, **kwargs)
            tries += 1

        self.assertEqual(0, exit_code, f'output: {output}, error:{error}')
        return output

    def tearDown(self) -> None:
        for file in [self.filename]:
            if os.path.exists(file):
                print(f'Deleting file {file}')
                os.remove(file)
                print(f'File {file} deleted')

        if os.path.exists(self.downloaded_dir):
            os.system(f'rm -rf {self.downloaded_dir}')
            print(f'Deleted {self.downloaded_dir}')

        if os.path.exists(self.dir):
            os.system(f'rm -rf {self.dir}')
            print(f'Deleted {self.dir}')

        if self.upload_area_uuid:
            print(f'Deleting upload area {self.upload_area_uuid}')
            profile = f'--profile {ADMIN_PROFILE}'
            exit_code, output, error = run(f'{CLI} delete -d {profile}', input="y\n")

            if exit_code == 0:
                print(f'Upload area {self.upload_area_uuid} deleted!')
            else:
                print(output)
                print(error)

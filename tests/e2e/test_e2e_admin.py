import os
import re
import subprocess
import sys
from unittest import TestCase

sys.path.append('.')

admin_access = os.environ.get('HCA_UTIL_ADMIN_ACCESS')
admin_secret = os.environ.get('HCA_UTIL_ADMIN_SECRET')


def run(command: str, input: str = None, verbose=True):
    parsed_command = command.split(' ')
    proc = subprocess.Popen(parsed_command,
                            stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE,
                            )
    if input:
        stdout, stderr = proc.communicate(input.encode())
    else:
        stdout, stderr = proc.communicate()

    if verbose:
        print('$ ' + command)
        print(stdout.decode())
        print(stderr.decode())

    return proc.returncode, stdout.decode(), stderr.decode()


def search_uuid(text: str):
    m = re.search('([a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12})', text)
    if m:
        return m.group(1)
    return None


class TestAdminE2E(TestCase):
    def test_e2e_admin(self):
        # config
        print('Configuring covid-util')
        config, output, error = run(f'covid-util config {admin_access} {admin_secret} --profile covid-util', verbose=False)
        print(f'{output}')
        self.assertEqual(config, 0, f'config is not successful, output: {output}, error:{error}')

        # create upload area
        print('Creating Upload Area')
        upload_area = 'testuploadarea'
        create_upload, output, error = run(f'covid-util create {upload_area} --profile covid-util')

        self.assertEqual(create_upload, 0, f'upload area {upload_area} is not created, output: {output}, error:{error}')
        upload_area_uuid = search_uuid(output)
        self.assertTrue(upload_area_uuid, 'The upload area uuid could not be found from the output')

        # select upload area
        print('Selecting Upload Area')
        select_upload, output, error = run(f'covid-util select {upload_area_uuid} --profile covid-util')
        self.assertEqual(select_upload, 0,
                         f'upload area {upload_area_uuid} is not selected, output: {output}, error:{error}')

        # create tests file
        content = 'testing uploading of file'
        filename = 'tests-file.txt'

        create_file, output, error = run(f'touch {filename}')
        self.assertEqual(create_file, 0, f'Creation of tests file failed, output: {output}, error:{error}')

        # upload tests file
        print('Uploading file')
        upload_file, output, error = run(f'covid-util upload -f {filename} --profile covid-util')
        self.assertEqual(upload_file, 0, f'file upload failed, output: {output}, error:{error}')

        # list files
        print('Listing file')
        list_files, output, error = run(f'covid-util list --profile covid-util')
        self.assertEqual(list_files, 0, f'file cannot be listed, output: {output}, error:{error}')
        self.assertTrue(filename in output,
                        f'file {filename} was not uploaded to {upload_area}, output: {output}, error:{error}')

        # delete file
        print('Deleting file')
        delete_file, output, _ = run(f'covid-util delete -f {filename} --profile covid-util')
        self.assertEqual(delete_file, 0, f'{filename} cannot be deleted, output: {output}, error:{error}')

        # list files
        print('Listing file to check if it is deleted')
        list_files, output, error = run(f'covid-util list --profile covid-util')
        self.assertFalse(filename in output,
                         f'file {filename} was not deleted to {upload_area}, output: {output}, error:{error}')

        print('Deleting upload area')
        delete_upload, output, _ = run(f'covid-util delete -d --profile covid-util', "y\n")

        print('Listing upload area to check if it is deleted')
        select_upload, output, error = run(f'covid-util select {upload_area_uuid} --profile covid-util')
        self.assertEqual(select_upload, 1,
                         f'upload area {upload_area_uuid} is not deleted, output: {output}, error:{error}')

        delete_local_file, output, error = run(f'rm {filename}')
        self.assertEqual(delete_local_file, 0, f'{filename} cannot be deleted locally, output: {output}, error:{error}')

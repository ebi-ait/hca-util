import sys

from tests.e2e.test_utils import run, search_all_uuids

FILENAME = sys.argv[1]  # file which contains uuids to delete

CLI = 'morphic-util'

code, output, error = run(FILENAME)
uuids = search_all_uuids(output)

print(uuids)

print(len(uuids))

for uuid in uuids:
    run(f'{CLI} select {uuid}')
    run(f'{CLI} delete -d', "y\n")
    print(f'deleted {uuid}!')

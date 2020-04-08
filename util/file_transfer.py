# from multiprocessing.dummy import Pool
import threading
from time import sleep


class TransferProgress(object):

    def __init__(self, file_transfer):
        self._file_transfer = file_transfer
        self._lock = threading.Lock()

    def __call__(self, bytes_amount):

        with self._lock:
            self._file_transfer.seen_so_far += bytes_amount
            percentage = (self._file_transfer.seen_so_far / self._file_transfer.size) * 100

            if percentage == 100.0:
                self._file_transfer.complete = True
                self._file_transfer.successful = True

            self._file_transfer.status = f'({percentage:.2f}%)'


class FileTransfer:
    def __init__(self, path, key, size=0, seen_so_far=0, status='', complete=False):
        self.path = path
        self.key = key
        self.size = size
        self.seen_so_far = seen_so_far
        self.status = status
        self.complete = complete
        self.successful = False

    def __str__(self):
        return f'FileTransfer (path={self.path}, key={self.key}, size={self.size}, seen_so_far={self.seen_so_far}, status={self.status}, complete={self.complete}) '


# with Pool(12) as p:
#    p.map(lambda f: self.upload(f), fs)
#    print('Done.')

# using a thread per file upload instead of threadpool as they are cheap

def transfer(t, fs):
    for i in range(len(fs)):
        if not fs[i].complete:
            threading.Thread(target=t, args=(i,)).start()

    # print initial transfer progress
    for f in fs:
        print(f'{f.key}  {f.seen_so_far} / {f.size}  {f.status}')

    while True:
        if [t for t in fs if not t.complete]:
            sleep(1)  # 1 sec
            print(f'\033[{len(fs) + 1}A\r')  # go back to start of first progress_list item
            for f in fs:
                print(f'{f.key}  {f.seen_so_far} / {f.size}  {f.status}')
        else:
            break

import os
import sys
import threading


class UploadProgress(object):

    def __init__(self, filename, progress_list, i):
        self._progress_list = progress_list
        self._idx = i
        self._filename = filename
        self._size = float(os.path.getsize(filename))
        self._seen_so_far = 0
        self._lock = threading.Lock()

    def __call__(self, bytes_amount):

        with self._lock:
            self._seen_so_far += bytes_amount
            percentage = (self._seen_so_far / self._size) * 100
            # sys.stdout.write("\r%s  %s / %s  (%.2f%%)" % (self._filename, self._seen_so_far, self._size, percentage))
            # sys.stdout.flush()

            self._progress_list[self._idx] = "%s  %s / %s  (%.2f%%)" % (self._filename, self._seen_so_far, self._size, percentage)

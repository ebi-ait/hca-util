import threading
from tqdm import tqdm


class ProgressBar:
    def __init__(self, target, total):
        self._target = target
        self._total = total
        self._seen_so_far = 0
        self._lock = threading.Lock()

    def __call__(self, bytes_amount):
        with tqdm(total=self._total, desc=self._target) as pbar:
            with self._lock:
                self._seen_so_far += bytes_amount
            pbar.update(self._seen_so_far)
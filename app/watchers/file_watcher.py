import os
import time
from typing import Callable

class FileWatcher:
    def __init__(self, watch_dir: str, file_pattern: str = "*.txt"):
        self.watch_dir = watch_dir
        self.file_pattern = file_pattern
        self.seen_files = set()

        if not os.path.exists(self.watch_dir):
            os.makedirs(self.watch_dir)

    def scan(self) -> list[str]:
        """Return list of new files that match the pattern."""
        matched = []
        for fname in os.listdir(self.watch_dir):
            fpath = os.path.join(self.watch_dir, fname)
            if not os.path.isfile(fpath):
                continue
            if not self._matches_pattern(fname):
                continue
            if fpath not in self.seen_files:
                self.seen_files.add(fpath)
                matched.append(fpath)
        return matched

    def _matches_pattern(self, filename: str) -> bool:
        return filename.endswith(self.file_pattern.lstrip("*"))

    def watch(self, callback: Callable[[str], None], interval: int = 60):
        """Poll directory and run callback(file_path) for each new file."""
        print(f"[Watcher] Watching {self.watch_dir} every {interval}s...")
        while True:
            new_files = self.scan()
            for file_path in new_files:
                print(f"[Watcher] Detected new file: {file_path}")
                callback(file_path)
            time.sleep(interval)

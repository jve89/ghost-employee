import os
import time
from threading import Thread
from app.jobs.job_registry import job_registry
from config.config_loader import load_job_configs

WATCH_INTERVAL = 5  # seconds

class FolderWatcher(Thread):
    def __init__(self, config):
        super().__init__(daemon=True)
        self.config = config
        self.seen_files = set()

    def run(self):
        path = self.config.watch_dir
        if not os.path.exists(path):
            os.makedirs(path)
        while True:
            for file in os.listdir(path):
                if file.endswith(".txt") and file not in self.seen_files:
                    self.seen_files.add(file)
                    full_path = os.path.join(path, file)
                    with open(full_path, "r", encoding="utf-8", errors="replace") as f:
                        content = f.read()
                    job = job_registry.get(self.config.job_name)
                    if job:
                        job.run(self.config, override_text=content, source=full_path)
            time.sleep(WATCH_INTERVAL)

def start_watchers():
    for config in load_job_configs():
        watcher = FolderWatcher(config)
        watcher.start()

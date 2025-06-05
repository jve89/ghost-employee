import os
import time
from threading import Thread
from app.jobs.job_registry import job_registry
from config.config_loader import load_job_configs
from infrastructure.logger.activity_log import activity_log

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
                if not file.endswith(".txt"):
                    continue
                if file in self.seen_files:
                    continue
                if hasattr(self.config, "file_pattern"):
                    import fnmatch
                    if not fnmatch.fnmatch(file, self.config.file_pattern):
                        print(f"[⏭️ Skipped] {file} does not match pattern: {self.config.file_pattern}")
                        continue

                self.seen_files.add(file)
                full_path = os.path.join(path, file)
                print(f"[📁 Watcher] New file: {file}")
                try:
                    with open(full_path, "r", encoding="utf-8", errors="replace") as f:
                        content = f.read()
                except Exception as e:
                    print(f"[⚠️ Error] Failed to read {file}: {e}")
                    continue

                job = job_registry.get(self.config.job_name)
                if job:
                    activity_log.record(
                        job_name=self.config.job_name,
                        trigger="watcher",
                        file=file,
                        status="started"
                    )
                    job.run(self.config, override_text=content, source=full_path)
                    activity_log.record(
                        job_name=self.config.job_name,
                        trigger="watcher",
                        file=file,
                        status="completed"
                    )
                else:
                    print(f"[⚠️ Watcher] Job '{self.config.job_name}' not found in registry.")

            time.sleep(WATCH_INTERVAL)

def start_watchers():
    for config in load_job_configs():
        watcher = FolderWatcher(config)
        watcher.start()

import os
import time
import threading
from fnmatch import fnmatch
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from config.config_loader import load_all_job_configs
from app.jobs.job_registry import job_registry
from app.core.models import JobConfig

class JobTriggerHandler(FileSystemEventHandler):
    def __init__(self, job_config: JobConfig):
        self.job_config = job_config
        self.last_trigger_time = 0  # 🕒 used for debouncing
        self.debounce_interval = 5  # seconds

    def on_modified(self, event):
        if not event.is_directory:
            file_name = os.path.basename(event.src_path)
            print(f"[📁 Watcher] Modified file: {file_name}")

            if not fnmatch(file_name, self.job_config.file_pattern or "*"):
                print(f"[⏭️ Skipped] {file_name} does not match pattern: {self.job_config.file_pattern}")
                return

            self.trigger_job(event.src_path)

    def on_created(self, event):
        if not event.is_directory:
            file_name = os.path.basename(event.src_path)
            print(f"[📁 Watcher] New file: {file_name}")

            if not fnmatch(file_name, self.job_config.file_pattern or "*"):
                print(f"[⏭️ Skipped] {file_name} does not match pattern: {self.job_config.file_pattern}")
                return

            self.trigger_job(event.src_path)

    def trigger_job(self, file_path=None):
        now = time.time()
        if now - self.last_trigger_time < self.debounce_interval:
            print(f"[⏳ Debounce] Ignoring duplicate trigger for '{self.job_config.job_id}'")
            return

        self.last_trigger_time = now
        job = job_registry.get(self.job_config.job_id)
        if not job:
            print(f"[⚠️ Watcher] Job '{self.job_config.job_id}' not found in registry.")
            return
        print(f"[📁 Watcher] Triggering job: {self.job_config.job_id} on file: {file_path}")
        job.run(self.job_config, file_path)

def start_watchers():
    configs = load_all_job_configs()
    observers = []

    for config in configs:
        if not getattr(config, "active", True):
            print(f"[⏸️ Watcher] Skipping inactive job: {config.job_name}")
            continue

        watch_dir = config.watch_dir
        if not os.path.isdir(watch_dir):
            print(f"[📂 Auto-Create] Creating watch_dir: {watch_dir}")
            os.makedirs(watch_dir, exist_ok=True)

        event_handler = JobTriggerHandler(config)
        observer = Observer()
        observer.schedule(event_handler, path=watch_dir, recursive=False)
        observer.start()
        observers.append(observer)
        print(f"[👁️ Watcher] Watching: {watch_dir} for job '{config.job_name}'")

    # Keep thread alive
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        for obs in observers:
            obs.stop()
        for obs in observers:
            obs.join()

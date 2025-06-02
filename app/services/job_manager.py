import threading
import time
from app.core.models import JobConfig
from app.jobs.job_registry import job_registry

class JobManager:
    def __init__(self, configs: list[JobConfig]):
        self.configs = configs
        self.threads = []

    def run_all_jobs(self):
        for config in self.configs:
            self._run_job_once(config)

    def start_scheduled_jobs(self):
        for config in self.configs:
            thread = threading.Thread(target=self._run_job_loop, args=(config,), daemon=True)
            thread.start()
            self.threads.append(thread)

    def _run_job_loop(self, config: JobConfig):
        job = job_registry.get(config.job_name)
        if not job:
            print(f"[WARN] Job '{config.job_name}' not found in registry.")
            return

        while True:
            print(f"[SCHEDULER] Running job '{config.job_name}'...")
            job.run(config)
            time.sleep(config.run_interval_seconds)

    def _run_job_once(self, config: JobConfig):
        job = job_registry.get(config.job_name)
        if job:
            job.run(config)
        else:
            print(f"[WARN] Job '{config.job_name}' not found in registry.")

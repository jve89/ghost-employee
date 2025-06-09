import threading
import time
from app.core.models import JobConfig
from app.jobs.job_registry import job_registry
from infrastructure.logger.activity_log import activity_log

class JobManager:
    def __init__(self, configs: list[JobConfig]):
        self.configs = configs
        self.threads = []

    def run_all_jobs(self):
        for config in self.configs:
            self._run_job_once(config)

    def start_scheduled_jobs(self):
        for config in self.configs:
            if not getattr(config, "active", True):
                print(f"[SCHEDULER] Skipping inactive job: {config.job_name}")
                continue
            thread = threading.Thread(target=self._run_job_loop, args=(config,), daemon=True)
            thread.start()
            self.threads.append(thread)

    def _run_job_loop(self, config: JobConfig):
        job = job_registry.get(config.job_name)
        if not job:
            print(f"[WARN] Job '{config.job_name}' not found in registry.")
            return

        print(f"[JobManager] ✅ Registered job: {config.job_id} with exporters: {[d['type'] for d in config.export_destinations]}")

        while True:
            print(f"[SCHEDULER] Running job '{config.job_name}'...")
            activity_log.record(job_name=config.job_name, trigger="interval", status="started")
            job.run(config)
            activity_log.record(job_name=config.job_name, trigger="interval", status="completed")
            time.sleep(config.run_interval_seconds)

    def _run_job_once(self, config: JobConfig):
        job = job_registry.get(config.job_name)
        if job:
            activity_log.record(job_name=config.job_name, trigger="manual", status="started")
            job.run(config)
            activity_log.record(job_name=config.job_name, trigger="manual", status="completed")
        else:
            print(f"[WARN] Job '{config.job_name}' not found in registry.")

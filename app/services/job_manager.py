import threading
import time
from app.core.models import JobConfig
from app.jobs.job_registry import job_registry
from infrastructure.logger.activity_log import activity_log
from config.config_loader import load_job_config

class JobManager:
    def __init__(self, configs: list[JobConfig]):
        self.configs = configs
        self.threads = []
        self.running_jobs = {}  # Track jobs by ID

    def run_all_jobs(self):
        for config in self.configs:
            self._run_job_once(config)

    def start_scheduled_jobs(self):
        for config in self.configs:
            if not getattr(config, "active", True):
                print(f"[SCHEDULER] Skipping inactive job: {config.job_name}")
                continue
            self._start_job_thread(config)

    def _start_job_thread(self, config: JobConfig):
        if config.job_id in self.running_jobs:
            print(f"[SCHEDULER] Job '{config.job_id}' already running. Skipping.")
            return

        thread = threading.Thread(target=self._run_job_loop, args=(config,), daemon=True)
        thread.start()
        self.running_jobs[config.job_id] = thread
        self.threads.append(thread)

    def _run_job_loop(self, config: JobConfig):
        job = job_registry.get(config.job_name)
        if not job:
            print(f"[WARN] Job '{config.job_name}' not found in registry.")
            return

        print(f"[JobManager] ✅ Registered job: {config.job_id} with exporters: {[d['type'] for d in config.export_destinations]}")

        while True:
            if not getattr(config, "active", True):
                print(f"[JobManager] ⏸️ Job '{config.job_name}' is paused.")
                time.sleep(1)
                continue
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

    def resume_job(self, job_id: str) -> str:
        if job_id in self.running_jobs:
            print(f"[JobManager] 🔄 Job '{job_id}' is already running.")
            return "already_running"

        config = load_job_config(job_id)
        config.active = True  # Reactivate the job
        self._start_job_thread(config)
        print(f"[JobManager] ✅ Job '{job_id}' resumed.")
        return "resumed"

def toggle_job_active(job_id: str) -> bool:
    from config.config_loader import load_job_config, save_job_config

    try:
        config = load_job_config(job_id)
        config.active = not getattr(config, "active", True)
        save_job_config(config, client_id="default")
        return config.active
    except Exception as e:
        print(f"❌ toggle_job_active failed for {job_id}: {e}")
        raise

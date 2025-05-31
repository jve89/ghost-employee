from app.core.models import JobConfig
from app.jobs.job_registry import job_registry

class JobManager:
    def __init__(self, configs: list[JobConfig]):
        self.configs = configs

    def run_all_jobs(self):
        for config in self.configs:
            job = job_registry.get(config.job_name)
            if job:
                job.run(config)
            else:
                print(f"[WARN] Job '{config.job_name}' not found in registry.")

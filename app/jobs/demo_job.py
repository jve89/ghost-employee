# app/jobs/demo_job.py
"""
🧪 Minimal Demo Job
Safe testbed for execution and export logic.
Does NOT use GPT. Ideal for dry-run and export testing.
"""
from datetime import datetime
from app.core.models import Task, JobConfig
from app.services.simple_executor import SimpleExecutor

class DemoJob:
    def run(self, config: JobConfig, override_text: str | None = None, source: str = "unknown") -> list[Task]:
        task = Task(
            job_id=config.job_id,
            source=source,
            description="Demo: Generate monthly report and notify stakeholders.",
            summary=override_text or "No summary provided.",
            created_at=datetime.utcnow().isoformat()
        )

        executor = SimpleExecutor()
        executor.execute(task, config)

        return [task]

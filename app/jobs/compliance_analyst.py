from datetime import datetime
from app.services.simple_executor import SimpleExecutor
from app.core.models import Task, JobConfig

class ComplianceAnalystJob:
    def run(self, config: JobConfig, override_text: str | None = None, source: str = "unknown") -> list[Task]:
        task = Task(
            job_id=config.job_id,
            source=source,
            description="Check compliance summary and log action items.",
            summary=override_text or "No summary provided.",
            created_at=datetime.utcnow().isoformat()
        )

        executor = SimpleExecutor()
        executor.execute(task, config)

        return [task]

"""
🧪 Minimal Demo Job
Safe testbed for execution and export logic.
Does NOT use GPT. Ideal for dry-run and export testing.
"""

from datetime import datetime
from app.core.models import Task, JobConfig
from app.services.simple_executor import SimpleExecutor
from app.services.demo_report_generator import generate_demo_report
from app.services.export_dispatcher import dispatch_exports
from infrastructure.logger.job_status import job_status
from infrastructure.logger.memory_logger import logger


class DemoJob:
    def run(self, config: JobConfig, override_text: str | None = None, source: str = "unknown") -> list[Task]:
        job_status.update(config.job_name)
        logger.info(f"Running job: {config.job_name}")

        task = Task(
            job_id=config.job_id,
            source=source,
            description="Demo: Generate monthly report and notify stakeholders.",
            summary=override_text or "No summary provided.",
            created_at=datetime.utcnow().isoformat()
        )

        executor = SimpleExecutor()
        executor.execute(task)

        results = [{"description": task.description, "status": task.status or "pending"}]

        # ✅ Export like all other jobs
        dispatch_exports(
            output_data={
                "summary": task.summary,
                "tasks": [task.model_dump()],
                "job_id": config.job_id
            },
            destination_configs=config.export_destinations,
            job_name=config.job_name,
            metadata={
                "sender": "demo@company.com",
                "subject": "Test Export from DemoJob"
            }
        )

        # ✅ Report generation
        generate_demo_report(
            summary=task.summary,
            tasks=[task.model_dump()],
            results=results,
            job_id=config.job_id
        )

        return [task]

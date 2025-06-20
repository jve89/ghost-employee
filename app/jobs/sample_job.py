"""
🚀 Full Pipeline Demo Job
This job demonstrates the complete Ghost Employee pipeline:
- Summarisation via GPT
- Task extraction via GPT
- Task execution
- Exporting results
"""

import time
from datetime import datetime
from app.core.models import JobConfig, Task
from app.core.interfaces import Summariser, TaskParser
from infrastructure.summariser.gpt_summariser import GPTSummariser
from infrastructure.task_parser.gpt_parser import GPTTaskParser
from app.services.executor_service import execute_task
from infrastructure.logger.memory_logger import logger
from infrastructure.logger.job_status import job_status
from infrastructure.logger.job_timesheet import log_job_run
from app.services.export_dispatcher import dispatch_exports
from app.services.demo_report_generator import generate_demo_report



class SampleJob:
    def __init__(self):
        self.summariser: Summariser = GPTSummariser()
        self.parser: TaskParser = GPTTaskParser()

    def run(self, config: JobConfig, override_text: str | None = None, source: str = "unknown") -> list[Task]:
        job_status.update(config.job_name)
        logger.info(f"Running job: {config.job_name}")

        input_text = override_text or "Log project update to Google Sheets: The system is now fully operational. Assigned to Johan. Due next Tuesday."

        summary = self.summariser.summarise(
            text=input_text,
            source_file=source,
            preferences={"sender": "unknown", "subject": "N/A"}
        )

        summary_text = summary.content

        # ✅ Manually define a single task
        task = Task(
            description="Create intern onboarding sheet",
            entity="Lisa",
            assignee="HR Team",
            job_id=config.job_id,
            source=source,
            summary=summary_text,
            created_at=datetime.utcnow().isoformat()
        )

        start = time.time()

        execute_task(task)

        task_list = [task]
        task_results = [(task, {"status": task.status})]

        # (task execution)

        duration = round(time.time() - start, 2)
        log_job_run(
            job_name=config.job_name,
            summary=summary_text,
            tasks_executed=len(task_results),
            status="success",
            duration_seconds=duration,
            tasks=[task.model_dump() for task in task_list]
        )


        dispatch_exports(
            output_data={
                "summary": summary_text,
                "tasks": [task.model_dump() for task in task_list],
                "job_id": config.job_id
            },
            destination_configs=config.export_destinations,
            job_name=config.job_name,
            metadata={
                "sender": "noreply@company.com",
                "subject": f"{config.job_name} Triggered Export"
            }
        )

        generate_demo_report(
            summary=summary_text,
            tasks=[task.model_dump() for task in task_list],
            results=[{"description": task.description, "status": task.status or "pending"} for task in task_list],
            job_id=config.job_name,
            to_pdf=False
        )

        return task_results


if __name__ == "__main__":
    job_config = load_job_config("sample_job")
    SampleJob().run(job_config)

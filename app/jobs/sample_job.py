# app/jobs/sample_job.py

"""
🚀 Full Pipeline Demo Job
This job demonstrates the complete Ghost Employee pipeline:
- Summarisation via GPT
- Task extraction via GPT
- Task execution
- Exporting results
"""
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
from config.config_loader import load_job_config


class SampleJob:
    def __init__(self):
        self.summariser: Summariser = GPTSummariser()
        self.parser: TaskParser = GPTTaskParser()

    def run(self, config: JobConfig, override_text: str | None = None, source: str = "unknown") -> list[Task]:
        job_status.update(config.job_name)
        logger.info(f"Running job: {config.job_name}")

        input_text = override_text or "Client requested a weekly performance report. Deadline is next Friday. Assigned to Lisa."
        summary = self.summariser.summarise(input_text, source)

        # ✅ Manually define a single task
        task = Task(
            description="Update contact Alice",
            entity="Alice",
            job_id=config.job_id,
            source=source,
            summary=summary.content,
            created_at=datetime.utcnow().isoformat()
        )

        # ✅ Execute and collect result
        execute_task(task)

        # For dispatch and reporting, use just Task list
        task_list = [task]

        # For custom tuple-based functions like export report
        task_results = [(task, {"status": task.status})]

        # ✅ Continue pipeline
        log_job_run(
            job_name=config.job_name,
            summary=summary.content,
            tasks_executed=len(task_results),
            status="success"
        )

        dispatch_exports(
            output_data={
                "summary": summary.content,
                "tasks": [task.dict() for task in task_list],
            },
            destination_configs=config.export_destinations,
            job_name=config.job_name
        )

        generate_demo_report(
            summary=summary.content,
            tasks=[task.dict() for task in task_list],
            results=[{"description": task.description, "status": task.status or "pending"} for task in task_list],
            job_id=config.job_name,
            to_pdf=False
        )

        return task_results


if __name__ == "__main__":
    job_config = load_job_config("sample_job")
    SampleJob().run(job_config)

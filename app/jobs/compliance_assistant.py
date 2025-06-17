# app/jobs/compliance_assistant.py

"""
✅ Compliance Assistant Job
This job mimics a compliance officer reviewing regulatory communications
and extracting actionable compliance items for tracking and reporting.
"""

import time
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


class ComplianceAssistantJob:
    def __init__(self):
        self.summariser: Summariser = GPTSummariser()
        self.parser: TaskParser = GPTTaskParser()

    def run(self, config: JobConfig, override_text: str | None = None, source: str = "unknown") -> list[Task]:
        job_status.update(config.job_name)
        logger.info(f"Running job: {config.job_name}")

        input_text = override_text or (
            "We received an update from the EU regulator regarding new AML reporting thresholds. "
            "The new limit is €5,000 and effective immediately. The compliance team must ensure internal policies reflect this change, "
            "and notify the finance department to update customer verification procedures."
        )

        summary = self.summariser.summarise(
            text=input_text,
            source_file=source,
            preferences={"sender": "unknown", "subject": "N/A"}
        )

        summary_text = summary.content  # ✅ Safely extract summary string

        tasks = self.parser.extract_tasks(summary, config.job_id)

        start = time.time()

        for task in tasks:
            execute_task(task)
        duration = round(time.time() - start, 2)
        
        log_job_run(
            job_name=config.job_name,
            summary=summary_text,
            tasks_executed=len(tasks),
            status="success",
            duration=duration,
            tasks=[task.model_dump() for task in tasks]
        )

        dispatch_exports(
            output_data={
                "summary": summary_text,  # ✅ Pass as string
                "tasks": [task.model_dump() for task in tasks],
                "job_id": config.job_id
            },
            destination_configs=config.export_destinations,
            job_name=config.job_name,
            metadata={
                "sender": "compliance@company.com",
                "subject": "Regulatory Update: AML Thresholds"
            }
        )

        generate_demo_report(
            summary=summary_text,  # ✅ Use same string
            tasks=[task.model_dump() for task in tasks],
            results=[{"description": task.description, "status": task.status or "pending"} for task in tasks],
            job_id=config.job_name
        )

        return tasks


if __name__ == "__main__":
    config = load_job_config("compliance_assistant")
    ComplianceAssistantJob().run(config)

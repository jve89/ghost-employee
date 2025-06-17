"""
💼 Data Entry Specialist Job
This job simulates a junior assistant who updates spreadsheets, CRM tools,
or internal records based on instructions received via email or chat.
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


class DataEntrySpecialistJob:
    def __init__(self):
        self.summariser: Summariser = GPTSummariser()
        self.parser: TaskParser = GPTTaskParser()

    def run(self, config: JobConfig, override_text: str | None = None, source: str = "unknown") -> list[Task]:
        job_status.update(config.job_name)
        logger.info(f"Running job: {config.job_name}")

        input_text = override_text or (
            "Hi team, please update our records. We have a new client: Alice Johnson, Company: Acme Corp, Email: alice@acme.com. "
            "Add this info to the CRM and make sure her onboarding form is filled out. Set her up for the Tuesday orientation."
        )

        summary = self.summariser.summarise(
            text=input_text,
            source_file=source,
            preferences={"sender": "unknown", "subject": "N/A"}
        )

        summary_text = summary.content

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
                "summary": summary_text,
                "tasks": [task.model_dump() for task in tasks],
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
            tasks=[task.model_dump() for task in tasks],
            results=[{"description": task.description, "status": task.status or "pending"} for task in tasks],
            job_id=config.job_name
        )

        return tasks


if __name__ == "__main__":
    config = load_job_config("data_entry_specialist")
    DataEntrySpecialistJob().run(config)

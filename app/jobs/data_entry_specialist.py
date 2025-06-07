# app/jobs/data_entry_specialist.py

"""
💼 Data Entry Specialist Job
This job simulates a junior assistant who updates spreadsheets, CRM tools,
or internal records based on instructions received via email or chat.
"""

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
        print("✅ Parsed export_destinations =", config.export_destinations)
        print("✅ Type of first item =", type(config.export_destinations[0]) if config.export_destinations else "None")

        input_text = override_text or (
            "Hi team, please update our records. We have a new client: Alice Johnson, Company: Acme Corp, Email: alice@acme.com. "
            "Add this info to the CRM and make sure her onboarding form is filled out. Set her up for the Tuesday orientation."
        )

        summary = self.summariser.summarise(input_text, source)
        tasks = self.parser.extract_tasks(summary, config.job_id)

        for task in tasks:
            execute_task(task)

        log_job_run(
            job_name=config.job_name,
            summary=summary.content,
            tasks_executed=len(tasks),
            status="success"
        )

        dispatch_exports(
            output_data={
                "summary": summary.content,
                "tasks": [task.model_dump() for task in tasks],
            },
            destination_configs=config.export_destinations,
            job_name=config.job_name
        )

        generate_demo_report(
            summary=summary.content,
            tasks=[task.model_dump() for task in tasks],
            results=[{"description": task.description, "status": task.status or "pending"} for task in tasks],
            job_id=config.job_name
        )

        return tasks


if __name__ == "__main__":
    config = load_job_config("data_entry_specialist")
    DataEntrySpecialistJob().run(config)

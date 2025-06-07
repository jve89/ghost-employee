# app/jobs/crm_ops_job.py

"""
👩‍💼 CRM Operations Assistant
Simulates a virtual assistant handling CRM updates from notes/emails.
"""

from datetime import datetime
from app.core.models import JobConfig, Task
from app.core.interfaces import Summariser, TaskParser
from app.core.crm_prefs_memory import CRMPrefsMemory
from infrastructure.summariser.gpt_summariser import GPTSummariser
from infrastructure.task_parser.gpt_parser import GPTTaskParser
from app.services.executor_service import execute_task
from infrastructure.logger.memory_logger import logger
from infrastructure.logger.job_status import job_status
from infrastructure.logger.job_timesheet import log_job_run
from app.services.export_dispatcher import dispatch_exports
from config.config_loader import load_job_config

class CRMOperationsJob:
    def __init__(self):
        self.summariser: Summariser = GPTSummariser()
        self.parser: TaskParser = GPTTaskParser()

    def run(self, config: JobConfig, override_text: str | None = None, source: str = "crm_notes.txt") -> list[Task]:
        job_status.update(config.job_name)
        logger.info(f"Running job: {config.job_name}")

        # 🧠 Load job-specific preferences
        prefs = CRMPrefsMemory(config.job_name).get_preferences()
        logger.info(f"Loaded preferences: {prefs}")

        # 👂 Simulated input for now (could later be file/email content)
        input_text = override_text or """
            Add Alice to CRM as a new contact. She's our new point of contact at Acme Corp.
            Also update Bob's contact details — his phone number changed.
        """

        summary_obj = self.summariser.summarise(
            text=input_text,
            source_file=source,
            preferences=prefs
        )

        tasks = self.parser.extract_tasks(
            summary=summary_obj,
            job_id=config.job_id,
            preferences=prefs
        )

        task_results = []

        for task in tasks:
            execute_task(task)
            task_results.append((task, {"status": task.status}))

        log_job_run(
            job_name=config.job_name,
            summary=summary_obj.content,
            tasks_executed=len(task_results),
            status="success"
        )

        dispatch_exports(
            output_data={
                "summary": summary_obj.content,
                "tasks": [task.model_dump() for task in tasks],
            },
            destination_configs=config.export_destinations,
            job_name=config.job_name
        )

        return task_results


if __name__ == "__main__":
    job_config = load_job_config("crm_ops_job")
    CRMOperationsJob().run(job_config)

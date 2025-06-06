# app/jobs/compliance_analyst.py

"""
✅ Compliance Analyst Job
This job mimics a compliance officer reviewing regulatory communications
and extracting actionable compliance items for tracking and reporting.
"""

from app.core.models import JobConfig, Task
from app.core.interfaces import Summariser, TaskParser, Executor
from infrastructure.summariser.gpt_summariser import GPTSummariser
from infrastructure.task_parser.gpt_parser import GPTTaskParser
from infrastructure.executor.task_executor import SimpleExecutor
from infrastructure.logger.memory_logger import logger
from infrastructure.logger.job_status import job_status
from infrastructure.logger.job_timesheet import log_job_run
from app.services.export_service import ExportService
from app.services.demo_report_generator import generate_demo_report
from config.config_loader import load_job_config


class ComplianceAnalystJob:
    def __init__(self):
        self.summariser: Summariser = GPTSummariser()
        self.parser: TaskParser = GPTTaskParser()
        self.executor: Executor = SimpleExecutor()

    def run(self, config: JobConfig, override_text: str | None = None, source: str = "unknown") -> list[Task]:
        job_status.update(config.job_name)
        logger.log(f"Running job: {config.job_name}")

        input_text = override_text or (
            "We received an update from the EU regulator regarding new AML reporting thresholds. "
            "The new limit is €5,000 and effective immediately. The compliance team must ensure internal policies reflect this change, "
            "and notify the finance department to update customer verification procedures."
        )

        summary = self.summariser.summarise(input_text, source)
        tasks = self.parser.extract_tasks(summary, config.job_id)

        for task in tasks:
            self.executor.execute(task)

        log_job_run(
            job_name=config.job_name,
            summary=summary.content,
            tasks_executed=len(tasks),
            status="success"
        )

        service = ExportService(config)
        for task in tasks:
            service.export(task)

        results = [{"description": task.description, "status": task.status or "pending"} for task in tasks]

        generate_demo_report(
            summary=summary.content,
            tasks=[task.dict() for task in tasks],
            results=results,
            job_id=config.job_name
        )

        return tasks


if __name__ == "__main__":
    config = load_job_config("compliance_analyst")
    ComplianceAnalystJob().run(config)

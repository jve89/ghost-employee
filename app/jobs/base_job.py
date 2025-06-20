# app/jobs/base_job.py

import os
from infrastructure.summariser.gpt_summariser import GPTSummariser
from infrastructure.task_parser.gpt_parser import GPTTaskParser
from infrastructure.executor.task_executor import execute_task
from infrastructure.logger.activity_log import log_event
from app.services.export_dispatcher import export_data

class BaseJob:
    def __init__(self, config: dict):
        self.config = config
        self.job_id = config.get("job_id", "unknown_job")
        self.job_name = config.get("job_name", "Unnamed Job")
        self.export_destinations = config.get("export_destinations", [])

    def run(self, file_path: str):
        try:
            log_event(f"Running job: {self.job_name}")

            text = self.preprocess_input(file_path)
            summary = self.generate_summary(text)
            tasks = self.extract_tasks(summary)
            results = self.execute_tasks(tasks)

            export_data(
                summary=summary,
                tasks=tasks,
                job_id=self.job_id,
                export_destinations=self.export_destinations
            )

            log_event(f"✅ Job '{self.job_name}' completed.")
        except Exception as e:
            log_event(f"❌ Job '{self.job_name}' failed: {e}")

    def preprocess_input(self, file_path: str) -> str:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()

    def generate_summary(self, text: str) -> str:
        summariser = GPTSummariser()
        return summariser.summarise(text, source_file=self.job_id)  # or file_path if you prefer

    def extract_tasks(self, summary) -> list[dict]:
        parser = GPTTaskParser()
        return parser.extract_tasks(summary, job_id=self.job_id)

    def execute_tasks(self, tasks: list[dict]) -> list[dict]:
        results = []
        for task in tasks:
            result = execute_task(task)
            results.append(result)
        return results

from app.core.models import JobConfig
from app.core.interfaces import Summariser, TaskParser, Executor
from infrastructure.summariser.gpt_summariser import GPTSummariser
from infrastructure.task_parser.gpt_parser import GPTTaskParser
from infrastructure.executor.task_executor import SimpleExecutor
from infrastructure.logger.memory_logger import logger
from infrastructure.logger.job_status import job_status
from config.config_loader import load_job_config
from app.services.export_dispatcher import dispatch_exports

class SampleJob:
    def __init__(self):
        self.summariser: Summariser = GPTSummariser()
        self.parser: TaskParser = GPTTaskParser()
        self.executor: Executor = SimpleExecutor()

    def run(self, config: JobConfig, override_text: str = None, source: str = "manual_entry.txt"):
        job_status.update(config.job_name)
        logger.log(f"Running job: {config.job_name}")

        input_text = override_text or "Client requested a weekly performance report. Deadline is next Friday. Assigned to Lisa."

        summary = self.summariser.summarise(input_text, source)
        tasks = self.parser.extract_tasks(summary)

        for task in tasks:
            self.executor.execute(task)

        output_data = {
            "summary": summary.content,
            "tasks": [task.dict() for task in tasks],
            "assignee": tasks[0].assignee if tasks else None
        }

        dispatch_exports(output_data, config.export_destinations, config.job_name)

if __name__ == "__main__":
    job_config = load_job_config("sample_job")
    SampleJob().run(job_config)

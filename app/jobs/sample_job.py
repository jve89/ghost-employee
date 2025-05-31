from app.core.models import JobConfig
from app.core.interfaces import Summariser, TaskParser, Executor, Exporter
from infrastructure.summariser.gpt_summariser import GPTSummariser
from infrastructure.task_parser.gpt_parser import GPTTaskParser
from infrastructure.executor.task_executor import SimpleExecutor
from infrastructure.exporters.log_exporter import LogExporter
from infrastructure.logger.memory_logger import logger
from infrastructure.logger.job_status import job_status

class SampleJob:
    def __init__(self):
        self.summariser: Summariser = GPTSummariser()
        self.parser: TaskParser = GPTTaskParser()
        self.executor: Executor = SimpleExecutor()
        self.exporter: Exporter = LogExporter()

    def run(self, config: JobConfig, override_text: str = None, source: str = "manual_entry.txt"):
        job_status.update(config.job_name)
        logger.log(f"Running job: {config.job_name}")
        input_text = override_text or "Client requested a weekly performance report. Deadline is next Friday. Assigned to Lisa."
        summary = self.summariser.summarise(input_text, source)
        tasks = self.parser.extract_tasks(summary)
        for task in tasks:
            success = self.executor.execute(task)
            if success:
                self.exporter.export(task)
                logger.log(f"Task executed and exported: {task.description}")

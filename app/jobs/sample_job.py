from app.core.models import JobConfig
from app.core.interfaces import Summariser, TaskParser, Executor, Exporter
from infrastructure.summariser.gpt_summariser import GPTSummariser
from infrastructure.task_parser.gpt_parser import GPTTaskParser
from infrastructure.executor.task_executor import SimpleExecutor
from infrastructure.exporters.log_exporter import LogExporter
from infrastructure.logger.memory_logger import logger

class SampleJob:
    def __init__(self):
        self.summariser: Summariser = GPTSummariser()
        self.parser: TaskParser = GPTTaskParser()
        self.executor: Executor = SimpleExecutor()
        self.exporter: Exporter = LogExporter()

    def run(self, config: JobConfig):
        logger.log(f"Running job: {config.job_name}")
        dummy_text = "Client requested a weekly performance report. Deadline is next Friday. Assigned to Lisa."
        summary = self.summariser.summarise(dummy_text, "manual_entry.txt")
        tasks = self.parser.extract_tasks(summary)
        for task in tasks:
            self.executor.execute(task)
            self.exporter.export(task)
            logger.log(f"Task executed and exported: {task.description}")

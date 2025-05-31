from app.core.models import JobConfig
from app.core.interfaces import Summariser, TaskParser, Executor, Exporter
from infrastructure.summariser.gpt_summariser import GPTSummariser
from infrastructure.task_parser.gpt_parser import GPTTaskParser
from infrastructure.executor.task_executor import SimpleExecutor
from infrastructure.exporters.log_exporter import LogExporter

class SampleJob:
    def __init__(self):
        self.summariser: Summariser = GPTSummariser()
        self.parser: TaskParser = GPTTaskParser()
        self.executor: Executor = SimpleExecutor()
        self.exporter: Exporter = LogExporter()

    def run(self, config: JobConfig):
        print(f"Running job: {config.job_name}")
        # Placeholder for full logic pipeline (watch → summarise → extract → execute → export)

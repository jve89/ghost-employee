from app.core.models import Task, JobConfig
from infrastructure.summariser.gpt_summariser import GPTSummariser

class SummaryService:
    def __init__(self, config: JobConfig):
        self.config = config

    def summarise(self, task: Task) -> str:
        return f"[Summary] {task.description}"

    def generate_summaries(self, tasks: list[Task]) -> list[str]:
        return [self.summarise(task) for task in tasks]

def summarise_text(text: str) -> str:
    summariser = GPTSummariser()
    result = summariser.summarise(text, source_file="base_demo.txt")
    return result.content
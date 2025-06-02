from app.core.models import Task, JobConfig

class SummaryService:
    def __init__(self, config: JobConfig):
        self.config = config

    def summarise(self, task: Task) -> str:
        return f"[Summary] {task.description}"

    def generate_summaries(self, tasks: list[Task]) -> list[str]:
        return [self.summarise(task) for task in tasks]

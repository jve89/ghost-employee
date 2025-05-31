from app.core.models import Summary, Task
from app.core.interfaces import TaskParser

class GPTTaskParser(TaskParser):
    def extract_tasks(self, summary: Summary) -> list[Task]:
        print("[GPTTaskParser] Extracting tasks from summary...")
        return [
            Task(description="Sample task", source_summary=summary.content)
        ]

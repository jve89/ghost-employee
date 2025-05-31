from app.core.models import Task

class GPTTaskParser:
    def extract_tasks(self, summary: str) -> list[Task]:
        print("[GPTTaskParser] Extracting tasks from summary...")
        return [Task(description="Sample task")]

from app.core.models import Task, JobConfig
from app.services.task_parser import GPTTaskParser

class TaskService:
    def __init__(self, config: JobConfig):
        self.config = config

    def extract_tasks(self, summaries: list[str]) -> list[Task]:
        all_tasks = []
        parser = GPTTaskParser()

        for summary in summaries:
            try:
                parsed = parser.parse(summary)
                for item in parsed:
                    try:
                        if isinstance(item, str):
                            description = item
                            all_tasks.append(Task(description=description))
                        elif isinstance(item, dict):
                            description = (
                                item.get("description")
                                or item.get("task")
                                or item.get("title")
                                or str(item)
                            )
                            assignee = item.get("assignee") or item.get("assigned_to")
                            all_tasks.append(Task(description=description, assignee=assignee))
                        else:
                            description = str(item)
                            all_tasks.append(Task(description=description))
                    except Exception as e:
                        print(f"[TaskService] Invalid task item: {item} → {e}")
                        all_tasks.append(Task(description="Task parsing failed – manual review needed."))
            except Exception as e:
                print(f"[TaskService] Failed to parse summary: {e}")
                all_tasks.append(Task(description="Summary parsing failed – manual review needed."))

        return all_tasks

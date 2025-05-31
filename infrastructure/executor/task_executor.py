from app.core.models import Task
from app.core.interfaces import Executor

class SimpleExecutor(Executor):
    def execute(self, task: Task) -> bool:
        print(f"[SimpleExecutor] Executing task: {task.description}")
        return True

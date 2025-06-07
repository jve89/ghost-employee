# infrastructure/executor/task_executor.py

from app.core.models import Task
from app.core.interfaces import Executor
from app.services.executor_service import execute_task

class SimpleExecutor(Executor):
    def execute(self, task: Task) -> None:
        execute_task(task)

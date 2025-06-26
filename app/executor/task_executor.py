import logging
from typing import List

from app.core.task_model import Task 

logger = logging.getLogger(__name__)

class TaskExecutor:
    def __init__(self, job_id: str):
        self.job_id = job_id

    def execute_tasks(self, tasks: List[Task]):
        for task in tasks:
            self.execute(task)

    def execute(self, task: Task):
        logger.info(f"[{self.job_id}] 🛠 Executing task: {task.description}")

        # TODO: Add plugin routing logic here
        # For now, just simulate execution
        print(f"[{self.job_id}] ✅ Executed: {task.description}")

# app/executor/task_executor.py

import logging
from typing import List
from app.jobs.job_registry import get_job_class
from app.logs.task_log_store import append_task_log
from app.core.task_model import Task

logger = logging.getLogger(__name__)

class TaskExecutor:
    def __init__(self, job_id: str):
        self.job_id = job_id
        self.job_class = get_job_class(job_id)()

    def execute_tasks(self, tasks: List[Task]):
        for task in tasks:
            self.execute(task)

    def execute(self, task: Task):
        logger.info(f"[{self.job_id}] 🛠 Executing task: {task.description}")

        try:
            self.job_class.execute(task.description)
            print(f"[{self.job_id}] ✅ Executed: {task.description}")
            append_task_log(self.job_id, task.description, success=True)
        except Exception as e:
            print(f"[{self.job_id}] ❌ Failed to execute '{task.description}': {e}")
            append_task_log(self.job_id, task.description, success=False)

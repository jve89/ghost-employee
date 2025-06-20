# infrastructure/executor/task_executor.py

from app.core.models import Task
from app.core.interfaces import Executor
from app.services.executor_service import execute_task  # Fallback
from app.services.task_router import route_task
from infrastructure.logger.memory_logger import memory_logger

import logging
logger = logging.getLogger(__name__)

class SimpleExecutor(Executor):
    def execute(self, task: Task) -> None:
        if route_task(task):
            return

        # ❌ Nothing matched — use generic fallback
        message = "[SimpleExecutor] ❓ No plugin matched. Using generic executor."
        logger.info(message)
        memory_logger.log("Executor", message)
        execute_task(task)

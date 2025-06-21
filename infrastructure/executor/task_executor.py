# infrastructure/executor/task_executor.py

from app.core.models import Task
from app.core.interfaces import Executor
from app.services.executor_service import execute_task  # Fallback
from app.services.task_router import route_task
from infrastructure.logger.memory_logger import memory_logger

from app.plugins.hr_plugin import handle_hr_task  # 👈 NEW
from infrastructure.exporters.file_exporter import FileExporter  # 👈 NEW

import logging
logger = logging.getLogger(__name__)

class SimpleExecutor(Executor):
    def execute(self, task: Task) -> None:
        task_description = task.description

        # ✅ Route-based plugin (preferred)
        if route_task(task):
            return

        # 🔎 HR Plugin
        success, message, export_entry = handle_hr_task(task_description)
        logger.info(message)
        memory_logger.log("HRPlugin", message)
        if success:
            if export_entry:
                exporter = FileExporter(config={}, job_id="hr_assistant")
                exporter.export_data_block(export_entry)
            return

        # ❌ Fallback — use generic executor
        message = "[SimpleExecutor] ❓ No plugin matched. Using generic executor."
        logger.info(message)
        memory_logger.log("Executor", message)
        execute_task(task)

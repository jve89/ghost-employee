# app/services/executor_service.py

from app.core.models import Task
from app.plugins.file_ops import FileOpsPlugin
from app.plugins.crm_plugin import CRMPlugin
from infrastructure.logger.retry_queue import retry_queue
from datetime import datetime

ALL_PLUGINS = [
    FileOpsPlugin(),
    CRMPlugin(),
]


def execute_task(task: Task) -> None:
    print(f"[ExecutorService] Executing: {task.description}")
    task.executed_at = datetime.utcnow()

    try:
        for plugin in ALL_PLUGINS:
            if plugin.can_handle(task):
                result = plugin.handle(task)
                task.status = "success" if result else "failed"
                print(f"[ExecutorService] ✅ Plugin handled task. Success: {result}")
                return

        task.status = "skipped"
        print("[ExecutorService] ❌ No plugin could handle the task.")

    except Exception as e:
        task.status = "failed"
        retry_queue.add(task, reason=str(e))
        print(f"[ExecutorService] ❌ Failed: {e}")

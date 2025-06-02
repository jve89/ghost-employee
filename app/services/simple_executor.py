from app.core.models import Task
from infrastructure.logger.retry_queue import retry_queue
from datetime import datetime
from infrastructure.exporters.log_exporter import LogExporter

EXPORTER_MAP = {
    "logs": LogExporter
}

class SimpleExecutor:
    def execute(self, task: Task) -> bool:
        print(f"[SimpleExecutor] Executing task: {task.description}")

        # Fail only if description contains "fail"
        success = "fail" not in task.description.lower()

        if not success:
            print("[SimpleExecutor] Task failed and queued for retry.")
            retry_queue.add(task, datetime.utcnow().isoformat())
        else:
            print("[SimpleExecutor] Task succeeded and will be exported.")

        return success

from datetime import datetime
from app.core.models import Task
from app.core.interfaces import Executor
import random
from infrastructure.logger.retry_queue import retry_queue

class SimpleExecutor(Executor):
    def execute(self, task: Task) -> bool:
        print(f"[SimpleExecutor] Executing task: {task.description}")

        task.executed_at = datetime.utcnow()  # ✅ New timestamp for realism

        if random.random() < 0.2:
            task.status = "failed"
            retry_queue.add(task, reason="Simulated execution failure")
            print("[SimpleExecutor] Task failed and queued for retry.")
            return False

        task.status = "success"
        return True

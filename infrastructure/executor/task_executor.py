from app.core.models import Task
from app.core.interfaces import Executor
import random
from infrastructure.logger.retry_queue import retry_queue

class SimpleExecutor(Executor):
    def execute(self, task: Task) -> bool:
        print(f"[SimpleExecutor] Executing task: {task.description}")

        # Simulate failure randomly
        if random.random() < 0.2:
            retry_queue.add(task, reason="Simulated execution failure")
            print("[SimpleExecutor] Task failed and queued for retry.")
            return False

        return True

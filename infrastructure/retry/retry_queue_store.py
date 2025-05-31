from infrastructure.logger.retry_queue import retry_queue
from app.core.models import Task
from app.services.simple_executor import SimpleExecutor
import uuid

class RetryQueueStore:
    def __init__(self):
        self.queue = []

    def get_all(self):
        return self.queue

    def add(self, task: Task, timestamp: str):
        task_entry = {
            "id": str(uuid.uuid4()),  # ✅ Add unique ID here
            "task": task.model_dump(),
            "timestamp": timestamp
        }
        self.queue.append(task_entry)

    def retry_all(self):
        for entry in list(self.queue):
            task = Task(**entry["task"])
            success = SimpleExecutor().execute(task)
            if success:
                self.queue.remove(entry)

# ✅ Singleton instance
retry_queue_store = RetryQueueStore()

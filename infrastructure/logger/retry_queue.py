from app.core.models import Task
from datetime import datetime
import uuid

class RetryQueue:
    def __init__(self):
        self.queue = []

    def add(self, task: Task, reason: str):
        self.queue.append({
            "id": str(uuid.uuid4()),
            "timestamp": datetime.utcnow().isoformat(),
            "task": task.model_dump(),
            "reason": reason
        })
        if len(self.queue) > 500:
            self.queue = self.queue[-250:]

    def all(self):
        return self.queue

    def get(self, retry_id: str):
        return next((item for item in self.queue if item["id"] == retry_id), None)

    def remove(self, retry_id: str):
        self.queue = [item for item in self.queue if item["id"] != retry_id]

retry_queue = RetryQueue()

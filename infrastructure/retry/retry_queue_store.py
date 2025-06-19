import os
import json
import uuid
from typing import List
from datetime import datetime
from app.core.models import Task

RETRY_QUEUE_FILE = "logs/retry_queue.json"

class RetryQueueStore:
    def __init__(self):
        self.queue = []
        self._load_from_disk()

    def _load_from_disk(self):
        if os.path.exists(RETRY_QUEUE_FILE):
            with open(RETRY_QUEUE_FILE, "r") as f:
                self.queue = json.load(f)
        else:
            self.queue = []

    def _save_to_disk(self):
        os.makedirs(os.path.dirname(RETRY_QUEUE_FILE), exist_ok=True)
        with open(RETRY_QUEUE_FILE, "w") as f:
            json.dump(self.queue, f, indent=2)

    def get_all(self) -> List[dict]:
        return self.queue

    def add(self, task: Task, timestamp: str):
        task_entry = {
            "id": str(uuid.uuid4()),
            "task": task.model_dump(),
            "timestamp": timestamp
        }
        self.queue.append(task_entry)
        self._save_to_disk()

# ✅ Singleton instance
retry_queue_store = RetryQueueStore()

def get_retry_queue():
    return retry_queue_store.get_all()

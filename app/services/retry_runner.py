# app/services/retry_runner.py

from app.core.models import Task
from app.services.simple_executor import SimpleExecutor
from infrastructure.retry.retry_queue_store import retry_queue_store

def retry_all_tasks():
    for entry in list(retry_queue_store.queue):
        task = Task(**entry["task"])
        success = SimpleExecutor().execute(task)
        if success:
            retry_queue_store.queue.remove(entry)
    retry_queue_store._save_to_disk()

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

def retry_task_by_id(task_id: str) -> str:
    from infrastructure.retry_queue_store import load_retry_queue, save_retry_queue
    from app.services.task_dispatcher import dispatch_task

    queue = load_retry_queue()
    remaining = []
    retried = False

    for entry in queue:
        if entry["id"] == task_id:
            dispatch_task(entry["task"])
            retried = True
        else:
            remaining.append(entry)

    save_retry_queue(remaining)
    return f"✅ Task {task_id} retried." if retried else f"⚠️ Task ID {task_id} not found."

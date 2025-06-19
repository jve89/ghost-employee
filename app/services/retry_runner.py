# app/services/retry_runner.py

from app.core.models import Task
from app.core.registry import get_job_config
from app.services.simple_executor import SimpleExecutor
from infrastructure.retry.retry_queue_store import retry_queue_store

def retry_all_tasks():
    for entry in list(retry_queue_store.queue):
        try:
            task = Task(**entry["task"])
            success = SimpleExecutor().execute(task)
            if success:
                retry_queue_store.queue.remove(entry)
        except Exception as e:
            print(f"❌ Retry failed for one entry: {e}")
    retry_queue_store._save_to_disk()

def retry_task_by_id(task_id: str) -> str:
    print(f"🔍 Attempting to retry task with ID: {task_id}")
    matched = None

    for entry in list(retry_queue_store.queue):
        print(f"🔎 Checking entry ID: {entry.get('id')}")
        if entry["id"] == task_id:
            matched = entry
            break

    if not matched:
        print("❌ No matching task found.")
        return f"⚠️ Task ID {task_id} not found."

    if "task" not in matched:
        print("❌ Retry entry is missing the 'task' field.")
        return f"❌ Retry failed — 'task' field missing from entry."

    try:
        task = Task(**matched["task"])
    except Exception as e:
        print(f"❌ Failed to reconstruct Task: {e}")
        return f"❌ Retry failed — task reconstruction error: {e}"

    print(f"✅ Task object loaded: {task}")

    try:
        config = get_job_config(task.job_id)
    except Exception as e:
        print(f"❌ Could not load job config for '{task.job_id}': {e}")
        return f"❌ Retry failed — missing config for job_id '{task.job_id}'"

    print(f"🚀 Executing task with job config...")
    success = SimpleExecutor().execute(task, config)
    print(f"🎯 Execution result: {success}")

    if success:
        print("✅ Task succeeded. Removing from retry queue...")
        retry_queue_store.queue.remove(matched)
        retry_queue_store._save_to_disk()
        return f"✅ Task {task_id} executed and removed."
    else:
        print("❌ Task execution failed.")
        return f"❌ Task {task_id} execution failed."
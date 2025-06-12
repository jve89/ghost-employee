# retry_failed_tasks.py

import os
from dotenv import load_dotenv
from datetime import datetime
from app.core.models import Task
from infrastructure.exporters.notion_exporter import NotionExporter
from infrastructure.retry.retry_queue_store import retry_queue_store

load_dotenv()

# Optional: You can hardcode or dynamically fetch config here
job_id = "retry_handler"
notion_exporter = NotionExporter(config={}, job_id=job_id)

def run_retry_handler():
    queue = retry_queue_store.get_all()
    if not queue:
        print("[RetryHandler] ✅ No failed tasks to retry.")
        return

    print(f"[RetryHandler] 🔁 Retrying {len(queue)} failed task(s)...")
    remaining_queue = []

    for item in queue:
        try:
            task_data = item["task"]
            task_obj = Task(**task_data)
            output_data = {
                "summary": task_obj.description,
                "source_file": "retry_queue",
                "tasks": [task_data],
            }
            notion_exporter.export(output_data=output_data, config={})
        except Exception as e:
            print(f"[RetryHandler] ❌ Failed to retry task: {e}")
            remaining_queue.append(item)

    # Save only the failed retries back to disk
    retry_queue_store.queue = remaining_queue
    retry_queue_store._save_to_disk()
    print(f"[RetryHandler] ✅ Retry run complete. Remaining: {len(remaining_queue)} task(s).")

if __name__ == "__main__":
    run_retry_handler()

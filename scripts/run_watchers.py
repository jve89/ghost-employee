import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import json
from app.executor.task_executor import TaskExecutor
from app.core.task_model import Task
from app.watchers.file_watcher import FileWatcher
from app.jobs.job_registry import get_job_class
from config.app_config import load_job_config
from app.parser.rule_parser import extract_tasks_from_text

def handle_file(file_path: str):
    print(f"[Watcher Triggered] File received: {file_path}")

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        tasks_text = extract_tasks_from_text(content)
        tasks = [Task(description=t) for t in tasks_text]

        print(f"[Parser] 🧠 Extracted {len(tasks)} task(s):")
        for task in tasks:
            print(f" - {task.description}")

        executor = TaskExecutor(job_id="compliance_assistant")
        executor.execute_tasks(tasks)

    except Exception as e:
        print(f"[Handler Error] ❌ Failed to process {file_path}: {e}")

def main():
    print("[Runner] 🚀 Starting compliance job watcher...")

    job_id = "compliance_assistant"
    config = load_job_config(job_id)

    watch_dir = config["watch_dir"]
    file_pattern = config.get("file_pattern", "*.txt")
    interval = config.get("run_interval_seconds", 60)

    watcher = FileWatcher(watch_dir, file_pattern)
    watcher.watch(callback=handle_file, interval=interval)

if __name__ == "__main__":
    main()

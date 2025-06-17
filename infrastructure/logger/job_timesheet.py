import glob
import os
import json
import tempfile
import shutil
from datetime import datetime

task_log = []  # In-memory store of recent task activity

def log_job_run(job_name: str, summary: str, tasks_executed: int, status: str, tasks: list[dict] = None, duration_seconds: float = 0.0):
    log_dir = "logs/timesheets"
    os.makedirs(log_dir, exist_ok=True)

    path = os.path.join(log_dir, f"{job_name}_timesheet.json")

    # Try to load existing log data
    try:
        with open(path, "r") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        data = []

    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "job": job_name,
        "summary": str(summary),
        "tasks_executed": tasks_executed,
        "status": status,
        "duration_seconds": round(duration_seconds, 2)
    }
    data.append(entry)

    # Safely write using a temporary file
    with tempfile.NamedTemporaryFile("w", delete=False, dir=log_dir, suffix=".tmp") as tf:
        json.dump(data, tf, indent=2)
        temp_path = tf.name

    shutil.move(temp_path, path)

    # ✅ Preserve live task logging
    if tasks:
        for task in tasks:
            task_log.append({
                "timestamp": datetime.utcnow().isoformat(),
                "job_name": job_name,
                "task": task.get("instruction") or task.get("title"),
                "status": task.get("status", "unknown")
            })
        del task_log[:-50]

def get_timesheet_data() -> list[dict]:
    all_data = []
    for file in glob.glob("logs/timesheets/*_timesheet.json"):
        job = os.path.basename(file).replace("_timesheet.json", "")
        with open(file) as f:
            try:
                entries = json.load(f)
                for e in entries:
                    e["job"] = job  # 🔗 Inject job name
                    all_data.append(e)
            except Exception:
                continue
    return all_data

def get_recent_tasks(limit: int = 20):
    return list(reversed(task_log[-limit:]))

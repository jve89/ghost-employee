import os
import json
import tempfile
import shutil
from datetime import datetime

def log_job_run(job_name: str, summary: str, tasks_executed: int, status: str):
    log_dir = "logs/timesheets"
    os.makedirs(log_dir, exist_ok=True)

    path = os.path.join(log_dir, f"{job_name}_timesheet.json")

    # Try to load existing log data
    try:
        with open(path, "r") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        data = []

    # Add the new entry
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "job": job_name,
        "summary": str(summary),
        "tasks_executed": tasks_executed,
        "status": status
    }
    data.append(entry)

    # Safely write using a temporary file
    with tempfile.NamedTemporaryFile("w", delete=False, dir=log_dir, suffix=".tmp") as tf:
        json.dump(data, tf, indent=2)
        temp_path = tf.name

    shutil.move(temp_path, path)

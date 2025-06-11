# infrastructure/logger/export_status_log.py

import os
import json
from datetime import datetime

EXPORT_LOG_PATH = "./logs/export_status.json"

def log_export_status(job_name: str, destination_type: str, success: bool, details: dict):
    os.makedirs(os.path.dirname(EXPORT_LOG_PATH), exist_ok=True)

    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "job_name": job_name,
        "destination": destination_type,
        "success": success,
        "details": details
    }

    # Append to existing JSON array or create new file
    if os.path.exists(EXPORT_LOG_PATH):
        with open(EXPORT_LOG_PATH, "r") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = []
    else:
        data = []

    data.append(log_entry)

    with open(EXPORT_LOG_PATH, "w") as f:
        json.dump(data, f, indent=2, default=str)

    print(f"[EXPORT LOG] {destination_type.upper()} export {'succeeded' if success else 'failed'}")

import os
import json
from datetime import datetime

class JobStatusStore:
    def __init__(self):
        self.status = {}

    def update(self, job_name: str):
        self.status[job_name] = datetime.utcnow().isoformat()

    def get_all(self):
        return self.status

job_status = JobStatusStore()

# 🔍 New function to feed dashboard with recent export activity
LOG_FILE = "logs/export_status.json"

def get_recent_activity(limit=10):
    if not os.path.exists(LOG_FILE):
        return []

    with open(LOG_FILE, "r") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            return []

    # Sort by newest first
    sorted_data = sorted(data, key=lambda x: x.get("timestamp", ""), reverse=True)
    return sorted_data[:limit]

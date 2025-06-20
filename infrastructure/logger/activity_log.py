import json
from datetime import datetime
from typing import List, Dict

LOG_FILE = "logs/activity_log.json"
MAX_ENTRIES = 100

class ActivityLog:
    def __init__(self):
        self.entries: List[Dict] = []
        self._load()

    def _load(self):
        try:
            with open(LOG_FILE, "r") as f:
                self.entries = json.load(f)
        except FileNotFoundError:
            self.entries = []

    def _save(self):
        with open(LOG_FILE, "w") as f:
            json.dump(self.entries[-MAX_ENTRIES:], f, indent=2)

    def record(self, job_name: str, trigger: str, file: str = None, status: str = "started"):
        entry = {
            "job_name": job_name,
            "trigger": trigger,  # "watcher" or "interval"
            "file": file,
            "status": status,
            "timestamp": datetime.utcnow().isoformat()
        }
        self.entries.append(entry)
        self._save()

    def get_recent(self, count: int = 20) -> List[Dict]:
        return self.entries[-count:]

activity_log = ActivityLog()

def log_event(message: str):
    # Minimal shim to keep legacy jobs compatible
    activity_log.record(
        job_name="system",
        trigger="manual",
        file=None,
        status=message
    )

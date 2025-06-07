import os
import json
from datetime import datetime
from pathlib import Path

MEMORY_DIR = "memory"
os.makedirs(MEMORY_DIR, exist_ok=True)

class JobMemory:
    def __init__(self, job_name: str):
        self.job_name = job_name
        self.file_path = os.path.join(MEMORY_DIR, f"{job_name}.json")
        self.data = self._load()

    def _load(self):
        if not os.path.exists(self.file_path):
            return {
                "history": [],
                "preferences": {
                    "tone": "neutral",
                    "priority_keywords": []
                },
                "last_updated": None
            }
        with open(self.file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def save(self):
        self.data["last_updated"] = datetime.utcnow().isoformat()
        with open(self.file_path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2)

    def append_entry(self, subject: str, summary: str, tasks: list, from_email: str):
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "subject": subject,
            "summary": summary,
            "tasks": tasks,
            "from": from_email
        }
        self.data["history"].append(entry)
        # Keep only last 5 entries
        self.data["history"] = self.data["history"][-5:]
        self.save()

    def get_last_summary(self):
        if self.data["history"]:
            return self.data["history"][-1].get("summary")
        return None

    def get_preferences(self):
        return self.data.get("preferences", {})

    def set_preferences(self, new_prefs: dict):
        self.data["preferences"] = new_prefs
        self.save()

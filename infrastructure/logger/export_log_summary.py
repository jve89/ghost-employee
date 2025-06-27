import os
import json
from typing import List

EXPORT_LOG_PATH = "app/logs/export_log.json"  # Update path if needed

def get_latest_exports(limit: int = 5) -> List[dict]:
    if not os.path.exists(EXPORT_LOG_PATH):
        return []

    with open(EXPORT_LOG_PATH, "r") as f:
        try:
            logs = json.load(f)
        except json.JSONDecodeError:
            return []

    logs.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    return logs[:limit]

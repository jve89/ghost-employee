# infrastructure/logger/export_log.py

from app.core.models import ExportResult
from datetime import datetime

class ExportLogStore:
    def __init__(self):
        self.logs: list[dict] = []  # Changed to dict to track metadata

    def add(self, result: ExportResult):
        entry = result.dict()
        entry.setdefault("retry_count", 0)
        entry.setdefault("retry_origin", None)
        self.logs.append(entry)

        if len(self.logs) > 1000:
            self.logs = self.logs[-500:]

    def get_logs(self) -> list[dict]:
        return self.logs

    def increment_retry(self, entry_id: str, origin: str):
        for entry in self.logs:
            if entry["id"] == entry_id:
                entry["retry_count"] = entry.get("retry_count", 0) + 1
                entry["retry_origin"] = origin
                break

export_log = ExportLogStore()

def retry(entry_id: str) -> bool:
    from infrastructure.retry.retry_queue_store import retry_queue_store
    logs = export_log.get_logs()

    entry = next((log for log in logs if log["id"] == entry_id), None)
    if not entry or entry.get("success"):
        return False

    # ✅ Step 2: Reject if retry limit reached
    if entry.get("retry_count", 0) >= 3:
        return False

    retry_queue_store.add({
        "job_name": entry["job_name"],
        "task": entry.get("details", {}).get("task", {}),
        "timestamp": entry["timestamp"],
        "id": entry_id,
        "origin": "export_log_retry",
        "retry_count": entry.get("retry_count", 0) + 1
    })

    export_log.increment_retry(entry_id, origin="export_log_retry")
    return True

def log_export(job_name, destination, success, details, retry_origin=None, retry_count=0, sender=None, subject=None):
    entry = {
        "timestamp": datetime.now().isoformat(),
        "job_name": job_name,
        "destination": destination,
        "success": success,
        "details": details,
        "retry_origin": retry_origin,
        "retry_count": retry_count,
        "sender": sender,
        "subject": subject,
    }
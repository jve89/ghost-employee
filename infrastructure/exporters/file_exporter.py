import os
from datetime import datetime
from app.core.interfaces import Exporter
from app.core.models import Task

class FileExporter(Exporter):
    def __init__(self, directory: str = "./exports/sample_job/"):
        self.directory = directory
        os.makedirs(self.directory, exist_ok=True)

    def export(self, task: Task) -> None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        job_label = getattr(task, "job_name", "unknown_job")
        filename = f"{job_label}_{timestamp}.txt"
        filepath = os.path.join(self.directory, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"🕒 Created at: {task.created_at}\n")
            f.write(f"📄 Source: {task.source}\n")
            f.write(f"📌 Description: {task.description}\n\n")
            f.write(f"📝 Summary:\n{task.summary}\n")

        print(f"[FileExporter] ✅ Exported task to {filepath}")

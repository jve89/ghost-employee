import os
from datetime import datetime
from app.core.interfaces import Exporter
from app.core.models import Task

class FileExporter(Exporter):
    def __init__(self, job_id: str, base_dir: str = "./exports/"):
        self.directory = os.path.join(base_dir, job_id)
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

    def export_all(self, summary: str, tasks: list[Task], execution_results: list[dict]) -> None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"summary_{timestamp}.txt"
        filepath = os.path.join(self.directory, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"📝 Summary:\n{summary}\n\n")
            f.write("📋 Tasks:\n")
            for task in tasks:
                f.write(f"- {task.description} (Assigned: {task.assignee or 'Unassigned'})\n")
            f.write("\n✅ Execution Results:\n")
            for result in execution_results:
                status = result.get("status", "unknown")
                f.write(f"- {result['task']}: {status}\n")

        print(f"[FileExporter] 📄 Full export saved to {filepath}")

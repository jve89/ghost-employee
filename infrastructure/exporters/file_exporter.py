import os
import json
from datetime import datetime
from app.core.interfaces import Exporter
from app.core.models import Task
from pydantic.json import pydantic_encoder

class FileExporter(Exporter):
    def __init__(self, config: dict = None, job_id: str = "unknown_job"):
        self.job_id = job_id
        self.config = config or {}
        self.directory = self.config.get("directory", f"./exports/{self.job_id}")
        os.makedirs(self.directory, exist_ok=True)

    def export(self, output_data: dict, config: dict) -> None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"summary_{timestamp}.json"
        filepath = os.path.join(self.directory, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(output_data, f, indent=2, default=pydantic_encoder)

        print(f"[FileExporter] ✅ Exported results to {filepath}")

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
                task_desc = result.get("task", "Unknown Task")
                f.write(f"- {task_desc}: {status}\n")

        print(f"[FileExporter] 📄 Full export saved to {filepath}")

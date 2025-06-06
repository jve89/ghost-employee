from app.core.models import Task, JobConfig
from infrastructure.retry.retry_queue_store import retry_queue_store
from infrastructure.exporters.log_exporter import LogExporter
from infrastructure.exporters.file_exporter import FileExporter
from datetime import datetime
from typing import Type

EXPORTER_MAP: dict[str, Type] = {
    "logs": LogExporter,
    "file": FileExporter,
    # Add more exporters here (e.g. email, notion, airtable, etc.)
}


class SimpleExecutor:
    def execute(self, task: Task, config: JobConfig) -> bool:
        print(f"[SimpleExecutor] Executing task: {task.description}")

        # Simulate success/failure condition
        success = "fail" not in task.description.lower()

        if not success:
            print("[SimpleExecutor] ❌ Task failed and will be queued for retry.")
            retry_queue_store.add(task, datetime.utcnow().isoformat())
            return False

        print("[SimpleExecutor] ✅ Task succeeded. Exporting...")
        self._export(task, config)

        return True

    def _export(self, task: Task, config: JobConfig) -> None:
        for destination in config.export_destinations:
            try:
                export_type = destination.type
                export_conf = destination.config or {}

                exporter_class = EXPORTER_MAP.get(export_type)
                if not exporter_class:
                    print(f"[Exporter] ⚠️ Unknown export type: {export_type}")
                    continue

                exporter = exporter_class(**export_conf)
                exporter.export(task)
                print(f"[Exporter] ✅ Successfully exported via {export_type}")

            except Exception as e:
                print(f"[Exporter] ❌ Failed to export via {destination}: {e}")

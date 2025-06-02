from datetime import datetime
from app.core.models import Task, ExportResult
from app.core.interfaces import Exporter
from infrastructure.logger.memory_logger import logger
from infrastructure.logger.export_log import export_log

class LogExporter:
    def export(self, task: Task) -> None:
        try:
            export_result = ExportResult(
                task_description=task.description,
                status="success",
                destination="logs",
                timestamp=task.timestamp or datetime.utcnow(),
                assignee=task.assignee
            )
        except Exception as e:
            print(f"[LogExporter] Failed to create ExportResult: {e}")
            export_result = ExportResult(
                task_description="Export failed – invalid task structure.",
                destination="logs",
                status="error",
                timestamp=datetime.utcnow(),
                assignee=None
            )
        export_log.add(export_result)

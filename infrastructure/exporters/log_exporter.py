from datetime import datetime
from app.core.models import Task, ExportResult
from app.core.interfaces import Exporter

class LogExporter(Exporter):
    def export(self, task: Task) -> ExportResult:
        print(f"[LogExporter] Exporting task to log: {task.description}")
        return ExportResult(
            task_description=task.description,
            destination="log",
            status="success",
            timestamp=datetime.utcnow()
        )

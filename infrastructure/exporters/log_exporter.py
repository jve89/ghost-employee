from datetime import datetime
from app.core.models import Task, ExportResult
from app.core.interfaces import Exporter
from infrastructure.logger.export_log import export_log

class LogExporter(Exporter):
    def export(self, task: Task) -> ExportResult:
        print(f"[LogExporter] Exporting task to log: {task.description}")
        result = ExportResult(
            task_description=task.description,
            destination="log",
            status="success",
            timestamp=datetime.utcnow()
        )
        export_log.add(result)
        return result

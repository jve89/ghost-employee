from datetime import datetime
from app.core.models import Task, ExportResult
from app.core.interfaces import Exporter
from infrastructure.logger.memory_logger import logger
from infrastructure.logger.export_log import export_log

class LogExporter:
    def __init__(self, job_id: str):
        self.job_id = job_id

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

    def export_all(self, summary: str, tasks: list[Task], execution_results: list[dict]) -> None:
        logger.info(f"[LogExporter] 📝 Summary: {summary}")
        for task in tasks:
            logger.info(f"[LogExporter] Task: {task.description} → {task.assignee or 'Unassigned'}")
        for result in execution_results:
            logger.info(f"[LogExporter] ✅ {result['task']}: {result.get('status', 'unknown')}")

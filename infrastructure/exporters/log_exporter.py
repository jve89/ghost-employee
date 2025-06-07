from datetime import datetime
from app.core.models import Task, ExportResult
from app.core.interfaces import Exporter
from infrastructure.logger.memory_logger import logger
from infrastructure.logger.export_log import export_log

class LogExporter(Exporter):
    def __init__(self, config: dict):
        self.job_id = config.get("job_id", "unknown_job")

    def export(self, output_data: dict, config: dict) -> None:
        try:
            summary = output_data.get("summary", "No summary provided.")
            tasks = output_data.get("tasks", [])

            logger.info(f"[LogExporter] 📝 Summary:\n{summary}")
            for task in tasks:
                logger.info(f"[LogExporter] Task: {task['description']} → {task.get('assignee', 'Unassigned')}")
        except Exception as e:
            print(f"[LogExporter] ❌ Failed to log export: {e}")

    def export_all(self, summary: str, tasks: list[Task], execution_results: list[dict]) -> None:
        logger.info(f"[LogExporter] 📝 Summary: {summary}")
        for task in tasks:
            logger.info(f"[LogExporter] Task: {task.description} → {task.assignee or 'Unassigned'}")
        for result in execution_results:
            logger.info(f"[LogExporter] ✅ {result['task']}: {result.get('status', 'unknown')}")

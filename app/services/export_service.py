from app.core.models import Task, ExportResult, JobConfig
from app.core.registry import get_exporters
from infrastructure.exporters.log_exporter import LogExporter
from infrastructure.logger.export_log import export_log

class ExportService:
    def __init__(self, config: JobConfig):
        self.config = config
        self.destinations = config.export_destinations or []

    def export_all(self, tasks: list[Task]) -> None:
        for task in tasks:
            self.export(task)

    def export(self, task: Task) -> None:
        if "logs" in self.destinations:
            exporter = LogExporter()
            exporter.export(task)

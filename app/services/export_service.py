from app.core.models import Task, JobConfig
from app.core.registry import get_exporters

class ExportService:
    def __init__(self, config: JobConfig):
        self.config = config
        self.destinations = config.export_destinations or []

    def export_all(self, tasks: list[Task]) -> None:
        for task in tasks:
            self.export(task)

    def export(self, task: Task) -> None:
        """Export a single task to all configured destinations."""
        for destination in self.destinations:
            try:
                exporters = get_exporters(destination.type)
                for exporter in exporters:
                    # Check if export() requires config (MailgunExporter-style)
                   if destination.type == "email":
                        exporter.export(task.model_dump(), destination.config)
                   else:
                        exporter.export(task)  # Send raw Task object to file, logs, etc.
            except Exception as e:
                print(f"[ExportService] Failed exporting to {destination.type}: {e}")

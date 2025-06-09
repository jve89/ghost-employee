from typing import List, Dict, Any
from app.core.models import ExportDestination, Task
from app.core.registry import get_exporters
from infrastructure.logger.export_status_log import log_export_status
from infrastructure.exporters.file_exporter import FileExporter
from infrastructure.exporters.log_exporter import LogExporter

def dispatch_exports(output_data: Dict[str, Any], destination_configs: List[ExportDestination], job_name: str = "unknown_job") -> None:
    for destination in destination_configs:
        dest_type = destination.type
        config = destination.config

        try:
            exporters = get_exporters(dest_type)
            for exporter_factory in exporters:
                exporter = exporter_factory(config, job_name)

                # 💡 Handle templating (only modifies config["message"])
                if dest_type == "email" and "summary" in output_data and "tasks" in output_data:
                    message_template = config.get("message", "Summary:\n{{summary}}\n\nTasks:\n{{tasks}}")
                    tasks_text = "\n".join(
                        f"- {t['description']} (Due: {t.get('due_date', 'N/A')}, Assigned: {t.get('assignee', 'Unassigned')})"
                        for t in output_data["tasks"]
                    )
                    config = config.copy()
                    config["message"] = message_template.replace("{{summary}}", output_data["summary"]).replace("{{tasks}}", tasks_text)

                exporter.export(output_data, config)
                log_export_status(job_name, dest_type, True, {"details": config})

        except Exception as e:
            print(f"[ERROR] Export to {dest_type} failed: {e}")
            log_export_status(job_name, dest_type, False, {"error": str(e)})

def export_results(job_id: str, summary: str, tasks: list[Task], execution_results: list[dict], job_config: dict):
    print("[ExportDispatcher] 📤 Exporting results (email pipeline)...")

    exporters = [
        FileExporter(config={}, job_id=job_id),
        LogExporter(job_id=job_id),
    ]

    for exporter in exporters:
        try:
            exporter.export_all(summary, tasks, execution_results)
        except Exception as e:
            print(f"[ExportDispatcher] ❌ Export via {exporter.__class__.__name__} failed: {e}")
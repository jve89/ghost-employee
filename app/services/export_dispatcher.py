from typing import List, Dict, Any
from app.core.models import ExportDestination
from app.core.registry import get_exporters
from infrastructure.logger.export_status_log import log_export_status

def dispatch_exports(output_data: Dict[str, Any], destination_configs: List[ExportDestination], job_name: str = "unknown_job") -> None:
    for destination in destination_configs:
        dest_type = destination.type
        config = destination.config

        try:
            exporters = get_exporters(dest_type)
            for exporter in exporters:
                # 💡 Handle dynamic templating for emails
                if dest_type == "email" and "summary" in output_data and "tasks" in output_data:
                    message_template = config.get("message", "Summary:\n{{summary}}\n\nTasks:\n{{tasks}}")
                    tasks_text = "\n".join(
                        f"- {t['description']} (Due: {t.get('due_date', 'N/A')}, Assigned: {t.get('assigned_to', 'Unassigned')})"
                        for t in output_data["tasks"]
                    )

                    formatted_message = message_template.replace("{{summary}}", output_data["summary"]).replace("{{tasks}}", tasks_text)
                    config = config.copy()  # Avoid mutating the original
                    config["message"] = formatted_message

                exporter.export(output_data, config)
                log_export_status(job_name, dest_type, True, {"details": config})

        except Exception as e:
            print(f"[ERROR] Export to {dest_type} failed: {e}")
            log_export_status(job_name, dest_type, False, {"error": str(e)})

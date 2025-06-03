from typing import List, Dict, Any
from app.core.export_destinations import ExportDestinationType
from infrastructure.exporters.file_exporter import export_to_file
from infrastructure.exporters.mailgun_exporter import export_to_email
from infrastructure.logger.export_status_log import log_export_status
from app.core.models import ExportDestination

def dispatch_exports(output_data: Dict[str, Any], destination_configs: List[ExportDestination], job_name: str = "unknown_job"):
    for destination in destination_configs:
        dest_type = destination.type
        config = destination.config

        try:
            if dest_type == ExportDestinationType.FILE:
                export_to_file(output_data, config)
                log_export_status(job_name, dest_type, True, {"path": config.get("directory")})

            elif dest_type == ExportDestinationType.EMAIL:
                # 🧠 Customise message with summary and tasks
                if "summary" in output_data and "tasks" in output_data:
                    message_template = config.get("message", "Summary:\n{{summary}}\n\nTasks:\n{{tasks}}")
                    tasks_text = "\n".join(
                        f"- {t.get('description')} (Due: {t.get('due_date')}, Assigned: {t.get('assigned_to')})"
                        for t in output_data["tasks"]
                    )
                    formatted_message = message_template.replace("{{summary}}", output_data["summary"]).replace("{{tasks}}", tasks_text)
                    config = config.copy()  # avoid mutating original
                    config["message"] = formatted_message

                export_to_email(output_data, config)
                log_export_status(job_name, dest_type, True, {"recipients": config.get("recipients")})

            else:
                print(f"[WARN] Unsupported export destination: {dest_type}")
                log_export_status(job_name, dest_type, False, {"error": "Unsupported export type"})

        except Exception as e:
            print(f"[ERROR] Export to {dest_type} failed: {e}")
            log_export_status(job_name, dest_type, False, {"error": str(e)})

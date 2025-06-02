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
                export_to_email(output_data, config)
                log_export_status(job_name, dest_type, True, {"recipients": config.get("recipients")})

            else:
                print(f"[WARN] Unsupported export destination: {dest_type}")
                log_export_status(job_name, dest_type, False, {"error": "Unsupported export type"})

        except Exception as e:
            print(f"[ERROR] Export to {dest_type} failed: {e}")
            log_export_status(job_name, dest_type, False, {"error": str(e)})

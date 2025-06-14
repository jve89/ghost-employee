from typing import List, Dict, Any
from pydantic import BaseModel
from app.core.models import ExportDestination, Task
from app.core.registry import get_exporters
from infrastructure.logger.export_status_log import log_export_status
from infrastructure.exporters.file_exporter import FileExporter
from infrastructure.exporters.log_exporter import LogExporter
from infrastructure.logger.export_log import log_export

def dispatch_exports(output_data: Dict[str, Any], destination_configs: List[ExportDestination], job_name: str = "unknown_job", metadata: dict = None) -> None:
    from pydantic import BaseModel

    # 🧠 Ensure summary is a string for safe logging and templating
    summary = output_data.get("summary")
    if isinstance(summary, BaseModel):
        summary = summary.model_dump()
    if isinstance(summary, dict):
        summary = summary.get("text", str(summary))  # Safe fallback
    elif not isinstance(summary, str):
        summary = str(summary)
    output_data["summary"] = summary

    # 🧠 Flatten Pydantic tasks
    if "tasks" in output_data:
        output_data["tasks"] = [
            t.model_dump() if isinstance(t, BaseModel) else t for t in output_data["tasks"]
        ]

    for dest in destination_configs:
        if isinstance(dest, tuple):
            dest_type, config = dest
        else:
            dest_type = dest.type
            config = dest.config

        try:
            exporters = get_exporters(dest_type)
            for exporter_factory in exporters:
                exporter = exporter_factory(config, job_name)

                # 💬 Inject summary/tasks into email message if needed
                if dest_type == "email" and summary and output_data.get("tasks"):
                    message_template = config.get("message", "Summary:\n{{summary}}\n\nTasks:\n{{tasks}}")
                    tasks_text = "\n".join(
                        f"- {t['description']} (Due: {t.get('due_date', 'N/A')}, Assigned: {t.get('assignee', 'Unassigned')})"
                        for t in output_data["tasks"]
                    )
                    config = config.copy()
                    config["message"] = message_template.replace("{{summary}}", summary).replace("{{tasks}}", tasks_text)

                exporter.export(output_data, config)

                # ✅ Log to status log
                log_export_status(job_name, dest_type, True, {"summary": summary, "details": config})

                # ✅ Log to in-memory export log (for dashboard)
                log_export(
                    job_name=job_name,
                    destination=dest_type,
                    success=True,
                    details=output_data,
                    sender=metadata.get("sender") if metadata else None,
                    subject=metadata.get("subject") if metadata else None
                )

        except Exception as e:
            print(f"[ERROR] Export to {dest_type} failed: {e}")

            log_export_status(job_name, dest_type, False, {"error": repr(e)})

            log_export(
                job_name=job_name,
                destination=dest_type,
                success=False,
                details={"error": str(e)},
                sender=metadata.get("sender") if metadata else None,
                subject=metadata.get("subject") if metadata else None
            )

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

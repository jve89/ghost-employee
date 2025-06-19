# app/core/registry.py
import json
from pathlib import Path
from app.core.models import JobConfig
from infrastructure.exporters.log_exporter import LogExporter
from infrastructure.exporters.file_exporter import FileExporter
from infrastructure.exporters.mailgun_exporter import MailgunExporter
from infrastructure.exporters.notion_exporter import NotionExporter
from app.plugins.sheets_plugin import SheetsPlugin  # ✅ NEW

# ✅ Centralised registry for all exporters
EXPORTER_REGISTRY = {
    "log": LogExporter,
    "file": FileExporter,
    "email": MailgunExporter,
    "notion": NotionExporter,
    "sheets": SheetsPlugin,  # ✅ New export destination
}

def get_exporters(destination_type: str) -> list:
    """
    Return a list of exporter factories (functions that accept config and job_id).
    """
    if destination_type not in EXPORTER_REGISTRY:
        raise ValueError(f"Unknown export destination: {destination_type}")

    cls = EXPORTER_REGISTRY[destination_type]
    return [lambda config, job_id: cls(config=config, job_id=job_id)]

def get_job_config(job_id: str) -> JobConfig:
    """
    Load a job config JSON and return a validated JobConfig object.
    """
    config_path = Path(f"config/job_schemas/{job_id}.json")
    if not config_path.exists():
        raise FileNotFoundError(f"❌ Job config not found for ID: {job_id}")

    with config_path.open("r", encoding="utf-8") as f:
        raw = json.load(f)

    return JobConfig(**raw)
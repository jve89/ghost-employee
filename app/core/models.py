from pydantic import BaseModel, validator
from typing import Optional, List, Dict, Any
from datetime import datetime

# ✅ Valid export destinations — centralised and enforced
VALID_DESTINATIONS = ["logs", "notion", "google_sheets", "email"]

class Summary(BaseModel):
    source_file: str
    content: str
    generated_at: datetime

class Task(BaseModel):
    description: str
    assignee: Optional[str] = None
    timestamp: datetime = datetime.utcnow()

class ExportResult(BaseModel):
    task_description: str
    destination: str
    status: str
    timestamp: datetime
    assignee: Optional[str] = None

class ExportDestination(BaseModel):
    type: str
    config: Dict[str, Any]

class JobConfig(BaseModel):
    job_name: str
    watch_dir: str
    gpt_model: str
    retry_limit: int
    run_interval_seconds: int
    export_destinations: Optional[List[ExportDestination]] = []

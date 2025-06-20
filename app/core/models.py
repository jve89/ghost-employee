from pydantic import BaseModel, validator
from typing import Optional, List, Dict, Any
from datetime import datetime

# ✅ Valid export destinations — centralised and enforced
VALID_DESTINATIONS = ["logs", "notion", "google_sheets", "email", "file"]

class Summary(BaseModel):
    source_file: str
    content: str
    generated_at: datetime
    sender: Optional[str] = None         # ✅ New
    subject: Optional[str] = None        # ✅ New

class Task(BaseModel):
    job_id: str
    source: str
    description: str
    summary: str
    created_at: str  # ISO 8601 timestamp
    assignee: Optional[str] = None
    timestamp: datetime = datetime.utcnow()
    status: Optional[str] = "pending"
    executed_at: Optional[datetime] = None
    entity: Optional[str] = None
    action: Optional[str] = None
    payload: Optional[Dict[str, Any]] = None

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
    job_id: str
    watch_dir: str
    gpt_model: str
    retry_limit: int
    run_interval_seconds: int
    file_pattern: Optional[str] = "*"
    active: bool = True
    export_destinations: List[ExportDestination]
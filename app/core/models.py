from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class Summary(BaseModel):
    source_file: str
    content: str
    generated_at: datetime

class Task(BaseModel):
    description: str
    due_date: Optional[datetime] = None
    assigned_to: Optional[str] = None
    source_summary: Optional[str] = None  # Optional: link back to summary ID or file

class ExportResult(BaseModel):
    task_description: str
    destination: str
    status: str
    timestamp: datetime

class JobConfig(BaseModel):
    job_name: str
    watch_dir: str
    export_destinations: List[str]
    gpt_model: Optional[str] = "gpt-4"
    retry_limit: int = 3

import sys
import os
sys.path.insert(0, os.path.abspath("."))  # Make sure project root is in path

from infrastructure.executor.task_executor import PluginExecutor
from app.core.models import Task

executor = PluginExecutor()

task = Task(
    description = "Rename watched/performance_notes.txt to watched/notes_old.txt",
    assignee="automation",
    job_id="compliance_analyst",
    source="test_email",
    summary="Test summary",
    created_at="2025-06-06T00:00:00Z"
)

success = executor.execute(task)
print("✅ Success:", success)
print("📝 Status:", task.status)

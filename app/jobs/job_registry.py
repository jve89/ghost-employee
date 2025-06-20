from app.jobs.base_demo_job import BaseDemoJob
from app.jobs.hr_assistant import HRAssistantJob

# ✅ Use a dictionary for fast lookup by job_id
JOB_REGISTRY = {
    "base_demo_job": BaseDemoJob,
    "hr_assistant": HRAssistantJob,
}

def get_job_class(job_id: str):
    if job_id in JOB_REGISTRY:
        return JOB_REGISTRY[job_id]
    raise ValueError(f"Unknown job_id: {job_id}")

# ✅ Optional: Export lowercase alias for compatibility
job_registry = JOB_REGISTRY

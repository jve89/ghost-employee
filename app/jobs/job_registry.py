# app/jobs/job_registry.py

from app.jobs.compliance_assistant import ComplianceAssistantJob

# Register jobs (classes)
JOB_REGISTRY = {
    "compliance_assistant": ComplianceAssistantJob,
}

# TEMP hardcoded email routing (expandable later)
EMAIL_TO_JOB_ID = {
    "compliance@ghost.system": "compliance_assistant"
}

def get_job_class(job_id: str):
    if job_id in JOB_REGISTRY:
        return JOB_REGISTRY[job_id]
    raise ValueError(f"Unknown job_id: {job_id}")

def list_registered_jobs():
    return [
        {"job_id": job_id, "job_name": cls.job_name}
        for job_id, cls in JOB_REGISTRY.items()
    ]

def get_job_by_email(email: str):
    """
    Maps incoming email to job instance.
    """
    job_id = EMAIL_TO_JOB_ID.get(email.lower())
    if job_id:
        job_class = get_job_class(job_id)
        return job_class()  # instantiate for method calls
    return None

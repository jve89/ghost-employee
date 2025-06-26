from app.jobs.compliance_assistant import ComplianceAssistantJob

JOB_REGISTRY = {
    "compliance_assistant": ComplianceAssistantJob,
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

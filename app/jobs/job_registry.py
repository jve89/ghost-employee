from app.jobs.demo_job import DemoJob
from app.jobs.sample_job import SampleJob
from app.jobs.data_entry_specialist import DataEntrySpecialistJob
from app.jobs.crm_ops_job import CRMOperationsJob
from app.jobs.compliance_assistant import ComplianceAssistantJob

# ✅ Use class references (not instances)
JOB_REGISTRY = {
    "sample_job": SampleJob,
    "demo_job": DemoJob,
    "data_entry_specialist": DataEntrySpecialistJob,
    "crm_ops_job": CRMOperationsJob,
    "compliance_assistant": ComplianceAssistantJob,
}

def get_job_class(job_id: str):
    if job_id in JOB_REGISTRY:
        return JOB_REGISTRY[job_id]
    raise ValueError(f"Unknown job_id: {job_id}")

from app.jobs.demo_job import DemoJob
from app.jobs.data_entry_specialist import DataEntrySpecialistJob
from app.jobs.crm_ops_job import CRMOperationsJob
from app.jobs.compliance_assistant import ComplianceAssistantJob
from app.jobs.hr_onboarding_assistant import HROnboardingAssistantJob

# ✅ Use class references (not instances)
JOB_REGISTRY = {
    "demo_job": DemoJob,
    "data_entry_specialist": DataEntrySpecialistJob,
    "crm_ops_job": CRMOperationsJob,
    "compliance_assistant": ComplianceAssistantJob,
    "hr_onboarding_assistant": HROnboardingAssistantJob,
}

def get_job_class(job_id: str):
    if job_id in JOB_REGISTRY:
        return JOB_REGISTRY[job_id]
    raise ValueError(f"Unknown job_id: {job_id}")

# ✅ Export lowercase alias for compatibility
job_registry = JOB_REGISTRY

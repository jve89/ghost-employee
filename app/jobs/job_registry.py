from app.jobs.demo_job import DemoJob
from app.jobs.sample_job import SampleJob
from app.jobs.compliance_analyst import ComplianceAnalystJob
from app.jobs.data_entry_specialist import DataEntrySpecialistJob

job_registry = {
    "sample_job": SampleJob(),
    "demo_job": DemoJob(),
    "compliance_analyst": ComplianceAnalystJob(),
    "data_entry_specialist": DataEntrySpecialistJob,  
}

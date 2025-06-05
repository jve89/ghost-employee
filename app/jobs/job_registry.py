from app.jobs.demo_job import DemoJob
from app.jobs.sample_job import SampleJob
from app.jobs.compliance_analyst import ComplianceAnalystJob

job_registry = {
    "sample_job": SampleJob(),
    "demo_job": DemoJob(),
    "compliance_analyst": ComplianceAnalystJob(),  
}

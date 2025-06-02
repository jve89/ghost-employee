from app.jobs.sample_job import SampleJob
from app.jobs.prepare_interns import PrepareInternsJob

job_registry = {
    "sample_job": SampleJob(),
    "prepare_interns": PrepareInternsJob(),
}

from config.config_loader import load_job_config
from app.jobs.sample_job import SampleJob

if __name__ == "__main__":
    config = load_job_config("sample_job")
    SampleJob().run(config)

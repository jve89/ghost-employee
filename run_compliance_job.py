from config.config_loader import load_job_config
from app.jobs.compliance_analyst import ComplianceAnalystJob

if __name__ == "__main__":
    config = load_job_config("compliance_analyst")
    ComplianceAnalystJob().run(config)

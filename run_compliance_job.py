from config.config_loader import load_job_config
from app.jobs.compliance_assistant import ComplianceAssistantJob

if __name__ == "__main__":
    config = load_job_config("compliance_analyst")
    ComplianceAssistantJob().run(config)

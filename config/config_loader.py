import os
import json
from app.core.models import JobConfig

def load_job_configs() -> list[JobConfig]:
    config_dir = "config/job_schemas"
    configs = []
    for file in os.listdir(config_dir):
        if file.endswith(".json"):
            with open(os.path.join(config_dir, file)) as f:
                data = json.load(f)
                configs.append(JobConfig(**data))
    return configs

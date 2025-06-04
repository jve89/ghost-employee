import os
import json
from app.core.models import JobConfig

def load_job_configs() -> list[JobConfig]:
    config_dir = "config/job_schemas"
    configs = []
    for file in os.listdir(config_dir):
        if file.endswith(".json"):
            path = os.path.join(config_dir, file)
            print(f"🔍 Loading: {path}")
            with open(path) as f:
                data = json.load(f)
                print(f"📄 JSON Content: {data}")
                configs.append(JobConfig(**data))
    return configs

def load_job_config(job_name: str) -> JobConfig:
    path = f"config/job_schemas/{job_name}.json"
    print(f"🔍 Loading single job config: {path}")
    with open(path) as f:
        data = json.load(f)
        return JobConfig(**data)

def load_all_job_configs(config_dir: str = "config/job_schemas") -> list[JobConfig]:
    job_configs = []

    for filename in os.listdir(config_dir):
        if filename.endswith(".json"):
            path = os.path.join(config_dir, filename)
            with open(path, "r") as f:
                data = json.load(f)
                job_config = JobConfig(**data)
                job_configs.append(job_config)

    return job_configs

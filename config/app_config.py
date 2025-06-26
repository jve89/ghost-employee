import json
import os

def load_job_config(job_id: str) -> dict:
    config_path = f"config/job_schemas/{job_id}.json"
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config not found: {config_path}")
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)

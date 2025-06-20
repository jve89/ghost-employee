import os
import json
from pathlib import Path
from pydantic import TypeAdapter
from app.core.models import JobConfig

adapter = TypeAdapter(JobConfig)

def load_all_job_configs(base_dir: str = "clients") -> list[JobConfig]:
    job_configs = []
    seen_ids = set()

    client_id = os.getenv("CLIENT_ID", "default")
    client_path = os.path.join(base_dir, client_id, "jobs")
    if not os.path.isdir(client_path):
        return []

    for filename in os.listdir(client_path):
        if filename.endswith(".json"):
            path = os.path.join(client_path, filename)
            with open(path, "r") as f:
                data = json.load(f)
                job_config = adapter.validate_python(data)

                if job_config.job_id in seen_ids:
                    print(f"⚠️ Duplicate job_id '{job_config.job_id}' found in {path}. Skipping.")
                    continue

                seen_ids.add(job_config.job_id)
                job_configs.append(job_config)

    return job_configs

def save_job_config(job_config: JobConfig, client_id: str):
    # Optional future-proofing for saving per-client
    path = f"clients/{client_id}/jobs/{job_config.job_id}.json"
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(job_config.model_dump(), f, indent=2)

def load_job_config(job_id: str, base_dir: str = "clients") -> JobConfig:
    for client_folder in os.listdir(base_dir):
        config_path = os.path.join(base_dir, client_folder, "jobs", f"{job_id}.json")
        if os.path.exists(config_path):
            with open(config_path, "r") as f:
                data = json.load(f)
                return adapter.validate_python(data)

    raise FileNotFoundError(f"❌ Job config not found for ID: {job_id}")

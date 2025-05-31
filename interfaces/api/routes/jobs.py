from fastapi import APIRouter
from fastapi import HTTPException
from app.jobs.job_registry import job_registry
from app.services.job_manager import JobManager
from config.config_loader import load_job_configs
from app.core.models import JobConfig
from infrastructure.logger.memory_logger import logger

router = APIRouter()

@router.get("/", response_model=list[JobConfig])
def list_jobs():
    return load_job_configs()

@router.post("/run/{job_name}")
def run_job(job_name: str):
    config_list = load_job_configs()
    config = next((c for c in config_list if c.job_name == job_name), None)

    if not config:
        raise HTTPException(status_code=404, detail="Job config not found")

    job = job_registry.get(job_name)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    job.run(config)
    return {"status": "started", "job": job_name}

@router.get("/logs")
def get_logs():
    return {"logs": logger.get_logs()}
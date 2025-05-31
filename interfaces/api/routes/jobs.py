from fastapi import APIRouter
from config.config_loader import load_job_configs
from app.core.models import JobConfig

router = APIRouter()

@router.get("/", response_model=list[JobConfig])
def list_jobs():
    return load_job_configs()

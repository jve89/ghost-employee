from fastapi import APIRouter
from fastapi.responses import RedirectResponse
from fastapi import HTTPException
from app.jobs.job_registry import job_registry
from app.services.job_manager import JobManager
from config.config_loader import load_job_configs
from app.core.models import JobConfig
from infrastructure.logger.memory_logger import logger
from infrastructure.logger.job_status import job_status
from infrastructure.logger.export_log import export_log
from infrastructure.logger.retry_queue import retry_queue
from infrastructure.retry import retry_queue_store

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

@router.get("/status")
def job_statuses():
    return job_status.get_all()

@router.get("/exports")
def get_export_logs():
    return [r.model_dump() for r in export_log.get_logs()]

@router.get("/retries")
def get_retries():
    return retry_queue.all()

@router.post("/retries/{retry_id}")
def retry_task(retry_id: str):
    entry = next((e for e in retry_queue_store.queue if e.get("id") == retry_id), None)

    if not entry:
        raise HTTPException(status_code=404, detail="Retry task not found")

    task = Task(**entry["task"])
    success = SimpleExecutor().execute(task)

    if success:
        retry_queue_store.queue.remove(entry)

    return {"status": "retried", "success": success}

@router.get("/retry-queue")
def retry_queue():
    return {"retry_queue": retry_queue_store.get_all()}

@router.post("/retry-failed")
def retry_failed_tasks():
    retry_queue_store.retry_all()
    return RedirectResponse(url="/dashboard", status_code=303)

@router.get("/jobs/retry-queue")
def get_retry_queue():
    return {"retry_queue": retry_queue_store.queue}

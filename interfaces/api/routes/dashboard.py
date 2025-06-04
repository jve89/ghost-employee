import os
import json
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from infrastructure.logger.memory_logger import logger
from infrastructure.retry.retry_queue_store import retry_queue_store
from infrastructure.logger.job_status import job_status
from config.config_loader import load_job_configs
from infrastructure.logger.export_log import export_log
from infrastructure.logger.job_status import get_recent_activity

router = APIRouter()
templates = Jinja2Templates(directory="interfaces/api/templates")

@router.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

@router.get("/jobs/logs")
async def get_logs():
    return JSONResponse(content={"logs": logger.get_logs()})

@router.get("/jobs/status")
async def get_status():
    return JSONResponse(content=job_status.get_all())

@router.get("/jobs/retry-queue")
async def get_retry_queue_api():
    return {"retry_queue": retry_queue_store.get_all()}

@router.get("/jobs")
async def get_jobs():
    jobs = load_job_configs()
    return JSONResponse(content=jobs)

@router.get("/jobs/exports")
def get_exports():
    return [r.dict() for r in export_log.get_logs()]

@router.get("/dashboard/activity")
def get_dashboard_activity():
    return get_recent_activity()

@router.get("/dashboard/exports")
def get_recent_exports():
    log_path = "./logs/export_status.json"

    if not os.path.exists(log_path):
        return JSONResponse(content={"exports": []})

    try:
        with open(log_path, "r") as f:
            data = json.load(f)
        # Return last 10 in reverse (newest first)
        recent = sorted(data, key=lambda x: x["timestamp"], reverse=True)[:10]
        return {"exports": recent}
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to read export log: {str(e)}"}
        )

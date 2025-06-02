from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from infrastructure.logger.memory_logger import logger
from infrastructure.retry.retry_queue_store import get_retry_queue
from infrastructure.logger.job_status import job_status
from config.config_loader import load_job_configs
from infrastructure.logger.export_log import export_log


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
    return JSONResponse(content={"retry_queue": get_retry_queue()})

@router.get("/jobs")
async def get_jobs():
    jobs = load_job_configs()
    return JSONResponse(content=jobs)

@router.get("/jobs/exports")
def get_exports():
    from infrastructure.logger.export_log import get_export_log
    return get_export_log()

@router.get("/jobs/exports")
def get_exports():
    return [r.dict() for r in export_log.get_logs()]

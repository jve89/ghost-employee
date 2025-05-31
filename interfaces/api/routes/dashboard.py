from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from infrastructure.logger.job_status import job_status
from infrastructure.logger.export_log import export_log
from infrastructure.retry.retry_queue_store import retry_queue_store

import os

router = APIRouter()
templates = Jinja2Templates(directory=os.path.join("interfaces", "api", "templates"))

@router.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):
    statuses = job_status.get_all()
    exports = export_log.get_logs()
    retries = retry_queue_store.get_all()
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "statuses": statuses,
        "exports": [r.model_dump() for r in exports],
        "retry_queue": retries,
    })

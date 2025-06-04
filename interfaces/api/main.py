# interfaces/api/main.py

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from interfaces.api.routes.jobs import router as jobs_router
from interfaces.api.routes.dashboard import router as dashboard_router
from config.config_loader import load_all_job_configs
from app.jobs.sample_job import SampleJob
from infrastructure.logger.memory_logger import logger
import threading
import time

app = FastAPI()
app.include_router(jobs_router, prefix="/jobs")
app.include_router(dashboard_router)

templates = Jinja2Templates(directory="interfaces/api/templates")

@app.get("/")
def root():
    return RedirectResponse(url="/dashboard")

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):
    job_configs = load_all_job_configs()
    return templates.TemplateResponse("dashboard.html", {"request": request, "jobs": job_configs})

@app.on_event("startup")
def start_background_jobs():
    job_configs = load_all_job_configs()
    for config in job_configs:
        thread = threading.Thread(target=job_loop, args=(config,), daemon=True)
        thread.start()
    logger.log(f"✅ Started {len(job_configs)} background job threads.")

def job_loop(config):
    job = SampleJob()
    interval = config.run_interval_seconds or 60
    while True:
        try:
            logger.log(f"🔄 Auto-running job: {config.job_name}")
            job.run(config)
        except Exception as e:
            logger.log(f"[ERROR] Job '{config.job_name}' failed: {e}")
        time.sleep(interval)

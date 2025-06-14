# interfaces/api/main.py

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

from interfaces.api.routes.auth import router as auth_router
from interfaces.api.routes.mailgun_webhook import router as mailgun_router
from interfaces.api.routes.jobs import router as jobs_router
from interfaces.api.routes.dashboard import router as dashboard_router

from config.config_loader import load_all_job_configs
from app.jobs.sample_job import SampleJob
from infrastructure.logger.memory_logger import logger
from infrastructure.logger.activity_log import activity_log

import threading
import time

# --- Init FastAPI app ---
app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="supersecretkey123")

# --- Register routers ---
app.include_router(auth_router)
app.include_router(jobs_router, prefix="/jobs")
app.include_router(dashboard_router)
app.include_router(mailgun_router)

templates = Jinja2Templates(directory="interfaces/api/templates")

# --- Root Redirect ---
@app.get("/")
def root():
    return RedirectResponse(url="/dashboard")

# --- Activity log endpoint ---
@app.get("/logs/activity")
def get_activity_log():
    return activity_log.get_recent(50)

# --- (Unused) Dashboard fallback (can be deleted later) ---
@app.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):
    session = request.session
    if not session.get("logged_in"):
        return RedirectResponse("/login", status_code=303)

    job_configs = load_all_job_configs()
    return templates.TemplateResponse("dashboard.html", {"request": request, "jobs": job_configs})

# --- Background job threads ---
@app.on_event("startup")
def start_background_jobs():
    job_configs = load_all_job_configs()
    for config in job_configs:
        thread = threading.Thread(target=job_loop, args=(config,), daemon=True)
        thread.start()
    logger.info(f"✅ Started {len(job_configs)} background job threads.")

def job_loop(config):
    job = SampleJob()
    interval = config.run_interval_seconds or 60
    while True:
        try:
            logger.info(f"🔄 Auto-running job: {config.job_name}")
            job.run(config)
        except Exception as e:
            logger.error(f"[ERROR] Job '{config.job_name}' failed: {e}")
        time.sleep(interval)

def email_watcher_loop():
    inbox_path = Path("watched/test_inbox")
    processed_path = Path("watched/processed")
    inbox_path.mkdir(parents=True, exist_ok=True)
    processed_path.mkdir(parents=True, exist_ok=True)

    while True:
        for file in inbox_path.glob("*.txt"):
            try:
                # 📄 Filename format: mailgun_<timestamp>__<job_id>.txt
                parts = file.stem.split("__")
                if len(parts) != 2:
                    logger.warning(f"⚠️ Skipping file with invalid format: {file.name}")
                    continue

                job_id = parts[1]
                if job_id not in job_registry:
                    logger.warning(f"❌ No matching job found for: {job_id}")
                    continue

                with open(file, "r", encoding="utf-8", errors="ignore") as f:
                    text_input = f.read()

                if not text_input.strip():
                    logger.warning(f"⚠️ Empty file skipped: {file.name}")
                    continue

                # ✅ Run the job
                config = load_job_config(job_id)
                job = job_registry[job_id]
                logger.info(f"📥 Email-triggered run for job: {job_id}")
                job.run(config=config, override_text=text_input)

                # Move to processed
                dest = processed_path / file.name
                file.rename(dest)
                logger.info(f"📦 Moved to processed: {file.name}")

            except Exception as e:
                logger.error(f"💥 Error processing email file {file.name}: {e}")

        time.sleep(10)  # Check every 10 seconds

# --- Launch email watcher on startup ---
@app.on_event("startup")
def start_email_watcher():
    thread = threading.Thread(target=email_watcher_loop, daemon=True)
    thread.start()
    logger.info("📨 Email watcher started.")
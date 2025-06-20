import os
import json
import glob
from datetime import datetime
from pydantic import BaseModel
from pathlib import Path
from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from infrastructure.logger.memory_logger import logger
from infrastructure.retry.retry_queue_store import retry_queue_store
from infrastructure.logger.job_status import job_status
from config.config_loader import load_all_job_configs as load_job_configs
from infrastructure.logger.export_log import export_log
from infrastructure.logger.job_status import get_recent_activity
from infrastructure.auth.decorators import require_login_json
from collections import defaultdict
from infrastructure.logger.job_timesheet import get_timesheet_data
from app.services.job_manager import toggle_job_active

router = APIRouter()
templates = Jinja2Templates(directory="interfaces/api/templates")

class JobCreateRequest(BaseModel):
    job_name: str
    watch_dir: str
    run_interval_seconds: int
    gpt_model: str

@router.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    if not request.session.get("logged_in"):
        return RedirectResponse(url="/login", status_code=303)
    return templates.TemplateResponse("dashboard.html", {"request": request})

@router.get("/jobs/logs")
@require_login_json
async def get_logs():
    return JSONResponse(content={"logs": logger.get_logs()})

@router.get("/jobs/status")
@require_login_json
async def get_status():
    return JSONResponse(content=job_status.get_all())

@router.get("/jobs/retry-queue")
@require_login_json
async def get_retry_queue_api():
    return {"retry_queue": retry_queue_store.get_all()}

@router.get("/jobs")
async def get_jobs():
    jobs = load_job_configs()
    return JSONResponse(content=jobs)

@router.get("/jobs/exports")
@require_login_json
async def get_exports(request: Request):
    return [r.dict() for r in export_log.get_logs()]

@router.get("/dashboard/activity")
@require_login_json
async def get_dashboard_activity(request: Request):
    return get_recent_activity()

@router.get("/dashboard/job-stats")
@require_login_json
async def job_stats(request: Request):
    stats = {}

    # 📊 Load task run data from timesheets
    for file in glob.glob("logs/timesheets/*_timesheet.json"):
        job = os.path.basename(file).replace("_timesheet.json", "")
        with open(file) as f:
            entries = json.load(f)
        if entries:
            last_run = entries[-1]["timestamp"]
            count = sum(e["tasks_executed"] for e in entries)
            stats[job] = {
                "last_run": last_run,
                "total_tasks": count,
                "runs": len(entries),
                "export_count": 0,
                "failed_exports": 0
            }

    # 📦 Enrich with export stats
    for entry in export_log.get_logs():
        job = entry["job_name"]
        if job not in stats:
            stats[job] = {
                "last_run": "never",
                "total_tasks": 0,
                "runs": 0,
                "export_count": 0,
                "failed_exports": 0
            }
        stats[job]["export_count"] += 1
        if not entry["success"]:
            stats[job]["failed_exports"] += 1

    return JSONResponse(content=stats)

@router.get("/dashboard/exports")
@require_login_json
async def get_recent_exports(request: Request):
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

@router.get("/dashboard/retry-stats")
#@require_login_json
async def get_retry_stats(request: Request):
    try:
        queue = retry_queue_store.get_all()
        stats_by_job = defaultdict(lambda: {"total_tasks": 0, "last_retry_attempt": None})

        for entry in queue:
            job = entry.get("job_name", "unknown")
            stats_by_job[job]["total_tasks"] += 1

            ts = entry.get("timestamp")
            if ts:
                parsed = datetime.fromisoformat(ts)
                last = stats_by_job[job]["last_retry_attempt"]
                if not last or parsed > last:
                    stats_by_job[job]["last_retry_attempt"] = parsed

        for job, stats in stats_by_job.items():
            if stats["last_retry_attempt"]:
                stats["last_retry_attempt"] = stats["last_retry_attempt"].isoformat()
            else:
                stats["last_retry_attempt"] = "n/a"

        return stats_by_job

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@router.post("/dashboard/retry-export/{entry_id}")
@require_login_json
async def retry_export(request: Request, entry_id: str):
    try:
        from infrastructure.logger.export_log import export_log
        success = export_log.retry(entry_id)
        if success:
            return {"status": "ok", "message": "✅ Export retry queued."}
        else:
            return {"status": "error", "message": "❌ Retry failed or not supported."}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@router.get("/dashboard/latest-demo-export")
@require_login_json
async def get_latest_demo_export(request: Request):
    from pathlib import Path

    EXPORTS_DIR = Path("exports/demo_job")
    folders = sorted(EXPORTS_DIR.glob("*_GhostRun"), reverse=True)
    if not folders:
        return JSONResponse(content={"status": "no exports yet"})

    latest = folders[0]
    metadata_path = latest / "metadata.json"
    if not metadata_path.exists():
        return JSONResponse(content={"status": "no metadata"})

    with open(metadata_path) as f:
        metadata = json.load(f)

    return {
        "folder": latest.name,
        "timestamp": metadata["timestamp"],
        "job_id": metadata["job_id"],
        "task_count": metadata["task_count"],
        "success_count": metadata["success_count"],
        "failure_count": metadata["failure_count"],
        "pdf_download_url": f"/dashboard/download/{latest.name}/summary.pdf"
    }

@router.get("/dashboard/download/{folder}/{filename}")
def download_demo_export_file(folder: str, filename: str):
    from pathlib import Path
    from fastapi.responses import FileResponse

    path = Path("exports/demo_job") / folder / filename
    if not path.exists():
        return JSONResponse(status_code=404, content={"error": "File not found"})
    return FileResponse(path)

@router.post("/dashboard/create-job")
@require_login_json
async def create_job(request: Request, data: JobCreateRequest):
    new_config = {
        "job_id": data.job_name,
        "job_name": data.job_name,
        "watch_dir": data.watch_dir,
        "run_interval_seconds": data.run_interval_seconds,
        "gpt_model": data.gpt_model,
        "retry_limit": 3,
        "export_destinations": [
            {
                "type": "logs",
                "config": {}
            }
        ]
    }

    path = f"config/job_schemas/{data.job_name}.json"
    os.makedirs("config/job_schemas", exist_ok=True)

    with open(path, "w") as f:
        json.dump(new_config, f, indent=2)

    return {"status": "created", "job": data.job_name}

@router.post("/dashboard/retry-failed")
def retry_failed_tasks():
    try:
        from app.services.retry_runner import retry_all_tasks
        retry_all_tasks()
        return RedirectResponse(url="/dashboard", status_code=303)
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@router.get("/dashboard/latest-compliance-export")
@require_login_json
async def latest_compliance_export(request: Request):
    from pathlib import Path
    import json
    from fastapi.responses import JSONResponse

    export_dir = Path("exports/compliance_analyst")
    folders = sorted(export_dir.glob("*_GhostRun"), reverse=True)

    if not folders:
        return JSONResponse({"status": "no_exports"}, status_code=404)

    latest = folders[0]
    metadata_path = latest / "metadata.json"
    export_path = latest / "export.json"

    if not metadata_path.exists() or not export_path.exists():
        return JSONResponse({"status": "incomplete"}, status_code=500)

    try:
        with metadata_path.open() as f:
            metadata = json.load(f)
        with export_path.open() as f:
            export = json.load(f)
    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)}, status_code=500)

    return {
        "job_name": metadata.get("job_id", "compliance_analyst"),
        "timestamp": metadata.get("timestamp", latest.name.replace("_GhostRun", "")),
        "summary": export.get("summary", "-"),
        "tasks": export.get("tasks", [])
    }

@router.get("/dashboard/email-activity")
@require_login_json
async def get_email_activity(request: Request):
    try:
        from infrastructure.logger.activity_log import activity_log
        entries = activity_log.get_recent(count=20)

        # Filter for email-triggered jobs only
        email_entries = [e for e in entries if e.get("trigger") == "email"]
        recent = sorted(email_entries, key=lambda x: x["timestamp"], reverse=True)[:5]

        return {"email_activity": recent}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@router.get("/dashboard/email-jobs")
@require_login_json
async def get_email_triggered_jobs(request: Request):
    memory_path = Path("memory")
    job_files = sorted(memory_path.glob("mailgun_*.json"), reverse=True)

    jobs = []
    for file in job_files:
        try:
            with open(file) as f:
                data = json.load(f)
                jobs.append({
                    "timestamp": data.get("timestamp", "unknown"),
                    "job_type": data.get("job_type", "unknown"),
                    "sender": data.get("sender", "unknown"),
                    "subject": data.get("subject", "unknown"),
                    "status": data.get("status", "unknown")
                })
        except Exception:
            continue
        if len(jobs) == 5:
            break

    return JSONResponse(content=jobs)

@router.post("/dashboard/retry-task/{task_id}")
@require_login_json
async def retry_single_task(request: Request, task_id: str):
    try:
        from app.services.retry_runner import retry_task_by_id
        result = retry_task_by_id(task_id)
        return {"status": "ok", "message": result}
    except Exception as e:
        print(f"Retry failed: {e}")  # 👈 Add console output for debugging
        return JSONResponse(status_code=500, content={"status": "error", "message": "❌ Retry failed."})

@router.get("/dashboard/latest-tasks")
@require_login_json
async def get_latest_tasks(request: Request):
    from infrastructure.logger.job_timesheet import get_recent_tasks
    return get_recent_tasks(limit=20)

@router.get("/dashboard/recent-failures")
@require_login_json
async def get_recent_failures(request: Request):
    try:
        failures = []

        # Load export log failures
        for entry in reversed(export_log.get_logs()):
            if not entry.get("success"):
                failures.append({
                    "type": "Export Failure",
                    "timestamp": entry.get("timestamp", "unknown"),
                    "job": entry.get("job_name", "unknown"),
                    "destination": entry.get("destination", "unknown"),
                    "details": entry.get("details", {}),
                    "retry_count": entry.get("retry_count", 0)
                })
                if len(failures) == 5:
                    break

        return {"failures": failures}

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@router.get("/api/dashboard/job-durations")
async def get_job_durations():
    logs = get_timesheet_data()
    durations_by_job = defaultdict(list)

    for entry in logs:
        job = entry.get("job")
        duration = entry.get("duration")
        if job and isinstance(duration, (int, float)):
            durations_by_job[job].append(duration)

    avg_durations = {
        job: round(sum(times) / len(times), 2)
        for job, times in durations_by_job.items() if times
    }

    return JSONResponse(avg_durations)

@router.post("/jobs/{job_id}/toggle")
@require_login_json
async def toggle_job_state(request: Request, job_id: str):
    try:
        new_state = toggle_job_active(job_id)
        return {"job_id": job_id, "active": new_state}
    except Exception as e:
        print(f"❌ Failed to toggle job {job_id}: {e}")
        raise HTTPException(status_code=500, detail="Toggle failed")


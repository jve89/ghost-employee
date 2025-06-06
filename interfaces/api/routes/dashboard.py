import os
import json
import glob
from pydantic import BaseModel
from fastapi import APIRouter, Request, Form
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

class JobCreateRequest(BaseModel):
    job_name: str
    watch_dir: str
    run_interval_seconds: int
    gpt_model: str

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

@router.get("/dashboard/job-stats")
def job_stats():
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

@router.post("/dashboard/retry-export/{entry_id}")
def retry_export(entry_id: str):
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
def get_latest_demo_export():
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
async def create_job(data: JobCreateRequest):
    new_config = {
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

@router.get("/dashboard/latest-compliance-export")
def latest_compliance_export():
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

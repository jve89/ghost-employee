from fastapi import APIRouter, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from datetime import datetime
import os, shutil

from app.logs.input_log import load_input_log, append_input_log
from infrastructure.logger.export_log import export_log
from infrastructure.retry.retry_queue_store import retry_queue_store
from app.jobs.job_registry import list_registered_jobs

router = APIRouter()
templates = Jinja2Templates(directory="interfaces/api/templates")

# -- 🔐 Serve Dashboard Page --

@router.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})


# -- 📁 Get Ghost Jobs List --

@router.get("/dashboard/jobs")
async def get_jobs():
    jobs = list_registered_jobs()
    return JSONResponse(content={"jobs": jobs})


# -- 📥 Input Log --

@router.get("/dashboard/input-log")
async def get_input_log():
    log = load_input_log()
    return JSONResponse(content={"log": log})


# -- ⬆️ File Upload Endpoint --

@router.post("/dashboard/upload")
async def upload_file(
    job_id: str = Form(...),
    instruction: str = Form(""),
    file: UploadFile = File(...)
):
    try:
        job_folder = f"watched/{job_id}"
        os.makedirs(job_folder, exist_ok=True)

        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        file_path = os.path.join(job_folder, f"{timestamp}_{file.filename}")
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)

        if instruction.strip():
            with open(file_path + ".instruction.txt", "w") as f:
                f.write(instruction.strip())

        append_input_log({
            "source": "manual_upload",
            "job_id": job_id,
            "file": file_path,
            "instruction": instruction,
            "timestamp": datetime.utcnow().isoformat()
        })

        return {"message": "✅ File uploaded successfully"}
    except Exception as e:
        print(f"[Upload Error] ❌ {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})


# -- 🔁 Retry Queue --

@router.get("/dashboard/retry-queue")
async def get_retry_queue():
    queue = retry_queue_store.get_all()
    return JSONResponse(content={"retry_queue": queue})


# -- ⚙️ Latest Tasks --

@router.get("/dashboard/latest-tasks")
async def get_latest_tasks():
    from infrastructure.logger.job_timesheet import get_recent_tasks
    tasks = get_recent_tasks(limit=10)
    return JSONResponse(content={"tasks": tasks})


# -- ⚙️ Active Jobs List --

@router.get("/dashboard/active-jobs")
async def get_active_jobs():
    from infrastructure.logger.job_status import job_status
    return JSONResponse(content=job_status.get_all())


# -- 📄 Latest Export Summary --

@router.get("/dashboard/latest-compliance-export")
async def get_latest_compliance_export():
    logs = export_log.get_logs()
    compliance_exports = [
        log for log in logs
        if log.get("job_id") == "compliance_assistant" and "summary" in log
    ]
    if not compliance_exports:
        return JSONResponse(content={"summary": "No compliance exports yet."})

    latest = sorted(compliance_exports, key=lambda x: x["timestamp"], reverse=True)[0]
    return JSONResponse(content={"summary": latest["summary"]})

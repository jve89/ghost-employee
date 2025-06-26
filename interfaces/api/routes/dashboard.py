from fastapi import APIRouter, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from datetime import datetime
import os, shutil

from app.logs.input_log import load_input_log, append_input_log
from infrastructure.retry.retry_queue_store import retry_queue_store
from app.jobs.job_registry import list_registered_jobs
from infrastructure.logger.task_log_summary import load_recent_tasks
from infrastructure.logger.export_log_summary import get_latest_export

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
    try:
        tasks = load_task_log()
        return {"tasks": tasks[:10]}  # newest first
    except Exception as e:
        return {"error": str(e), "tasks": []}

# -- ⚙️ Active Jobs List --

@router.get("/dashboard/active-jobs")
async def get_active_jobs():
    from infrastructure.logger.job_status import job_status
    return JSONResponse(content=job_status.get_all())


# -- 📄 Latest Export Summary --

@router.get("/dashboard/latest-compliance-export")
async def get_latest_compliance_export():
    result = get_latest_export(job_id="compliance_assistant")
    return JSONResponse(content=result)

# -- 📊 Retry Stats Summary --

@router.get("/dashboard/retry-stats")
async def get_retry_stats():
    try:
        queue = retry_queue_store.get_all()
        total = len(queue)
        failed = sum(1 for t in queue if not t.get("retry_result"))
        recent = sorted(queue, key=lambda x: x.get("result_timestamp", ""), reverse=True)[:5]

        return JSONResponse(content={
            "total": total,
            "failed": failed,
            "recent": recent
        })
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

# -- 📤 Recent Export Files --

@router.get("/dashboard/recent-export-files")
async def get_recent_export_files():
    try:
        export_dir = "./exports/compliance_assistant/"
        if not os.path.exists(export_dir):
            return JSONResponse(content={"files": []})

        files = [
            f for f in os.listdir(export_dir)
            if os.path.isfile(os.path.join(export_dir, f))
        ]
        files.sort(reverse=True)
        return JSONResponse(content={"files": files[:10]})
    except Exception as e:
        print(f"[Dashboard] ❌ Failed to load export files: {e}")
        return JSONResponse(content={"files": []})

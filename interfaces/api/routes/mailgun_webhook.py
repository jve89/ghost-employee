# interfaces/api/routes/mailgun_webhook.py

from datetime import datetime
from pathlib import Path
import shutil

from fastapi import APIRouter, Request, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from starlette.status import HTTP_200_OK, HTTP_400_BAD_REQUEST

from app.jobs.job_registry import job_registry
from config.config_loader import load_job_config
from infrastructure.logger.activity_log import activity_log

import os
import json

router = APIRouter()

@router.post("/api/mailgun_webhook")
async def mailgun_webhook(request: Request):
    try:
        # Parse form data from Mailgun
        payload = await request.form()
        sender = payload.get("sender")
        subject = payload.get("subject")
        body_plain = payload.get("body-plain")
        recipient = payload.get("recipient")
        attachments = payload.getlist("attachment-1") if "attachment-1" in payload else []

        # Extract job_id from recipient email address
        job_id = derive_job_id_from_recipient(recipient)
        if not job_id:
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="No job ID found in recipient address.")

        if job_id not in job_registry:
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=f"Unknown job: {job_id}")

        # Choose text input source: attachment > body
        text_input = body_plain
        if attachments:
            content = await attachments[0].read()
            text_input = content.decode("utf-8", errors="ignore")

        if not text_input:
            raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail="No text content available to process.")

        # Load config and execute the job
        config = load_job_config(job_id)
        job = job_registry[job_id]
        activity_log.record(job_name=job_id, trigger="email", file=f"{sender} | {subject}", status="started")
        job.run(config=config, override_text=text_input)
        activity_log.record(job_name=job_id, trigger="email", file=f"{sender} | {subject}", status="completed")

        return JSONResponse(content={"status": "success"}, status_code=HTTP_200_OK)

    except Exception as e:
        return JSONResponse(content={"status": "error", "detail": str(e)}, status_code=HTTP_400_BAD_REQUEST)

def derive_job_id_from_recipient(recipient: str) -> str | None:
    """
    Extracts job ID from recipient address like ghost+crm_ops_job@domain.com
    """
    if "+" in recipient and "@" in recipient:
        local = recipient.split("@")[0]
        parts = local.split("+")
        if len(parts) == 2:
            return parts[1].strip()
    return None

@router.post("/mailgun/incoming")
async def receive_generic_email(
    sender: str = Form(...),
    subject: str = Form(...),
    attachment_1: UploadFile = File(None)
):
    try:
        timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H-%M-%S")
        base_name = f"mailgun_{timestamp}"
        save_dir = Path("watched/test_inbox")
        save_dir.mkdir(parents=True, exist_ok=True)

        # 📝 Save attachment if it's a .txt
        if attachment_1 and attachment_1.filename.endswith(".txt"):
            save_path = save_dir / f"{base_name}__{attachment_1.filename}"
            with open(save_path, "wb") as f:
                shutil.copyfileobj(attachment_1.file, f)

        # 🧠 Save email metadata
        memory_file = Path("memory") / f"{base_name}.json"
        metadata = {
            "timestamp": timestamp,
            "sender": sender,
            "subject": subject,
            "status": "saved",
            "job_type": "email_task"
        }
        with open(memory_file, "w") as f:
            f.write(json.dumps(metadata, indent=2))

        return JSONResponse(content={"status": "ok", "message": "✅ Email saved."})

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
# interfaces/api/routes/email_input.py

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from app.jobs.job_registry import get_job_by_email
from datetime import datetime

router = APIRouter()

@router.post("/email/inbound")
async def receive_email(request: Request):
    try:
        payload = await request.json()
        recipient = payload.get("recipient")
        subject = payload.get("subject", "")
        body = payload.get("body-plain", "")
        attachments = payload.get("attachments", [])
        sender = payload.get("sender", "")

        job = get_job_by_email(recipient)
        if not job:
            return JSONResponse(status_code=404, content={"error": "No matching ghost employee for this address"})

        email_data = {
            "sender": sender,
            "recipient": recipient,
            "subject": subject,
            "body": body,
            "attachments": attachments,
            "timestamp": datetime.utcnow().isoformat()
        }

        job.trigger_from_email(email_data)
        return {"message": "✅ Email received and dispatched"}

    except Exception as e:
        print(f"[Email Input] ❌ Error: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})

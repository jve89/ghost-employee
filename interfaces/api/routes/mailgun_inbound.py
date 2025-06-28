# interfaces/api/routes/mailgun_inbound.py

from fastapi import APIRouter, Request, status
from fastapi.responses import JSONResponse
import json

router = APIRouter()

@router.post("/mailgun/inbound")
async def mailgun_inbound(request: Request):
    try:
        form = await request.form()
        recipient = form.get("recipient")
        sender = form.get("sender")
        subject = form.get("subject")
        body_plain = form.get("body-plain")
        body_html = form.get("body-html")
        message_headers = form.get("message-headers")
        headers_json = json.loads(message_headers) if message_headers else {}

        print(f"[Mailgun] Received email for: {recipient}")
        print(f"[Mailgun] From: {sender}")
        print(f"[Mailgun] Subject: {subject}")
        print(f"[Mailgun] Body: {body_plain[:100]}...")

        task_data = {
            "recipient": recipient,
            "sender": sender,
            "subject": subject,
            "body": body_plain,
            "headers": headers_json
        }

        # Placeholder for pipeline integration:
        # process_inbound_email(task_data)

        return JSONResponse(content={"status": "success", "details": "Email received and parsed."}, status_code=status.HTTP_200_OK)

    except Exception as e:
        print(f"[Mailgun] Inbound error: {e}")
        return JSONResponse(content={"status": "error", "details": str(e)}, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

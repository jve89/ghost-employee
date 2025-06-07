# app/core/email_replier.py

import os
from openai import OpenAI
from dotenv import load_dotenv
from app.core.models import Task
import requests

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_reply(subject: str, summary: str, tasks: list[Task], job_config: dict) -> str:
    if not job_config.get("use_gpt_replies", False):
        return fallback_reply(subject, summary, tasks)

    try:
        task_text = "\n".join(f"- {task.description}" for task in tasks)

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": (
                    "You are a professional virtual assistant replying to a work email. "
                    "Write a clear, concise, and polite response confirming that the contents were received, "
                    "summarising the findings, and listing any actions taken or planned. "
                    "Sign off as a virtual assistant."
                )},
                {"role": "user", "content": (
                    f"Subject: {subject}\n\n"
                    f"Summary:\n{summary}\n\n"
                    f"Tasks:\n{task_text}"
                )}
            ],
            temperature=0.5,
            max_tokens=300
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        print(f"[EmailReplier] ❌ GPT failed: {e}")
        return fallback_reply(subject, summary, tasks)

def fallback_reply(subject: str, summary: str, tasks: list[Task]) -> str:
    task_lines = "\n".join(f"- {task.description}" for task in tasks)
    return (
        f"Subject: Re: {subject}\n\n"
        f"Hello,\n\n"
        f"This is a confirmation that your message was received and reviewed by our virtual assistant.\n\n"
        f"Summary:\n{summary}\n\n"
        f"Tasks identified:\n{task_lines}\n\n"
        f"Best regards,\nGhost Employee"
    )

def generate_and_send_reply(subject: str, body: str, summary: str, tasks: list[Task], job_config: dict):
    sender_email = job_config.get("sender") or os.getenv("DEFAULT_SENDER", "noreply@yourdomain.com")
    recipient_email = job_config.get("recipient") or os.getenv("DEFAULT_RECIPIENT", "test@example.com")
    reply_subject = f"Re: {subject}"

    # Step 1: Generate reply content
    message_body = generate_reply(subject, summary, tasks, job_config)

    print(f"[EmailReplier] ✉️ Generated reply:\n{message_body}\n")

    # Step 2: Send via Mailgun
    mailgun_domain = os.getenv("MAILGUN_DOMAIN")
    mailgun_api_key = os.getenv("MAILGUN_API_KEY")

    if not mailgun_domain or not mailgun_api_key:
        print("[EmailReplier] ❌ Mailgun credentials missing.")
        return

    response = requests.post(
        f"https://api.mailgun.net/v3/{mailgun_domain}/messages",
        auth=("api", mailgun_api_key),
        data={
            "from": f"Ghost Employee <{sender_email}>",
            "to": recipient_email,
            "subject": reply_subject,
            "text": message_body
        }
    )

    if response.status_code == 200:
        print("[EmailReplier] ✅ Reply sent via Mailgun.")
    else:
        print(f"[EmailReplier] ❌ Failed to send email: {response.status_code} — {response.text}")

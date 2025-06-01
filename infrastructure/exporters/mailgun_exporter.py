import os
import requests
from dotenv import load_dotenv
from app.core.models import Task
from app.core.interfaces import Exporter
from datetime import datetime

load_dotenv()

class MailgunExporter(Exporter):
    def export(self, task: Task):
        api_key = os.getenv("MAILGUN_API_KEY")
        domain = os.getenv("MAILGUN_DOMAIN")
        to_email = os.getenv("MAILGUN_TO_EMAIL", "your@email.com")  # default if not set

        if not api_key or not domain:
            print("[MailgunExporter] Missing credentials.")
            return

        subject = f"New Task: {task.description}"
        body = f"""
        Task: {task.description}
        Due: {task.due_date}
        Assigned to: {task.assigned_to}
        """

        response = requests.post(
            f"https://api.mailgun.net/v3/{domain}/messages",
            auth=("api", api_key),
            data={
                "from": f"Ghost Employee <bot@{domain}>",
                "to": [to_email],
                "subject": subject,
                "text": body
            }
        )

        if response.status_code == 200:
            print("[MailgunExporter] Email sent successfully.")
        else:
            print(f"[MailgunExporter] Failed to send email: {response.text}")

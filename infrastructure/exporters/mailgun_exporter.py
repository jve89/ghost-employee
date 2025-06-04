import os
import requests
from dotenv import load_dotenv
from app.core.interfaces import Exporter

load_dotenv()

class MailgunExporter(Exporter):
    def export(self, output_data: dict, config: dict):
        api_key = os.getenv("MAILGUN_API_KEY")
        domain = os.getenv("MAILGUN_DOMAIN")
        to_emails = config.get("recipients", [os.getenv("MAILGUN_TO_EMAIL", "test@example.com")])
        subject = config.get("subject", "Ghost Employee Export")
        message = config.get("message", "Summary:\n{{summary}}\n\nTasks:\n{{tasks}}")

        if not api_key or not domain:
            print("[MailgunExporter] Missing credentials.")
            return

        response = requests.post(
            f"https://api.mailgun.net/v3/{domain}/messages",
            auth=("api", api_key),
            data={
                "from": os.getenv("MAILGUN_FROM", f"Ghost Employee <bot@{domain}>"),
                "to": to_emails,
                "subject": subject,
                "text": message
            }
        )

        if response.status_code == 200:
            print("[MailgunExporter] Email sent successfully.")
        else:
            print(f"[MailgunExporter] Failed to send email: {response.status_code} - {response.text}")

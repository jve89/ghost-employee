import os
import requests
import json
from dotenv import load_dotenv
from app.core.interfaces import Exporter

load_dotenv()

class MailgunExporter(Exporter):
    def __init__(self, config: dict = None, job_id: str = "unknown_job"):
        self.config = config or {}
        self.job_id = job_id

    def export(self, output_data: dict, config: dict):
        config = self.config
        api_key = os.getenv("MAILGUN_API_KEY")
        domain = os.getenv("MAILGUN_DOMAIN")
        to_emails = config.get("recipients", [os.getenv("MAILGUN_TO_EMAIL", "test@example.com")])
        subject = config.get("subject", "Ghost Employee Export")
        default_message = config.get("message", "Summary:\n{{summary}}\n\nTasks:\n{{tasks}}")

        if not api_key or not domain:
            print("[MailgunExporter] ❌ Missing Mailgun credentials.")
            return

        message = self._generate_message(output_data, default_message)

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
            print("[MailgunExporter] ✅ Email sent successfully.")
        else:
            print(f"[MailgunExporter] ❌ Failed to send email: {response.status_code} - {response.text}")

    def _generate_message(self, output_data: dict, fallback_template: str) -> str:
        summary = output_data.get("summary", "")
        tasks = output_data.get("tasks", [])
        task_text = "\n".join(f"- {t.get('description', '')}" for t in tasks)

        if not summary or not tasks:
            return fallback_template.replace("{{summary}}", summary).replace("{{tasks}}", task_text)

        try:
            from openai import OpenAI
            client = OpenAI()

            prompt = (
                "Write a short, professional email summarising a compliance review.\n"
                f"Summary:\n{summary}\n\n"
                f"Tasks:\n{task_text}\n\n"
                "Tone: Friendly, professional, and natural. Keep it concise and human-sounding."
            )

            completion = client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
            )

            return completion.choices[0].message.content.strip()

        except Exception as e:
            print(f"[MailgunExporter] ⚠️ GPT message generation failed: {e}")
            return fallback_template.replace("{{summary}}", summary).replace("{{tasks}}", task_text)

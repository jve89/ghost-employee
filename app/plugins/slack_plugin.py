# app/plugins/slack_plugin.py

import requests
from app.core.models import Task
from datetime import datetime

class SlackPlugin:
    def can_handle(self, task: Task) -> bool:
        """Decide if this task should be handled by Slack."""
        return "slack" in task.description.lower() or "notify" in task.description.lower()

    def handle(self, task: Task) -> bool:
        """Send a message to Slack using a webhook URL from the task metadata."""
        try:
            webhook_url = task.metadata.get("slack_webhook_url")
            if not webhook_url:
                print("[SlackPlugin] ❌ No webhook URL in task metadata.")
                return False

            message = f":ghost: *Ghost Employee Notification*\n{task.description}\n_Time: {datetime.utcnow().isoformat()}_"

            response = requests.post(webhook_url, json={"text": message})

            if response.status_code == 200:
                print("[SlackPlugin] ✅ Message sent successfully.")
                return True
            else:
                print(f"[SlackPlugin] ❌ Slack responded with status {response.status_code}")
                return False

        except Exception as e:
            print(f"[SlackPlugin] ❌ Exception occurred: {e}")
            return False

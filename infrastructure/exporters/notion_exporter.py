import os
import requests
from datetime import datetime
from typing import Dict, Any

NOTION_API_KEY = os.getenv("NOTION_API_KEY")
NOTION_VERSION = "2022-06-28"
NOTION_API_URL = "https://api.notion.com/v1/pages"


class NotionExporter:
    def __init__(self, config: Dict[str, Any], job_id: str = "unknown_job"):
        self.config = config
        self.job_id = job_id
        self.headers = {
            "Authorization": f"Bearer {NOTION_API_KEY}",
            "Content-Type": "application/json",
            "Notion-Version": NOTION_VERSION,
        }
        self.database_id = config.get("database_id")

    def export(self, output_data: Dict[str, Any], config: Dict[str, Any]):
        if not self.database_id:
            print("[NotionExporter] ❌ Missing Notion database_id in config.")
            return

        title = f"{self.job_id} – {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        summary = str(output_data.get("summary", "No summary"))
        source_file = output_data.get("source_file", "unknown")

        # First task only (Notion only accepts one row per payload)
        first_task = output_data.get("tasks", [{}])[0]
        due_date = first_task.get("due_date")
        assignee = first_task.get("assignee")

        payload = {
            "parent": {"database_id": self.database_id},
            "properties": {
                "Title": {
                    "title": [{"text": {"content": title}}]
                },
                "Description": {
                    "rich_text": [{"text": {"content": summary}}]
                },
                "Due Date": {
                    "date": {"start": due_date} if due_date else None
                },
                "Assigned To": {
                    # Empty people field – you could map this to actual Notion users later
                    "people": []
                },
                "Priority": {
                    "select": {"name": "Normal"}  # Must match one of your select options
                },
                "Source File": {
                    "select": {"name": source_file} if source_file else None
                },
                "Confidence": {
                    "select": {"name": "n/a"}
                },
            }
        }

        # Strip None values (especially Due Date if not present)
        payload["properties"] = {
            k: v for k, v in payload["properties"].items() if v is not None
        }

        response = requests.post(NOTION_API_URL, headers=self.headers, json=payload)
        if response.status_code == 200:
            print("[NotionExporter] ✅ Successfully exported to Notion.")
        else:
            print(f"[NotionExporter] ❌ Failed: {response.status_code} – {response.text}")

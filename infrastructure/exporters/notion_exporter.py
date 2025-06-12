import os
import requests
from datetime import datetime
from typing import Dict, Any
from dotenv import load_dotenv  
from infrastructure.retry.retry_queue_store import retry_queue_store
from app.core.models import Task  # Make sure this matches your task model

load_dotenv()                   

NOTION_API_KEY = os.getenv("NOTION_API_KEY")
NOTION_VERSION = "2022-06-28"
NOTION_API_URL = "https://api.notion.com/v1/pages"

# Map assignee names → Notion user IDs
NOTION_USER_MAP = {
    "Johan": "5a2e3241-2f1d-4b8f-b44c-d63528c2ac1b",
    # You can add more users here later
}

class NotionExporter:
    def __init__(self, config: Dict[str, Any], job_id: str = "unknown_job"):
        self.config = config
        self.job_id = job_id
        self.headers = {
            "Authorization": f"Bearer {NOTION_API_KEY}",
            "Content-Type": "application/json",
            "Notion-Version": NOTION_VERSION,
        }
        self.database_id = config.get("database_id") or os.getenv("NOTION_DATABASE_ID")

    def export(self, output_data: Dict[str, Any], config: Dict[str, Any]):
        if not self.database_id:
            print(f"[DEBUG] ENV DB ID: {os.getenv('NOTION_DATABASE_ID')}")
            print(f"[DEBUG] Final DB ID: {self.database_id}")
            print("[NotionExporter] ❌ Missing Notion database_id in config.")
            return

        summary = str(output_data.get("summary", "No summary"))
        source_file = output_data.get("source_file", "unknown")
        tasks = output_data.get("tasks", [])

        if not tasks:
            print("[NotionExporter] ⚠️ No tasks found – exporting summary only.")
            tasks = [{"description": summary}]

        for i, task in enumerate(tasks):
            title = f"{self.job_id} – Task {i+1} – {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            due_date = task.get("due_date")
            assignee = task.get("assignee", "Unassigned")
            priority = task.get("priority", "Normal")  # ← NEW: use priority if present

            payload = {
                "parent": {"database_id": self.database_id},
                "properties": {
                    "Title": {
                        "title": [{"text": {"content": title}}]
                    },
                    "Description": {
                        "rich_text": [{"text": {"content": task.get('description', '')}}]
                    },
                    "Due Date": {
                        "date": {"start": due_date} if due_date else None
                    },
                    "Assigned To": {
                        "people": [{"id": NOTION_USER_MAP[assignee]}] if assignee in NOTION_USER_MAP else []
                    },
                    "Priority": {
                        "select": {"name": priority}  # ← NEW: use task priority dynamically
                    },
                    "Source File": {
                        "select": {"name": source_file} if source_file else None
                    },
                    "Confidence": {
                        "select": {"name": "n/a"}
                    },
                }
            }

            # Strip None values
            payload["properties"] = {
                k: v for k, v in payload["properties"].items() if v is not None
            }

            response = requests.post(NOTION_API_URL, headers=self.headers, json=payload)
            if response.status_code == 200:
                print(f"[NotionExporter] ✅ Task {i+1} exported to Notion.")
            else:
                print(f"[NotionExporter] ❌ Task {i+1} failed: {response.status_code} – {response.text}")
                
                # Log this task to persistent retry queue
                try:
                    task_obj = Task(**task)
                    retry_queue_store.add(task_obj, timestamp=datetime.utcnow().isoformat())
                    print(f"[NotionExporter] 🔁 Task {i+1} added to retry queue.")
                except Exception as e:
                    print(f"[NotionExporter] ⚠️ Failed to add task to retry queue: {e}")

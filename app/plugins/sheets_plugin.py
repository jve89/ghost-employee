# app/plugins/sheets_plugin.py

import os
import json
from app.core.models import Task
from app.core.interfaces import Plugin
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

class SheetsPlugin(Plugin):
    def __init__(self, config: dict, job_id: str = "unknown"):
        self.sheet_id = config.get("sheet_id") or os.getenv("GOOGLE_SHEET_ID")
        self.range = config.get("range", "Sheet1!A1")
        self.creds = self.get_google_credentials()
        self.service = build("sheets", "v4", credentials=self.creds)
        self.sheet = self.service.spreadsheets()

    def get_google_credentials(self) -> Credentials:
        json_path = os.getenv("GOOGLE_SERVICE_ACCOUNT_PATH", "config/credentials/ghost_employee_sheets_key.json")

        if not os.path.exists(json_path):
            raise RuntimeError(f"Google Sheets credential file not found at {json_path}")

        try:
            with open(json_path, "r") as f:
                json_dict = json.load(f)

            return Credentials.from_service_account_info(
                json_dict,
                scopes=["https://www.googleapis.com/auth/spreadsheets"]
            )
        except Exception as e:
            raise RuntimeError(f"Failed to load service account credentials: {e}")

    def can_handle(self, task: Task) -> bool:
        return "sheet" in task.description.lower()

    def handle(self, task: Task) -> dict:
        row = [
            task.description,
            task.entity or "",
            task.assignee or "",
            task.summary[:100],  # limit summary size
            task.created_at,
        ]

        try:
            self.sheet.values().append(
                spreadsheetId=self.sheet_id,
                range=self.range,
                valueInputOption="RAW",
                body={"values": [row]},
            ).execute()

            return {"status": "success", "message": "Task logged to Google Sheets"}
        except Exception as e:
            return {"status": "failed", "message": str(e)}
    
    def export(self, data: dict, config: dict) -> None:
        tasks = data.get("tasks", [])
        if not tasks:
            raise ValueError("No tasks to export to Google Sheets")

        for task in tasks:
            row = [
                task.get("description", ""),
                task.get("entity", ""),
                task.get("assignee", ""),
                data.get("summary", "")[:100],
                task.get("created_at", ""),
            ]

            self.sheet.values().append(
                spreadsheetId=self.sheet_id,
                range=self.range,
                valueInputOption="RAW",
                body={"values": [row]},
            ).execute()
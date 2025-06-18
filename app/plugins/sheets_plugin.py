# app/plugins/sheets_plugin.py

import os
import json
from app.core.models import Task
from app.core.interfaces import Plugin
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from dotenv import load_dotenv

load_dotenv()

class SheetsPlugin(Plugin):
    def __init__(self):
        self.sheet_id = os.getenv("GOOGLE_SHEET_ID")
        self.creds = self.get_google_credentials()
        self.service = build("sheets", "v4", credentials=self.creds)
        self.sheet = self.service.spreadsheets()

    def get_google_credentials(self) -> Credentials:
        path = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
        if not path:
            raise RuntimeError("Missing GOOGLE_SERVICE_ACCOUNT_JSON in .env")

        try:
            with open(path, "r") as f:
                info = json.load(f)
            return Credentials.from_service_account_info(
                info, scopes=["https://www.googleapis.com/auth/spreadsheets"]
            )
        except Exception as e:
            raise RuntimeError(f"Failed to load Google credentials from file: {e}")

    def can_handle(self, task: Task) -> bool:
        # Example: send any task with "sheet" keyword to Sheets
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
                range="Sheet1!A1",
                valueInputOption="RAW",
                body={"values": [row]},
            ).execute()

            return {"status": "success", "message": "Task logged to Google Sheets"}
        except Exception as e:
            return {"status": "failed", "message": str(e)}

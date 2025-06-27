# infrastructure/utils/google_sheets_exporter.py

import gspread
from google.oauth2.service_account import Credentials

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
SERVICE_ACCOUNT_FILE = "config/secrets/ghost_employee_service_account.json"

def export_task_to_sheet(sheet_id: str, task: str, status: str, job_id: str):
    print(f"[DEBUG] Exporting task. Sheet ID: {sheet_id}, Task: {task}, Status: {status}, Job ID: {job_id}")
    creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    client = gspread.authorize(creds)

    try:
        spreadsheet = client.open_by_key(sheet_id)
        sheet = spreadsheet.sheet1
    except Exception as e:
        print(f"[SheetsExporter] ❌ Failed to open sheet: {e}")
        return False

    try:
        sheet.append_row([job_id, task, status])
        print(f"[SheetsExporter] ✅ Exported task: {task}")
        return True
    except Exception as e:
        print(f"[SheetsExporter] ❌ Failed to append row: {e}")
        return False
# scripts/list_worksheets.py

import os
import gspread
from google.oauth2.service_account import Credentials

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
SERVICE_ACCOUNT_FILE = "config/secrets/ghost_employee_service_account.json"
SHEET_ID = os.getenv("GOOGLE_SHEET_ID")

creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
client = gspread.authorize(creds)

spreadsheet = client.open_by_key(SHEET_ID)
worksheets = spreadsheet.worksheets()

print(f"\n✅ Available worksheets in {spreadsheet.title}:")
for ws in worksheets:
    print(f" - Title: {ws.title}")

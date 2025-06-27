import os
import gspread
from google.oauth2.service_account import Credentials

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
SERVICE_ACCOUNT_FILE = "config/secrets/ghost_employee_service_account.json"

GOOGLE_SHEET_ID = os.getenv("GOOGLE_SHEET_ID")

creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
client = gspread.authorize(creds)

try:
    sheet = client.open_by_key(GOOGLE_SHEET_ID).sheet1
    print("✅ Successfully opened the sheet!")
    sheet.append_row(["Test", "Success", "✅"])
    print("✅ Successfully appended test row.")
except Exception as e:
    print(f"❌ Failed: {e}")

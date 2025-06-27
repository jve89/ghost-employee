import os
import gspread
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv

load_dotenv()

SHEET_ID = os.getenv("GOOGLE_SHEET_ID")
SERVICE_ACCOUNT_FILE = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

print(f"[DEBUG] SERVICE_ACCOUNT_FILE: {SERVICE_ACCOUNT_FILE}")
creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
client = gspread.authorize(creds)

try:
    sheet = client.open_by_key(SHEET_ID).sheet1
    sheet.append_row(["test_job", "test_task", "success"])
    print("✅ Successfully appended test row.")
except Exception as e:
    print(f"❌ Failed to append row: {e}")

# scripts/test_gspread_direct.py

import gspread
from google.oauth2.service_account import Credentials

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
SERVICE_ACCOUNT_FILE = "config/secrets/ghost_employee_service_account.json"
SHEET_ID = "1o2E0vcsdEWC2L6_JTpzkIXJ45UAd3Wz18YtPnHtaL0w"

creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
client = gspread.authorize(creds)

try:
    spreadsheet = client.open_by_key(SHEET_ID)
    worksheets = spreadsheet.worksheets()
    print(f"\n✅ Successfully opened: {spreadsheet.title}")
    print(f"✅ Worksheets found:")
    for ws in worksheets:
        print(f" - {ws.title}")
except Exception as e:
    print(f"❌ Failed direct test: {e}")

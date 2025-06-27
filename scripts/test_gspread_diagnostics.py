# scripts/test_gspread_diagnostics.py

import os
import gspread
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv

load_dotenv()  # ✅ This will now load your .env automatically

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
SERVICE_ACCOUNT_FILE = "config/secrets/ghost_employee_service_account.json"
GOOGLE_SHEET_ID = os.getenv("GOOGLE_SHEET_ID")

def main():
    try:
        creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        client = gspread.authorize(creds)

        # List all spreadsheets accessible
        print("✅ Successfully authenticated with service account.")

        # Attempt to open the target spreadsheet by key
        print(f"🔍 Attempting to open spreadsheet with ID: {GOOGLE_SHEET_ID}")
        spreadsheet = client.open_by_key(GOOGLE_SHEET_ID)
        print(f"✅ Successfully opened spreadsheet: {spreadsheet.title}")

        # List all worksheet names
        worksheets = spreadsheet.worksheets()
        print("📄 Worksheets in this spreadsheet:")
        for ws in worksheets:
            print(f" - {ws.title}")

        # Attempt to open "Sheet1"
        try:
            sheet = spreadsheet.worksheet("Sheet1")
            print("✅ 'Sheet1' found and accessible.")
        except Exception as e:
            print(f"❌ Failed to access 'Sheet1': {e}")

    except Exception as e:
        print(f"❌ Failed diagnostics: {e}")

if __name__ == "__main__":
    main()

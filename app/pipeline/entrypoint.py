# app/pipeline/entrypoint.py

import os
import random
import time
from app.parser.rule_parser import extract_tasks_from_text
from app.logs.task_log_store import append_task_log
from infrastructure.utils.google_sheets_exporter import export_task_to_sheet
from dotenv import load_dotenv

load_dotenv()

GOOGLE_SHEET_ID = os.getenv("GOOGLE_SHEET_ID")

def handle_input(source, job_id, text, files):
    print(f"[Pipeline] 🚀 Triggered from {source} for job {job_id}")
    print(f"[Pipeline] 📝 Text: {text[:50]}...")  # show first 50 chars for safety
    print(f"[Pipeline] 📎 Files: {files}")

    tasks = extract_tasks_from_text(text)
    print(f"[Pipeline] 🧠 Extracted {len(tasks)} task(s):")
    for task in tasks:
        print(f" - {task}")

    # Simulate execution + structured logging
    for task in tasks:
        time.sleep(0.1)  # simulate processing time
        success = random.choice([True, True, True, False])  # 75% success rate
        status = "✅ Success" if success else "❌ Failed"
        append_task_log(job_id, task, success)
        print(f"[DEBUG] GOOGLE_SHEET_ID in pipeline: {GOOGLE_SHEET_ID}")
        export_task_to_sheet(sheet_id=GOOGLE_SHEET_ID, task=task, status=status, job_id=job_id)
        print(f"[Pipeline] {status}: {task}")

    print(f"[Pipeline] ✅ Processing complete.")

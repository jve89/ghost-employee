# app/pipeline/entrypoint.py

from app.parser.rule_parser import extract_tasks_from_text

def handle_input(source, job_id, text, files):
    print(f"[Pipeline] 🚀 Triggered from {source} for job {job_id}")
    print(f"[Pipeline] 📝 Text: {text[:50]}...")  # show first 50 chars for safety
    print(f"[Pipeline] 📎 Files: {files}")
    
    tasks = extract_tasks_from_text(text)
    print(f"[Pipeline] 🧠 Extracted {len(tasks)} task(s):")
    for task in tasks:
        print(f" - {task}")

    print(f"[Pipeline] ✅ Processing complete.")

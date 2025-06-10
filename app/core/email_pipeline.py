import os
import uuid
import json
from datetime import datetime
from infrastructure.task_parser.gpt_parser import parse_text_to_summary
from app.services.task_service import extract_tasks
from app.services.simple_executor import execute_tasks
from app.services.export_dispatcher import export_results
from app.core.job_memory import JobMemory
from app.core.email_replier import generate_reply, generate_and_send_reply

def process_email_content(subject: str, body: str, job_config: dict):
    print(f"[EmailPipeline] 📩 Processing email: {subject}")

    combined_text = f"Subject: {subject}\n\n{body}"

    try:
        summary = parse_text_to_summary(combined_text, job_config)
        tasks = extract_tasks(summary, job_config)
        results = execute_tasks(tasks, job_config)

        export_results(
            job_id=job_config["job_id"],
            summary=summary,
            tasks=tasks,
            execution_results=results,
            job_config=job_config,
        )

        # Save to memory
        JobMemory(job_config["job_name"]).append_entry(
            subject=subject,
            summary=summary.content,
            tasks=[t.description for t in tasks],
            from_email=job_config.get("sender", "unknown")
        )

        # 🧠 Auto-reply if enabled
        if job_config.get("use_gpt_replies"):
            generate_and_send_reply(subject, body, summary.content, tasks, job_config)

        # ✅ Log to email jobs memory (for dashboard tile)
        log_email_triggered_job(subject, job_config, status="completed")

        print(f"[EmailPipeline] ✅ Email processed and saved to memory.")

    except Exception as e:
        print(f"[EmailPipeline] ❌ Failed to process email: {e}")
        log_email_triggered_job(subject, job_config, status="error")

def log_email_triggered_job(subject, job_config, status="completed"):
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "job_type": job_config.get("job_name", "unknown"),
        "sender": job_config.get("sender", "unknown"),
        "subject": subject,
        "status": status
    }

    os.makedirs("memory", exist_ok=True)
    with open(f"memory/mailgun_{uuid.uuid4()}.json", "w") as f:
        json.dump(entry, f, indent=2)

# app/services/email_template_service.py

from datetime import datetime

def generate_email_body(summary: str, tasks: list, results: list) -> str:
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    lines = [
        f"🧠 **Ghost Employee Job Report**",
        f"🕒 Completed at: {timestamp}",
        "",
        "## Summary",
        summary.strip(),
        "",
        "## Tasks",
    ]

    for task in tasks:
        lines.append(f"- {task['action']} → `{task.get('status', 'pending')}`")

    lines.append("")
    lines.append("## Execution Results")

    for result in results:
        lines.append(f"- {result.get('description', 'No description')} → `{result.get('status', 'unknown')}`")

    lines.append("")
    lines.append("This message was generated automatically by Ghost Employee 🤖.")

    return "\n".join(lines)

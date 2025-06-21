import re
from app.core.models import Task

HR_KEYWORDS = [
    "offboard", "onboard", "promotion", "payroll", "contract", "employee", "personnel file",
    "hired", "leaving", "join the company", "start date", "termination", "HR"
]

def handle_hr_task(task_description: str) -> tuple[bool, str, dict | None]:
    """
    Match HR-related tasks and simulate execution.
    Returns: (success: bool, log_message: str, export_entry: dict | None)
    """
    patterns = [
        (r"offboard (\w+ \w+)", "Offboarding {name} initiated.", "offboarding"),
        (r"promote (\w+ \w+)", "Promotion process started for {name}.", "promotion"),
        (r"onboard (\w+ \w+)", "Onboarding process started for {name}.", "onboarding"),
        (r"notify payroll", "Payroll department has been notified.", "payroll_update"),
        (r"schedule (interview|hr meeting|exit interview)", "Scheduled {meeting_type}.", "schedule"),
        (r"update (digital )?personnel file", "Personnel file has been updated.", "file_update"),
    ]

    for pattern, response_template, tag in patterns:
        match = re.search(pattern, task_description, re.IGNORECASE)
        if match:
            value = match.group(1) if match.groups() else "unspecified"
            log_msg = response_template.format(name=value, meeting_type=value)
            export_entry = {
                "type": "hr_action",
                "tag": tag,
                "summary": log_msg,
                "details": {
                    "actor": value,
                    "original_text": task_description
                }
            }
            return True, f"[HRPlugin] ✅ {log_msg}", export_entry

    # Fallback: simple keyword match
    lowered = task_description.lower()
    if any(keyword in lowered for keyword in HR_KEYWORDS):
        fallback_msg = f"[HRPlugin] ✅ Handled general HR task: {task_description}"
        export_entry = {
            "type": "hr_action",
            "tag": "generic",
            "summary": fallback_msg,
            "details": {
                "original_text": task_description
            }
        }
        return True, fallback_msg, export_entry

    return False, "[HRPlugin] ❌ No HR pattern matched", None

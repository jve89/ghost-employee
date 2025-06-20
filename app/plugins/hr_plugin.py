# app/plugins/hr_plugin.py

import re
from app.core.models import Task

HR_KEYWORDS = [
    "offboard", "onboard", "promotion", "payroll", "contract", "employee", "personnel file",
    "hired", "leaving", "join the company", "start date", "termination", "HR"
]

def handle_hr_task(task_description: str) -> tuple[bool, str]:
    """
    Match HR-related tasks and simulate execution.
    Returns: (success: bool, message: str)
    """
    patterns = [
        (r"offboard (\w+ \w+)", "Offboarding {name} initiated."),
        (r"promote (\w+ \w+)", "Promotion process started for {name}."),
        (r"onboard (\w+ \w+)", "Onboarding process started for {name}."),
        (r"notify payroll", "Payroll department has been notified."),
        (r"schedule (interview|hr meeting|exit interview)", "Scheduled {meeting_type}."),
        (r"update (digital )?personnel file", "Personnel file has been updated."),
    ]

    for pattern, response_template in patterns:
        match = re.search(pattern, task_description, re.IGNORECASE)
        if match:
            name_or_type = match.group(1) if match.groups() else "unspecified"
            message = response_template.format(name=name_or_type, meeting_type=name_or_type)
            return True, f"[HRPlugin] ✅ {message}"

    # Fallback: simple keyword match
    lowered = task_description.lower()
    if any(keyword in lowered for keyword in HR_KEYWORDS):
        return True, f"[HRPlugin] ✅ Handled general HR task: {task_description}"

    return False, "[HRPlugin] ❌ No HR pattern matched"

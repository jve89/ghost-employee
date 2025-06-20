# infrastructure/email/email_subject_matcher.py

import re
from typing import Optional

# 📌 Define subject patterns per job_id
JOB_SUBJECT_PATTERNS = {
    "compliance_assistant": [r"\bcompliance\b", r"🛡️"],
    "hr_onboarding_assistant": [r"\bonboarding\b", r"intern"],
    "crm_ops_job": [r"\bclient\b", r"\bsync\b", r"\bCRM\b"],
    "example_job": [r"\bdemo\b", r"\bsample\b"],
}

def match_job_id(subject: str) -> Optional[str]:
    normalized = subject.lower()
    for job_id, patterns in JOB_SUBJECT_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, normalized, re.IGNORECASE):
                return job_id
    return None

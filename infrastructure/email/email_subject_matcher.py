# infrastructure/email/email_subject_matcher.py

import re
from typing import Optional

# 📌 Define subject patterns per job_id
JOB_SUBJECT_PATTERNS = {
    "base_demo": [r"\bdemo\b", r"\bsample\b", r"\bonboarding\b", r"\bcompliance\b", r"\bclient\b", r"🛡️"],
}

def match_job_id(subject: str) -> Optional[str]:
    normalized = subject.lower()
    for job_id, patterns in JOB_SUBJECT_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, normalized, re.IGNORECASE):
                return job_id
    return None

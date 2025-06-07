# test_email_pipeline.py

import os
import sys
sys.path.insert(0, os.path.abspath("."))

from app.core.email_pipeline import process_email_content

# Simulate a job config
job_config = {
    "job_id": "compliance_analyst",
    "job_name": "compliance_analyst",
    "use_gpt_replies": True,
    "sender": "jovanerkel@gmail.com",  # Simulated sender
    "recipient": "jovanerkel@gmail.com"
}

# Simulate incoming email
subject = "Weekly Compliance Report"
body = """
Hi team,

Attached is this week's performance report. Please archive it and prepare a summary.

Thanks,
Compliance Team
"""

# Process it
process_email_content(subject, body, job_config)

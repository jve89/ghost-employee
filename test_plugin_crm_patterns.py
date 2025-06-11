# test_plugin_crm_patterns.py

from app.plugins.crm_plugin import CRMPlugin

# Simulate the `task` object that the plugin expects
class DummyTask:
    def __init__(self, description):
        self.description = description
        self.entity = "Alex"
        self.job_id = "test_crm_job"

# Sample test cases
test_descriptions = [
    "Complete onboarding form for Alex",
    "Schedule orientation for new hire",
    "Add Jane Doe to CRM",
    "Check in with lead John Smith",
    "Follow up with prospect from last week",
    "Send welcome email to Emily",
    "Update contact record for Martin",
    "Modify contact for sales rep",
    "Create new lead profile in CRM",
    "Book intro call with candidate",
]

plugin = CRMPlugin()

print("\n[CRMPlugin Regex Test Results]")
for desc in test_descriptions:
    task = DummyTask(desc)
    matched = plugin.can_handle(task)
    result = "✅ MATCH" if matched else "❌ NO MATCH"
    print(f"{result} | {desc}")

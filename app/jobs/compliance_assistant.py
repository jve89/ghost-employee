# app/jobs/compliance_assistant.py

class ComplianceAssistantJob:
    job_name = "Compliance Assistant"

    @staticmethod
    def generate_tasks_from_summary(summary: str) -> list[str]:
        """
        Simple rule-based task extractor for compliance documents.
        This can later be replaced or augmented by GPT logic.
        """
        keywords = [
            "non-compliance", "audit", "incident", "regulation",
            "follow-up", "deadline", "report", "escalation", "corrective action"
        ]
        lines = summary.splitlines()
        return [
            line.strip() for line in lines
            if any(kw in line.lower() for kw in keywords)
        ]

    def execute(self, task: str):
        """
        Simulate execution of a compliance task.
        """
        print(f"[ComplianceAssistantJob] ✅ Executing: {task}")

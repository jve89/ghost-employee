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
    
    def trigger_from_email(self, email_data: dict):
        """
        Handles inbound email, triggers pipeline.
        """
        print(f"[ComplianceAssistantJob] 📩 Email received from {email_data['sender']} with subject: {email_data['subject']}")

        # Simulate pipeline trigger
        from app.pipeline.entrypoint import handle_input  # adjust path if needed
        handle_input(
            source="email_input",
            job_id="compliance_assistant",
            text=email_data["body"],
            files=email_data["attachments"]
        )

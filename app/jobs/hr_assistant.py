from app.jobs.base_job import BaseJob

class HRAssistantJob(BaseJob):
    def generate_tasks_from_summary(self, summary: str) -> list[str]:
        # Sample prompt-response parsing logic for HR tasks
        lines = summary.splitlines()
        return [
            line.strip() for line in lines
            if any(kw in line.lower() for kw in ["verwerken", "mutatie", "arbeidsvoorwaarden", "personeelsdossier", "cao", "contract", "in dienst", "uit dienst"])
        ]

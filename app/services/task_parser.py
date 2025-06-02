from app.core.models import Task

class GPTTaskParser:
    def parse(self, summary: str) -> list[dict]:
        # Dummy parser logic for testing
        return [
            {"description": "Create intern onboarding sheet"},
            {"description": "Send welcome email to new interns"}
        ]

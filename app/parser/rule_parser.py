# app/parser/rule_parser.py

def extract_tasks_from_text(text: str) -> list[str]:
    """
    Extracts task-relevant lines from input text using simple keyword matching.
    Used by jobs like Compliance Assistant to detect follow-ups.
    """
    keywords = [
        "non-compliance", "incident", "follow-up", "audit", "deadline",
        "escalation", "report", "corrective action", "violation", "breach"
    ]
    lines = text.splitlines()
    return [
        line.strip() for line in lines
        if any(kw in line.lower() for kw in keywords)
    ]

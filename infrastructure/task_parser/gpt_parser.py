import os
import json
from openai import OpenAI
from app.core.models import Summary, Task
from app.core.interfaces import TaskParser
from datetime import datetime
from dotenv import load_dotenv
from app.core.job_memory import JobMemory

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class GPTTaskParser(TaskParser):
    def extract_tasks(self, summary: Summary, job_id: str, preferences: dict | None = None) -> list[Task]:
        print("[GPTTaskParser] Extracting tasks from GPT...")

        # Load memory for this job
        memory = JobMemory(job_id)
        last_summary = memory.get_last_summary() or "None"
        preferences = preferences or memory.get_preferences()

        tone = preferences.get("tone", "neutral")
        priorities = preferences.get("priority_keywords", [])
        task_hint = preferences.get("task_hint", "")

        try:
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": (
                        f"You are a helpful assistant that extracts structured tasks from summaries.\n\n"
                        f"Tone preference: {tone}\n"
                        f"Priority keywords: {', '.join(priorities) if priorities else 'None'}\n"
                        f"Task hint: {task_hint}\n"
                        f"Last summary you processed was:\n{last_summary}\n\n"
                        f"Return a JSON array of tasks. Each task must include:\n"
                        f"- 'description': What to do\n"
                        f"- 'entity': The person involved (e.g. Alice or Bob)\n"
                        f"- 'company': The organisation involved (e.g. Acme Corp)\n"
                        f"- 'assignee': Who is responsible (if known)"
                    )},

                    {"role": "user", "content": summary.content}
                ],
                temperature=0.3,
                max_tokens=500
            )

            raw_json = response.choices[0].message.content.strip()
            parsed = json.loads(raw_json)

            tasks = []
            for item in parsed:
                description = item.get("description") or item.get("task") or "No description"
                assignee = item.get("assignee") or item.get("assigned_to")

                # Prefer 'entity' or 'contact' for person, fallback to 'company'
                entity = item.get("entity") or item.get("contact") or item.get("company") or "Unknown"
                company = item.get("company") or None

                tasks.append(Task(
                    description=description,
                    entity=entity,
                    assignee=assignee,
                    job_id=job_id,
                    source=summary.source_file,
                    summary=summary.content,
                    created_at=datetime.utcnow().isoformat()
                ))

            return tasks

        except Exception as e:
            print(f"[GPTTaskParser] Failed to parse tasks: {e}")
            return [
                Task(
                    description="Task parsing failed – manual review needed.",
                    assignee=None,
                    job_id=job_id,
                    source=summary.source_file,
                    summary=summary.content,
                    created_at=datetime.utcnow().isoformat()
                )
            ]

def parse_text_to_summary(text: str, job_config: dict) -> Summary:
    print("[GPTParser] Generating summary with GPT...")

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": (
                    "You are an assistant summarising the content of an incoming email. "
                    "Write a concise summary, capturing key points and implied tasks."
                )},
                {"role": "user", "content": text}
            ],
            temperature=0.5,
            max_tokens=300
        )

        content = response.choices[0].message.content.strip()
        return Summary(
            content=content,
            source_file=job_config.get("sender", "email"),
            generated_at=datetime.utcnow().isoformat()  # ✅ Corrected field
        )

    except Exception as e:
        print(f"[GPTParser] ❌ Failed to summarise: {e}")
        return Summary(
            content="Summary generation failed.",
            source_file="email",
            generated_at=datetime.utcnow().isoformat()  # ✅ Corrected fallback
        )
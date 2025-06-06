import os
import json
from openai import OpenAI
from app.core.models import Summary, Task
from app.core.interfaces import TaskParser
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class GPTTaskParser(TaskParser):
    def extract_tasks(self, summary: Summary, job_id: str) -> list[Task]:
        print("[GPTTaskParser] Extracting tasks from GPT...")

        try:
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": (
                        "You are a helpful assistant that extracts structured tasks from summaries. "
                        "Reply with a JSON array of objects, each with 'description' and 'assignee'."
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
                tasks.append(Task(
                    description=item.get("description") or item.get("task") or "No description",
                    assignee=item.get("assignee") or item.get("assigned_to"),
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

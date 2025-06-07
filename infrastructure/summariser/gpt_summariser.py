import os
from openai import OpenAI
from datetime import datetime
from dotenv import load_dotenv

from app.core.models import Summary
from app.core.interfaces import Summariser

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class GPTSummariser(Summariser):
    def summarise(self, text: str, source_file: str, preferences: dict | None = None) -> Summary:
        print(f"[GPTSummariser] Requesting GPT summary for {source_file}...")
        tone = preferences.get("tone", "professional and concise") if preferences else "professional and concise"
        language = preferences.get("language", "English") if preferences else "English"
        system_prompt = f"Summarise this file in a {tone} tone using {language}."
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text}
            ],
            temperature=0.3,
            max_tokens=300
        )
        content = response.choices[0].message.content.strip()
        return Summary(
            source_file=source_file,
            content=content,
            generated_at=datetime.utcnow()
        )

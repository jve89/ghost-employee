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
        email_sender = preferences.get("sender") if preferences else None
        email_subject = preferences.get("subject") if preferences else None
        system_prompt = f"Summarise this file in a {tone} tone using {language}."

        if email_sender or email_subject:
            system_prompt += " The content comes from an email"
            if email_sender:
                system_prompt += f" sent by {email_sender}"
            if email_subject:
                system_prompt += f" with the subject line '{email_subject}'"
            system_prompt += "."

        system_prompt += " Highlight any actions or decisions clearly."
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
            generated_at=datetime.utcnow(),
            sender=email_sender,
            subject=email_subject
        )

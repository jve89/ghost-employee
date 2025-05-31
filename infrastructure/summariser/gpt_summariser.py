import os
from openai import OpenAI
from datetime import datetime
from dotenv import load_dotenv

from app.core.models import Summary
from app.core.interfaces import Summariser

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class GPTSummariser(Summariser):
    def summarise(self, text: str, source_file: str) -> Summary:
        print(f"[GPTSummariser] Requesting GPT summary for {source_file}...")
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Summarise this file in clear, professional language."},
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

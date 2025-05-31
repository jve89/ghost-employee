from datetime import datetime
from app.core.models import Summary
from app.core.interfaces import Summariser

class GPTSummariser(Summariser):
    def summarise(self, text: str, source_file: str) -> Summary:
        # Stub for now — later, add OpenAI integration
        print(f"[GPTSummariser] Summarising file: {source_file}")
        return Summary(
            source_file=source_file,
            content="Stub summary of input text.",
            generated_at=datetime.utcnow()
        )

from datetime import datetime

class MemoryLogger:
    def __init__(self):
        self.logs = []

    def log(self, message: str):
        timestamp = datetime.utcnow().isoformat()
        entry = f"{timestamp} | {message}"
        self.logs.append(entry)
        # Keep log size under control
        if len(self.logs) > 1000:
            self.logs = self.logs[-500:]

    def get_logs(self) -> list[str]:
        return self.logs

logger = MemoryLogger()

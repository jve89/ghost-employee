# infrastructure/logger/export_log.py

from app.core.models import ExportResult

class ExportLogStore:
    def __init__(self):
        self.logs: list[ExportResult] = []

    def add(self, result: ExportResult):
        self.logs.append(result)
        if len(self.logs) > 1000:
            self.logs = self.logs[-500:]

    def get_logs(self) -> list[ExportResult]:
        return self.logs

export_log = ExportLogStore()

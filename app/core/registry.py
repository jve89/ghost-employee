from app.core.interfaces import Exporter
from infrastructure.exporters.log_exporter import LogExporter

def get_exporters(destination: str) -> list[Exporter]:
    if destination == "logs":
        return [LogExporter()]
    else:
        raise ValueError(f"Unknown export destination: {destination}")

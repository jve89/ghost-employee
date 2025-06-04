from app.core.interfaces import Exporter
from infrastructure.exporters.log_exporter import LogExporter
from infrastructure.exporters.file_exporter import FileExporter
from infrastructure.exporters.mailgun_exporter import MailgunExporter

def get_exporters(destination_type: str) -> list[Exporter]:
    """
    Return a list of exporter instances for a given destination type.
    You can configure multiple exporters per type here if needed.
    """
    if destination_type == "logs":
        return [LogExporter()]
    elif destination_type == "file":
        return [FileExporter()]
    elif destination_type == "email":
        return [MailgunExporter()]
    else:
        raise ValueError(f"Unknown export destination: {destination_type}")

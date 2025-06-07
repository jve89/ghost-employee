from infrastructure.exporters.log_exporter import LogExporter
from infrastructure.exporters.file_exporter import FileExporter
from infrastructure.exporters.mailgun_exporter import MailgunExporter

def get_exporters(destination_type: str) -> list:
    """
    Return a list of exporter factories (functions that accept config and return instances).
    """
    if destination_type == "log": 
        return [lambda config: LogExporter(config)]
    elif destination_type == "file":
        return [lambda config: FileExporter(config)]
    elif destination_type == "email":
        return [lambda config: MailgunExporter(config)]
    else:
        raise ValueError(f"Unknown export destination: {destination_type}")

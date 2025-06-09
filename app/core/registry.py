from infrastructure.exporters.log_exporter import LogExporter
from infrastructure.exporters.file_exporter import FileExporter
from infrastructure.exporters.mailgun_exporter import MailgunExporter

def get_exporters(destination_type: str) -> list:
    """
    Return a list of exporter factories (functions that accept config and job_id).
    """
    if destination_type == "log":
        return [lambda config, job_id: LogExporter(config=config, job_id=job_id)]
    elif destination_type == "file":
        return [lambda config, job_id: FileExporter(config=config, job_id=job_id)]
    elif destination_type == "email":
        return [lambda config, job_id: MailgunExporter(config=config, job_id=job_id)]
    else:
        raise ValueError(f"Unknown export destination: {destination_type}")

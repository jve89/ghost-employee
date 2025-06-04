# infrastructure/exporters/file_exporter.py

import os
import json
from datetime import datetime
from app.core.interfaces import Exporter
from app.core.models import Task

class FileExporter(Exporter):
    def __init__(self, config: dict = None):
        self.directory = (config or {}).get("directory", "./exports/sample_job/")
        os.makedirs(self.directory, exist_ok=True)

    def export(self, task: Task) -> None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"ghost_export_{timestamp}.json"
        filepath = os.path.join(self.directory, filename)

        def default_serializer(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            return str(obj)

        with open(filepath, "w") as f:
            json.dump(task.dict(), f, indent=2, default=default_serializer)

        print(f"[FileExporter] Exported task to {filepath}")

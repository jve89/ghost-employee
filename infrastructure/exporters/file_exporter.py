# infrastructure/exporters/file_exporter.py

import os
import json
from datetime import datetime

def export_to_file(data: dict, config: dict):
    directory = config.get("directory", "./exports")
    os.makedirs(directory, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"ghost_export_{timestamp}.json"
    filepath = os.path.join(directory, filename)

    def default_serializer(obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return str(obj)

    with open(filepath, "w") as f:
        json.dump(data, f, indent=2, default=default_serializer)

    print(f"[EXPORT] Written to file: {filepath}")

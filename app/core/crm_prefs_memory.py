import os
import json

class CRMPrefsMemory:
    def __init__(self, job_name: str):
        self.path = f"memory/preferences_{job_name}.json"
        os.makedirs("memory", exist_ok=True)
        if not os.path.exists(self.path):
            with open(self.path, "w") as f:
                json.dump({}, f)

    def get_preferences(self) -> dict:
        with open(self.path, "r") as f:
            return json.load(f)

    def set_preference(self, key: str, value: str):
        prefs = self.get_preferences()
        prefs[key] = value
        with open(self.path, "w") as f:
            json.dump(prefs, f, indent=2)

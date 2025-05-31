from datetime import datetime

class JobStatusStore:
    def __init__(self):
        self.status = {}

    def update(self, job_name: str):
        self.status[job_name] = datetime.utcnow().isoformat()

    def get_all(self):
        return self.status

job_status = JobStatusStore()

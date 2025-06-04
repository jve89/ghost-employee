import time
from config.config_loader import load_job_configs
from infrastructure.file_watchers.folder_watcher import start_watchers
from app.services.job_manager import JobManager
from infrastructure.email.email_watcher import poll_email_inbox

Thread(target=poll_email_inbox, daemon=True).start()

def main():
    configs = load_job_configs()
    manager = JobManager(configs)
    manager.start_scheduled_jobs()

if __name__ == "__main__":
    start_watchers()
    while True:
        time.sleep(1)
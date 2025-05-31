import time
from config.config_loader import load_job_configs
from infrastructure.file_watchers.folder_watcher import start_watchers
from app.services.job_manager import JobManager


def main():
    configs = load_job_configs()
    manager = JobManager(configs)
    manager.run_all_jobs()

if __name__ == "__main__":
    start_watchers()
    while True:
        time.sleep(1)
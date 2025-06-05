from app.services.watch_dir_dispatcher import start_watchers as start_folder_watchers
from infrastructure.email.email_watcher import EmailWatcher
import time

if __name__ == "__main__":
    print("[Runner] Starting Ghost Employee Watchers...")

    # Start watching folders (for new .txt files)
    start_folder_watchers()

    # Start watching inbox (IMAP)
    email_watcher = EmailWatcher()
    email_watcher.start()

    print("[Runner] All watchers started. Press Ctrl+C to stop.")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[Runner] Shutting down watchers...")

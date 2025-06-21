import time
import subprocess
from threading import Thread
from app.services.watch_dir_dispatcher import start_watchers
from infrastructure.email.email_watcher import EmailWatcher

def main():
    print("[Runner] 🚀 Starting Ghost Employee...")

    try:
        # Start FastAPI webhook server in background
        subprocess.Popen([
            "uvicorn",
            "interfaces.api.main:app",
            "--host", "0.0.0.0",
            "--port", "8000"
        ])
        print("[Runner] 🌐 FastAPI webhook server started on port 8000")

        # ✅ Start file watchers in a background thread
        Thread(target=start_watchers, daemon=True).start()
        print("[Runner] 📁 File watchers launched.")

        # ✅ Start EmailWatcher in main thread (safe in Gitpod)
        email_watcher = EmailWatcher()
        email_watcher.start_in_main_thread()

    except KeyboardInterrupt:
        print("\n[Runner] 🛑 Shutdown requested by user.")
    except Exception as e:
        print(f"[Runner] ❌ Unhandled error: {e}")
    finally:
        print("[Runner] 🔚 Exiting cleanly.")

if __name__ == "__main__":
    main()

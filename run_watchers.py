import time
from app.services.watch_dir_dispatcher import start_watchers
from infrastructure.email.email_watcher import EmailWatcher

def main():
    print("[Runner] 🚀 Starting Ghost Employee...")

    try:
        # EmailWatcher runs in main thread (Gitpod-safe)
        email_watcher = EmailWatcher()
        email_watcher.start_in_main_thread()

        # File watchers run in background
        start_watchers()

        print("[Runner] ✅ All watchers running.")
        while True:
            time.sleep(60)

    except KeyboardInterrupt:
        print("\n[Runner] 🛑 Shutdown requested by user.")
    except Exception as e:
        print(f"[Runner] ❌ Unhandled error: {e}")
    finally:
        print("[Runner] 🔚 Exiting cleanly.")

if __name__ == "__main__":
    main()

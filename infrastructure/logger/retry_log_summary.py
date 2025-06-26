from infrastructure.retry.retry_queue_store import retry_queue_store

def get_retry_queue():
    try:
        return retry_queue_store.get_all()
    except Exception as e:
        print(f"[Logger] ❌ Failed to load retry queue: {e}")
        return []

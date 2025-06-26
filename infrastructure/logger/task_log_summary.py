from app.logs.task_log_store import load_task_log

def load_recent_tasks(limit=10):
    try:
        tasks = load_task_log()
        return tasks[:limit]
    except Exception as e:
        print(f"[Logger] ❌ Failed to load task log: {e}")
        return []

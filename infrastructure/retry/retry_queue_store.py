# infrastructure/retry/retry_queue_store.py

import os
import json

RETRY_QUEUE_PATH = "logs/retry_queue.json"

# Ensure file exists
if not os.path.exists(RETRY_QUEUE_PATH):
    with open(RETRY_QUEUE_PATH, "w") as f:
        json.dump([], f)

def get_all():
    try:
        with open(RETRY_QUEUE_PATH, "r") as f:
            return json.load(f)
    except Exception as e:
        print(f"[RetryQueueStore] ❌ Failed to load retry queue: {e}")
        return []

def append(entry: dict):
    try:
        queue = get_all()
        queue.append(entry)
        with open(RETRY_QUEUE_PATH, "w") as f:
            json.dump(queue, f, indent=2)
    except Exception as e:
        print(f"[RetryQueueStore] ❌ Failed to append to retry queue: {e}")

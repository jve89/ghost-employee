from app.logs.input_log import load_input_log

def get_input_log():
    try:
        return load_input_log()
    except Exception as e:
        print(f"[Logger] ❌ Failed to load input log: {e}")
        return []

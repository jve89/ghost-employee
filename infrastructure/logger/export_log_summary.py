from infrastructure.logger.export_log import export_log

def get_latest_export(job_id="compliance_assistant"):
    try:
        logs = export_log.get_logs()
        matching = [log for log in logs if log.get("job_id") == job_id and "summary" in log]
        if not matching:
            return {"summary": "No exports found."}
        latest = sorted(matching, key=lambda x: x["timestamp"], reverse=True)[0]
        return {"summary": latest["summary"]}
    except Exception as e:
        print(f"[Logger] ❌ Failed to load export logs: {e}")
        return {"summary": "⚠️ Error loading export summary"}

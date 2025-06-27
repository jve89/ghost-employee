# app/pipeline/entrypoint.py

def handle_input(source, job_id, text, files):
    print(f"[Pipeline] 🚀 Triggered from {source} for job {job_id}")
    print(f"[Pipeline] 📝 Text: {text[:50]}...")  # show first 50 chars for safety
    print(f"[Pipeline] 📎 Files: {files}")
    # Simulate processing
    print(f"[Pipeline] ✅ Processing complete.")

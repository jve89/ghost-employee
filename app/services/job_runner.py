 # app/services/job_runner.py

def run_job(job, config: dict, override_text: str = None, metadata: dict = None):
    # Inject email metadata into config
    if metadata:
        config["email_context"] = metadata

    # Optional: add debug print
    if metadata:
        print(f"[JobRunner] Running job with email metadata: {metadata}")

    # Pass to job's run() method
    if override_text:
        job.run(config=config, override_text=override_text)
    else:
        job.run(config=config)

import asyncio
import signal
from config.config_loader import load_all_job_configs
from app.jobs.job_registry import get_job_class

running_tasks = []

async def run_job_periodically(config):
    job_class = get_job_class(config.job_id)
    job = job_class()
    while True:
        print(f"[Scheduler] Running job: {config.job_name}")
        job.run(config)
        await asyncio.sleep(config.run_interval_seconds)

async def shutdown():
    print("\n🛑 Shutdown requested. Cancelling tasks...")
    for task in running_tasks:
        task.cancel()
    await asyncio.gather(*running_tasks, return_exceptions=True)
    print("✅ All tasks cancelled. Exiting cleanly.")

async def main():
    job_configs = load_all_job_configs()

    # Schedule all jobs
    for config in job_configs:
        if getattr(config, "active", False):
            task = asyncio.create_task(run_job_periodically(config))
            running_tasks.append(task)

    # Setup signal handlers
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, lambda: asyncio.create_task(shutdown()))

    await asyncio.gather(*running_tasks)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("👋 Interrupted by user")

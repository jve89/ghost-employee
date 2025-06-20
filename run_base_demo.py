# run_base_demo.py

from app.jobs.base_demo_job import BaseDemoJob

if __name__ == "__main__":
    job = BaseDemoJob()
    job.run("watched/demo_inputs/test_demo_job.txt")

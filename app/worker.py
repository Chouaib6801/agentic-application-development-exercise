"""Worker that processes pending jobs."""

import time

from app.db import get_pending_jobs, update_job
from app.agent import process_prompt


def run_worker():
    """Run the worker loop to process pending jobs."""
    while True:
        pending = get_pending_jobs()
        
        if not pending:
            print("No pending jobs. Waiting...")
            time.sleep(2)
            continue
        
        for job_id, job in pending:
            print(f"Processing job {job_id}...")
            update_job(job_id, "running")
            
            try:
                result = process_prompt(job["prompt"])
                update_job(job_id, "completed", result)
                print(f"Job {job_id} completed.")
            except Exception as e:
                update_job(job_id, "failed", str(e))
                print(f"Job {job_id} failed: {e}")


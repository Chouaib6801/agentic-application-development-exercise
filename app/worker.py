"""Worker that processes pending jobs."""

import time
import uuid

from app.db import init_db, claim_next_job, update_job
from app.agent import process_prompt


def run_worker():
    """Run the worker loop to process pending jobs."""
    worker_id = str(uuid.uuid4())[:8]
    
    db_path = init_db()
    print(f"Using DB: {db_path}")
    print(f"Worker {worker_id} started.")
    
    while True:
        job = claim_next_job(worker_id)
        
        if job is None:
            print("No pending jobs. Waiting...")
            time.sleep(2)
            continue
        
        job_id = job["id"]
        payload = job["payload"]
        print(f"Processing job {job_id}...")
        
        try:
            # Extract text from payload for processing
            text = payload.get("text", "")
            result = process_prompt(text)
            
            # Store result (in a real app, write to file and store path)
            result_path = f"outputs/{job_id}.txt"
            _save_result(result_path, result)
            
            update_job(job_id, status="DONE", result_path=result_path)
            print(f"Job {job_id} completed.")
            
        except Exception as e:
            update_job(job_id, status="FAILED", error=str(e))
            print(f"Job {job_id} failed: {e}")


def _save_result(path: str, content: str) -> None:
    """Save result to file."""
    from pathlib import Path
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")

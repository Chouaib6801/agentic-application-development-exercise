"""Worker that processes pending jobs in a continuous loop."""

import signal
import sys
import time
import uuid
from datetime import datetime
from pathlib import Path

from app.db import init_db, claim_next_job, update_job, REPO_ROOT

# Graceful shutdown flag
_shutdown_requested = False


def _log(log_file: Path, message: str) -> None:
    """Append a timestamped message to the log file."""
    timestamp = datetime.utcnow().isoformat()
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] {message}\n")


def process_job(job: dict) -> str:
    """Process a single job and return the result path.
    
    Creates output directory, writes logs, generates report.
    Raises on failure.
    """
    job_id = job["id"]
    payload = job["payload"]
    
    # Create output directory
    output_dir = REPO_ROOT / "outputs" / job_id
    output_dir.mkdir(parents=True, exist_ok=True)
    
    log_file = output_dir / "run.log"
    report_file = output_dir / "report.md"
    
    _log(log_file, "Job started")
    _log(log_file, f"Payload: {payload}")
    
    # Extract input data
    text = payload.get("text", "")
    image = payload.get("image")
    context_dir = payload.get("context_dir")
    
    _log(log_file, "Processing input...")
    
    # Generate report (minimal for now)
    report_lines = [
        f"# Job Report: {job_id}",
        "",
        f"**Created:** {job['created_at']}",
        f"**Processed:** {datetime.utcnow().isoformat()}",
        "",
        "## Input",
        "",
    ]
    
    if text:
        report_lines.append(f"**Text:** {text}")
    if image:
        report_lines.append(f"**Image:** {image}")
    if context_dir:
        report_lines.append(f"**Context Directory:** {context_dir}")
    
    report_lines.extend([
        "",
        "## Result",
        "",
        "Processing completed successfully.",
        "",
        f"*Input text echoed:* {text}" if text else "*No text input provided.*",
    ])
    
    report_content = "\n".join(report_lines)
    report_file.write_text(report_content, encoding="utf-8")
    
    _log(log_file, f"Report written to {report_file}")
    _log(log_file, "Job completed successfully")
    
    return str(report_file)


def run_worker() -> None:
    """Run the worker loop to continuously process pending jobs.
    
    Handles graceful shutdown on Ctrl+C (SIGINT) and SIGTERM.
    """
    global _shutdown_requested
    
    worker_id = str(uuid.uuid4())[:8]
    
    # Setup signal handlers for graceful shutdown
    def handle_shutdown(signum, frame):
        global _shutdown_requested
        print("\nShutdown requested. Finishing current job...")
        _shutdown_requested = True
    
    signal.signal(signal.SIGINT, handle_shutdown)
    signal.signal(signal.SIGTERM, handle_shutdown)
    
    db_path = init_db()
    print(f"Using DB: {db_path}")
    print(f"Worker {worker_id} started. Press Ctrl+C to stop.")
    
    while not _shutdown_requested:
        job = claim_next_job(worker_id)
        
        if job is None:
            print("No pending jobs. Waiting...")
            # Check shutdown flag more frequently during sleep
            for _ in range(4):
                if _shutdown_requested:
                    break
                time.sleep(0.5)
            continue
        
        job_id = job["id"]
        print(f"Processing job {job_id}...")
        
        try:
            result_path = process_job(job)
            update_job(job_id, status="DONE", result_path=result_path)
            print(f"Job {job_id} completed: {result_path}")
            
        except Exception as e:
            error_msg = f"{type(e).__name__}: {e}"
            update_job(job_id, status="FAILED", error=error_msg)
            print(f"Job {job_id} failed: {error_msg}")
    
    print(f"Worker {worker_id} stopped.")
    sys.exit(0)

"""Simple JSON-based database for job storage."""

import json
import uuid
from pathlib import Path
from typing import Optional

DB_FILE = Path("jobs.json")


def _load_db() -> dict:
    """Load the database from disk."""
    if DB_FILE.exists():
        return json.loads(DB_FILE.read_text())
    return {}


def _save_db(data: dict) -> None:
    """Save the database to disk."""
    DB_FILE.write_text(json.dumps(data, indent=2))


def create_job(prompt: str) -> str:
    """Create a new job and return its ID."""
    db = _load_db()
    job_id = str(uuid.uuid4())[:8]
    db[job_id] = {"prompt": prompt, "status": "pending", "result": None}
    _save_db(db)
    return job_id


def get_job(job_id: str) -> Optional[dict]:
    """Get a job by ID."""
    db = _load_db()
    return db.get(job_id)


def update_job(job_id: str, status: str, result: Optional[str] = None) -> None:
    """Update a job's status and result."""
    db = _load_db()
    if job_id in db:
        db[job_id]["status"] = status
        if result is not None:
            db[job_id]["result"] = result
        _save_db(db)


def get_pending_jobs() -> list:
    """Get all pending jobs."""
    db = _load_db()
    return [(jid, job) for jid, job in db.items() if job["status"] == "pending"]


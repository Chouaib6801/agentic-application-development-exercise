"""SQLite-backed job queue for the agentic application."""

import json
import sqlite3
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional, Union

# Deterministic paths relative to repo root
REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DB_PATH = REPO_ROOT / "data" / "jobs.db"

# Cached connection
_connection: Optional[sqlite3.Connection] = None
_current_db_path: Optional[Path] = None


def _resolve_path(db_path: Union[Path, str, None] = None) -> Path:
    """Resolve the database path to an absolute Path."""
    if db_path is None:
        return DEFAULT_DB_PATH
    return Path(db_path).resolve()


def _get_connection(db_path: Union[Path, str, None] = None) -> sqlite3.Connection:
    """Get or create a database connection."""
    global _connection, _current_db_path
    
    resolved = _resolve_path(db_path)
    
    # Reuse connection if same path
    if _connection is not None and _current_db_path == resolved:
        return _connection
    
    # Close existing connection if different path
    if _connection is not None:
        _connection.close()
    
    # Ensure data directory exists
    resolved.parent.mkdir(parents=True, exist_ok=True)
    
    _connection = sqlite3.connect(str(resolved), check_same_thread=False)
    _connection.row_factory = sqlite3.Row
    _current_db_path = resolved
    
    return _connection


def get_db_path() -> Path:
    """Return the resolved default DB path (useful for debugging)."""
    return DEFAULT_DB_PATH


def init_db(db_path: Union[Path, str, None] = None) -> Path:
    """Initialize the database schema. Returns the resolved DB path."""
    resolved = _resolve_path(db_path)
    conn = _get_connection(resolved)
    
    conn.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id TEXT PRIMARY KEY,
            status TEXT NOT NULL DEFAULT 'PENDING',
            payload_json TEXT NOT NULL,
            result_path TEXT,
            error TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)
    # Index for efficient claim queries
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_jobs_status_created 
        ON jobs(status, created_at)
    """)
    conn.commit()
    
    return resolved


def create_job(payload: dict, db_path: Union[Path, str, None] = None) -> str:
    """Create a new job and return its ID."""
    conn = _get_connection(db_path)
    job_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()
    
    conn.execute(
        """
        INSERT INTO jobs (id, status, payload_json, created_at, updated_at)
        VALUES (?, 'PENDING', ?, ?, ?)
        """,
        (job_id, json.dumps(payload), now, now)
    )
    conn.commit()
    return job_id


def get_job(job_id: str, db_path: Union[Path, str, None] = None) -> Optional[dict]:
    """Get a job by ID."""
    conn = _get_connection(db_path)
    cursor = conn.execute(
        "SELECT * FROM jobs WHERE id = ?",
        (job_id,)
    )
    row = cursor.fetchone()
    if row is None:
        return None
    
    return _row_to_dict(row)


def claim_next_job(worker_id: str, db_path: Union[Path, str, None] = None) -> Optional[dict]:
    """Atomically claim the oldest PENDING job and mark it RUNNING.
    
    Uses a transaction to ensure only one worker can claim a job.
    Returns the claimed job or None if no pending jobs exist.
    """
    conn = _get_connection(db_path)
    now = datetime.utcnow().isoformat()
    
    # Use a transaction for atomic claim
    conn.execute("BEGIN IMMEDIATE")
    try:
        # Find oldest pending job
        cursor = conn.execute(
            """
            SELECT id FROM jobs 
            WHERE status = 'PENDING' 
            ORDER BY created_at ASC 
            LIMIT 1
            """
        )
        row = cursor.fetchone()
        
        if row is None:
            conn.execute("ROLLBACK")
            return None
        
        job_id = row["id"]
        
        # Mark as running
        conn.execute(
            """
            UPDATE jobs 
            SET status = 'RUNNING', updated_at = ?
            WHERE id = ? AND status = 'PENDING'
            """,
            (now, job_id)
        )
        conn.commit()
        
        # Return the full job
        return get_job(job_id, db_path)
        
    except Exception:
        conn.execute("ROLLBACK")
        raise


def update_job(job_id: str, db_path: Union[Path, str, None] = None, **fields) -> None:
    """Update a job's fields.
    
    Supported fields: status, result_path, error
    """
    if not fields:
        return
    
    conn = _get_connection(db_path)
    now = datetime.utcnow().isoformat()
    
    # Build dynamic UPDATE statement
    allowed_fields = {"status", "result_path", "error"}
    updates = []
    values = []
    
    for key, value in fields.items():
        if key in allowed_fields:
            updates.append(f"{key} = ?")
            values.append(value)
    
    if not updates:
        return
    
    updates.append("updated_at = ?")
    values.append(now)
    values.append(job_id)
    
    sql = f"UPDATE jobs SET {', '.join(updates)} WHERE id = ?"
    conn.execute(sql, values)
    conn.commit()


def _row_to_dict(row: sqlite3.Row) -> dict:
    """Convert a database row to a dictionary."""
    return {
        "id": row["id"],
        "status": row["status"],
        "payload": json.loads(row["payload_json"]),
        "result_path": row["result_path"],
        "error": row["error"],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }

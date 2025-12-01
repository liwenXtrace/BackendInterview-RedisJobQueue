"""
Redis queue + job state.

You must implement a reliable pattern safe for multi-workers and crashes.

Suggested list-based reliable queue:
- LPUSH jobs:queue <job_id>
- BRPOPLPUSH jobs:queue jobs:processing  (atomic claim)
- worker updates job hash -> processing
- on success/fail: LREM jobs:processing 1 <job_id> (ack)
- reaper scans jobs:processing for stuck jobs -> requeue once
"""

import json
from typing import Optional, Dict, Any, List
from datetime import datetime
from .redis_client import redis
from .config import settings
from .utils import now_utc

JOB_KEY_PREFIX = "job:"  # job:{id}

def job_key(job_id: str) -> str:
    return f"{JOB_KEY_PREFIX}{job_id}"

def serialize_dt(dt: Optional[datetime]) -> str:
    # Redis cannot store None
    return dt.isoformat() if dt else ""

def deserialize_dt(s: Optional[str]) -> Optional[datetime]:
    if not s:
        return None
    return datetime.fromisoformat(s)

async def create_job(job_id: str, payload: Dict[str, Any]) -> None:
    """
    Create job metadata and enqueue.

    Must set:
      status=queued, payload, attempts=0, created_at, updated_at,
      started_at empty, last_error empty
    Then enqueue job_id into settings.queue_key.
    """
    raise NotImplementedError

async def get_job(job_id: str) -> Optional[Dict[str, Any]]:
    """
    Fetch job hash from Redis and deserialize into Python types.
    """
    raise NotImplementedError

async def claim_job(block_s: int) -> Optional[str]:
    """
    Atomically claim next job into processing list.

    Suggested:
      BRPOPLPUSH queue_key -> processing_key
    """
    raise NotImplementedError

async def mark_processing(job_id: str) -> None:
    """
    Set status=processing, increment attempts, set started_at, updated_at.
    """
    raise NotImplementedError

async def mark_done(job_id: str, result: Dict[str, Any]) -> None:
    """
    Set status=done, store result, updated_at, ack from processing list.
    """
    raise NotImplementedError

async def mark_failed(job_id: str, error_msg: str) -> None:
    """
    Set status=failed, store last_error, updated_at, ack from processing list.
    """
    raise NotImplementedError

async def requeue_job(job_id: str) -> None:
    """
    Put back in queue if attempts < max_attempts.
    Reset status=queued and started_at empty, updated_at now.
    """
    raise NotImplementedError

async def scan_and_requeue_stuck_jobs() -> int:
    """
    Scan processing list for jobs stuck longer than processing_timeout_s.
    Requeue once if attempts < max_attempts otherwise fail terminally.

    Returns number of jobs requeued.
    """
    raise NotImplementedError

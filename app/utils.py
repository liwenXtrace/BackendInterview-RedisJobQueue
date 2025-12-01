import uuid
from datetime import datetime, timezone

def new_job_id() -> str:
    return str(uuid.uuid4())

def now_utc() -> datetime:
    return datetime.now(timezone.utc)

from pydantic import BaseModel
from typing import Any, Dict, Optional, Literal
from datetime import datetime

JobStatus = Literal["queued", "processing", "done", "failed"]

class CreateJobRequest(BaseModel):
    payload: Dict[str, Any]

class CreateJobResponse(BaseModel):
    job_id: str

class JobView(BaseModel):
    job_id: str
    status: JobStatus
    result: Optional[Dict[str, Any]] = None
    attempts: int
    created_at: datetime
    updated_at: datetime
    started_at: Optional[datetime] = None
    last_error: Optional[str] = None

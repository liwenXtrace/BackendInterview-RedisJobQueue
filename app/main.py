import os
import asyncio
from fastapi import FastAPI, HTTPException
from .models import CreateJobRequest, CreateJobResponse, JobView
from .utils import new_job_id
from . import queue
from .worker import start_workers
from .redis_client import close_redis

app = FastAPI(title="Redis Job Queue")

@app.on_event("startup")
async def on_startup():
    # In docker interview setup, this is false; workers run separately.
    if os.getenv("START_WORKERS_IN_API", "true").lower() == "true":
        asyncio.create_task(start_workers())

@app.on_event("shutdown")
async def on_shutdown():
    await close_redis()

@app.get("/ping")
async def ping():
    return {"message": "pong"}

@app.post("/jobs", response_model=CreateJobResponse)
async def create_job(req: CreateJobRequest):
    job_id = new_job_id()
    await queue.create_job(job_id, req.payload)
    return CreateJobResponse(job_id=job_id)

@app.get("/jobs/{job_id}", response_model=JobView)
async def get_job(job_id: str):
    job = await queue.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    # TODO: map dict -> JobView
    raise NotImplementedError

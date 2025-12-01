"""
Worker + reaper loops.

Worker:
- claim job_id atomically
- mark processing
- load payload
- process
- mark done/failed (with retry cap)

Reaper:
- periodically scan processing list
- requeue stuck jobs once
"""

import asyncio
from typing import Dict, Any
from .config import settings
from . import queue

async def process_job(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Simulate work. Candidates may adjust.
    """
    await asyncio.sleep(0.3)
    return {"processed": True, "original": payload}

async def worker_loop(worker_id: int = 0):
    while True:
        job_id = await queue.claim_job(block_s=settings.worker_poll_block_s)
        if not job_id:
            continue

        # TODO:
        # 1) fetch job metadata
        # 2) mark_processing(job_id)
        # 3) process payload
        # 4) mark_done / mark_failed / requeue based on attempts
        raise NotImplementedError

async def reaper_loop():
    while True:
        # TODO: call scan_and_requeue_stuck_jobs()
        raise NotImplementedError
        await asyncio.sleep(1.0)

async def start_workers():
    tasks = [
        asyncio.create_task(worker_loop(i))
        for i in range(settings.worker_concurrency)
    ]
    tasks.append(asyncio.create_task(reaper_loop()))
    await asyncio.gather(*tasks)

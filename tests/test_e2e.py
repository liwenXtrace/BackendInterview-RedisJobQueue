import pytest
import pytest_asyncio
from httpx import AsyncClient
import redis.asyncio as Redis
from app.config import settings
from app.queue import job_key
import asyncio


@pytest_asyncio.fixture
async def test_redis_client():
    r = Redis.from_url("redis://localhost:6379/0", decode_responses=True)
    await r.flushdb()
    try:
        yield r
    finally:
        await r.close()

@pytest.mark.asyncio
async def test_job_lifecycle(test_redis_client):
    """
    Expectation:
    - create job
    - poll until done
    """

    async with AsyncClient(base_url="http://localhost:8000") as client:
        r = await client.post("/jobs", json={"payload": {"x": 1}})
        assert r.status_code == 200
        job_id = r.json()["job_id"]

        # TODO: poll /jobs/{id} until done, assert status/result
        raise NotImplementedError


@pytest.mark.asyncio
async def test_requeue_stuck_job(test_redis_client):
    """
    Expectation:
    - create job
    - artificially simulate stuck processing
    - ensure reaper requeues once
    """
    async with AsyncClient(base_url="http://localhost:8000") as client:
        r = await client.post("/jobs", json={"payload": {"slow": True}})
        job_id = r.json()["job_id"]

        # Manually simulate a stuck processing job:
        # Move it into processing list and set started_at far in past.
        await test_redis_client.lpop(settings.queue_key)
        await test_redis_client.lpush(settings.processing_key, job_id)

        # Set processing state with old timestamp and attempts=1
        await test_redis_client.hset(
            job_key(job_id),
            mapping={
                "status": "processing",
                "attempts": "1",
                "started_at": "2000-01-01T00:00:00+00:00",
            },
        )

        # Wait long enough for reaper to run and worker to finish retry
        raise NotImplementedError
        # TODO: implement once queue/worker ready
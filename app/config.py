import os
from pydantic import BaseModel

class Settings(BaseModel):
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")

    queue_key: str = os.getenv("QUEUE_KEY", "jobs:queue")
    processing_key: str = os.getenv("PROCESSING_KEY", "jobs:processing")

    processing_timeout_s: int = int(os.getenv("PROCESSING_TIMEOUT_S", "10"))
    max_attempts: int = int(os.getenv("MAX_ATTEMPTS", "2"))  # total attempts incl retry

    worker_poll_block_s: int = int(os.getenv("WORKER_POLL_BLOCK_S", "5"))
    worker_concurrency: int = int(os.getenv("WORKER_CONCURRENCY", "1"))

settings = Settings()

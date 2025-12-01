# Redis Job Queue Challenge 

This repo is a starter skeleton for an interview exercise.  
Your task is to implement a **reliable Redis-backed job queue** with a FastAPI API service and a separate worker service.

---

## What you need to build

### API
Implement these endpoints:

1. **Create a job**
   - `POST /jobs`
   - Body:
     ```json
     { "payload": { ...any json... } }
     ```
   - Returns:
     ```json
     { "job_id": "<uuid>" }
     ```

2. **Get job status**
   - `GET /jobs/{job_id}`
   - Returns:
     ```json
     {
       "job_id": "<uuid>",
       "status": "queued | processing | done | failed",
       "result": { ... } | null,
       "attempts": <int>
     }
     ```

### Worker
A separate worker process should:
- claim jobs from Redis
- mark jobs `processing`
- simulate work (sleep is fine)
- mark jobs `done` or `failed`
- **ack** jobs out of the processing set/list

### Reliability requirements
Design for multi-instance safety and failures:
- **No job should be lost** if a worker dies mid-processing.
- A job should be processed **at most once successfully**.
- If a worker crashes during processing, the job may be retried, but:
  - **max retries = 1** (so total attempts ≤ 2).
- If a job is stuck in `processing` longer than **T seconds** (default 10s),
  it must be requeued once.

You may use any correct Redis approach, e.g.:
- reliable list queue pattern
- Redis Streams consumer groups
- Lua scripts for atomic transitions
- etc.

---

## How to run locally (interview workflow)

### 1) Start Redis + API + Worker
We run a **real server** and a **separate worker service** using Docker Compose:

```bash
docker-compose up --build
```
This starts:

- redis on localhost:6379

- api on localhost:8000

- worker as a separate service that consumes jobs

### 2) Try the API
Create a job:

```bash
curl -X POST http://localhost:8000/jobs \
  -H "Content-Type: application/json" \
  -d '{"payload":{"x":1}}'
```

Poll status:

```bash
curl http://localhost:8000/jobs/<job_id>
```

You should see status advance:
queued → processing → done (or failed)

### 3) View logs
Tail API logs:

```bash
docker-compose logs -f fastapi-api
```

Tail worker logs:

```bash
docker-compose logs -f job-worker
```


### 4) Testing (Mandatory)
You must provide automated tests that validate the system end-to-end against a running server.

#### What we expect:

At minimum, include two pytest tests:

1. Job lifecycle works:

    - Create a job via `POST /jobs`

    - Poll `GET /jobs/{id}` until terminal

    - Assert:

        - status becomes `"done"`

        - result is present and matches payload

        - attempts is ≥ 1

2. Stuck job is requeued once:

    - Insert a job directly into Redis in a stuck processing state
(so workers can’t race to complete it before it’s stuck)

    - Wait for:

        - reaper to requeue it

        - worker to complete retry

    - Assert:

        - status becomes `"done"` or `"failed"`

        - attempts becomes 2 (forced retry)


# Diagnostics async job queue (arq + Redis) — scaffold

Backward-compatible scaffold to offload long LLM-backed generation to a
background worker, so the HTTP API stays responsive under load. **Nothing here
is wired into the running app yet** — adopt deliberately.

## Why
The deep-diagnostic generation can take seconds–minutes (LLM + PDF). Running it
inside the request handler ties up a uvicorn worker for the whole duration.
A queue lets the API return a `job_id` instantly and a separate worker drain
jobs at a controlled rate.

> Prerequisite already done: the OpenRouter client is now **non-blocking**
> (`asyncio.to_thread`), so even without a queue a single worker can handle many
> concurrent LLM calls. The queue is for *true* long/background jobs and for
> capping LLM concurrency/cost centrally.

## Pieces
- `app/queue/settings.py` — Redis connection from env + `MAX_CONCURRENT_JOBS`.
- `app/queue/tasks.py` — `run_deep_diagnostic` (WIRE to the real pipeline).
- `app/queue/worker.py` — arq `WorkerSettings` (run as its own process).
- `app/routes/jobs.py` — `POST /api/v1/jobs/diagnostic`, `GET /api/v1/jobs/{id}`.

## Activate
1. `requirements.txt` already adds `arq` + `redis`. Rebuild the image.
2. Wire the real generation in `tasks.run_deep_diagnostic`.
3. Include the router in `app/main.py`:
   ```python
   from app.routes.jobs import router as jobs_router
   app.include_router(jobs_router)
   ```
4. Set env on BOTH api and worker: `REDIS_URL=redis://:<password>@redis:6379/0`.
5. Add a worker service to `docker-compose.prod.yml` (same image, different command):
   ```yaml
   avry-diagnostics-worker:
     build: { context: ./services/avry-diagnostics, dockerfile: Dockerfile }
     container_name: avry-diagnostics-worker
     restart: unless-stopped
     networks: [aivory-network]
     environment:
       - REDIS_URL=redis://:${REDIS_PASSWORD}@redis:6379/0
       - DATABASE_URL=${DATABASE_URL}
       - OPENROUTER_API_KEY=${OPENROUTER_API_KEY}
     command: ["arq", "app.queue.worker.WorkerSettings"]
     mem_limit: 512m
     cpus: 1.0
   ```
6. **Frontend**: switch the deep-diagnostic call to POST the async endpoint and
   poll `GET /api/v1/jobs/{id}` until `status == complete`. Keep the old sync
   endpoint until the frontend is migrated.

## Replicate
The same four files + worker service port cleanly to `avry-blueprint`,
`avry-roadmap`, `avry-workflows` (adjust task + ports).

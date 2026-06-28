"""arq worker entrypoint.

Run as a SEPARATE process/container from the API, sharing the same image:
    arq app.queue.worker.WorkerSettings

It connects to the same Redis the API enqueues to and processes jobs in the
background, up to MAX_CONCURRENT_JOBS at a time.
"""
from app.queue.settings import redis_settings, MAX_CONCURRENT_JOBS
from app.queue.tasks import run_deep_diagnostic


class WorkerSettings:
    functions = [run_deep_diagnostic]
    redis_settings = redis_settings()
    max_jobs = MAX_CONCURRENT_JOBS
    job_timeout = 180        # seconds; long enough for a deep LLM generation
    keep_result = 3600       # keep job results in Redis for 1h for polling
    max_tries = 2            # retry once on failure

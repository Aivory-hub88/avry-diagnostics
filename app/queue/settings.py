"""Shared Redis/arq connection settings for the diagnostics job queue.

Reads Redis config from the environment so the same image works for the API
process and the arq worker process. Requires the service to be on the same
docker network as the `redis` container (already wired: aivory-network).
"""
import os
from arq.connections import RedisSettings


def redis_settings() -> RedisSettings:
    # Prefer a full REDIS_URL if provided, else assemble from parts.
    url = os.getenv("REDIS_URL")
    if url:
        return RedisSettings.from_dsn(url)
    return RedisSettings(
        host=os.getenv("REDIS_HOST", "redis"),
        port=int(os.getenv("REDIS_PORT", "6379")),
        password=os.getenv("REDIS_PASSWORD") or None,
        database=int(os.getenv("REDIS_DB", "0")),
    )


# Cap simultaneous LLM jobs the worker will run. Keep this in line with the
# Traefik llm-inflight cap (30) and OpenRouter rate/cost limits.
MAX_CONCURRENT_JOBS = int(os.getenv("QUEUE_MAX_JOBS", "10"))

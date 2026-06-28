"""Async job API (scaffold) — backward-compatible, additive.

Existing sync endpoints are untouched. This adds an async path:
    POST /api/v1/jobs/diagnostic   -> {"job_id": "...", "status": "queued"}
    GET  /api/v1/jobs/{job_id}     -> {"status": "...", "result": {...}|null}

To activate, include this router in app/main.py:
    from app.routes.jobs import router as jobs_router
    app.include_router(jobs_router)
and set REDIS_URL (or REDIS_HOST/PORT/PASSWORD) on both the API and worker, and
run the worker container (see app/queue/QUEUE_SCAFFOLD.md).
"""
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse
from arq import create_pool
from arq.jobs import Job, JobStatus

from app.queue.settings import redis_settings

router = APIRouter(prefix="/api/v1/jobs", tags=["jobs"])


async def _pool():
    # A short-lived pool per request keeps the scaffold simple. For production,
    # create one pool on app startup and reuse it via app.state.
    return await create_pool(redis_settings())


@router.post("/diagnostic")
async def enqueue_diagnostic(request: Request):
    data = await request.json()
    pool = await _pool()
    try:
        job = await pool.enqueue_job("run_deep_diagnostic", data)
        if job is None:
            raise HTTPException(status_code=409, detail="Could not enqueue job")
        return JSONResponse(status_code=202, content={"job_id": job.job_id, "status": "queued"})
    finally:
        await pool.aclose()


@router.get("/{job_id}")
async def get_job(job_id: str):
    pool = await _pool()
    try:
        job = Job(job_id, redis=pool)
        status: JobStatus = await job.status()
        if status == JobStatus.not_found:
            raise HTTPException(status_code=404, detail="Job not found")
        result = None
        if status == JobStatus.complete:
            result = await job.result(timeout=1)
        return {"job_id": job_id, "status": status.value, "result": result}
    finally:
        await pool.aclose()

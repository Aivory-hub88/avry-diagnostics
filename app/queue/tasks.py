"""arq task functions for long-running diagnostic generation.

The HTTP API enqueues one of these and returns a job_id immediately; the arq
worker process runs it in the background. This decouples "concurrent users"
from "concurrent LLM calls" — the API stays responsive under spikes while the
worker drains jobs at a controlled rate (settings.MAX_CONCURRENT_JOBS).

NOTE (scaffold): `run_deep_diagnostic` currently calls a placeholder. Wire it
to the real generation path (e.g. app.services.snapshot_scoring_service /
app.agents.diagnosis_agent) when adopting. Keep the task idempotent and make it
re-entrant on retry.
"""
import logging
from typing import Any, Dict

logger = logging.getLogger("diagnostics.queue")


async def run_deep_diagnostic(ctx: Dict[str, Any], payload: Dict[str, Any]) -> Dict[str, Any]:
    """Background job: run the full LLM-backed diagnostic for `payload`.

    Args:
        ctx: arq job context (contains redis, job_id, job_try, etc.)
        payload: {"answers": {...}, "company_name": str, "user_id": str}

    Returns:
        The generated diagnostic result dict (stored by arq as the job result).
    """
    job_id = ctx.get("job_id")
    logger.info("Starting deep diagnostic job %s (try %s)", job_id, ctx.get("job_try"))

    # --- WIRE ME: replace this block with the real generation pipeline ---
    # from app.services.snapshot_scoring_service import SnapshotScoringService
    # from app.agents.diagnosis_agent import DiagnosisAgent
    # result = await DiagnosisAgent().run(payload)   # uses the now non-blocking OpenRouter client
    result = {
        "status": "completed",
        "note": "scaffold placeholder — wire run_deep_diagnostic to the real pipeline",
        "company_name": payload.get("company_name"),
        "user_id": payload.get("user_id"),
    }
    # ---------------------------------------------------------------------

    logger.info("Finished deep diagnostic job %s", job_id)
    return result

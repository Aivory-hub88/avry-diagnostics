"""
Diagnostic API Routes
Handles AI readiness diagnostic submission and retrieval.

Scoring is delegated to deterministic engines — never hardcoded:
- Free (12-question, 0-4 weighted)   -> DiagnosticCalculator.calculate_complete_result
- Paid/Deep (30-question snapshot)   -> calculate_snapshot_score
"""

from fastapi import APIRouter, HTTPException, status, Request, Depends
from fastapi.responses import JSONResponse
from uuid import uuid4
import secrets
from datetime import datetime
from typing import Optional, Any, Dict, List

from app.database.db_service import DatabaseService
from app.models.diagnostic import DiagnosticRecord
from app.auth import require_admin, require_auth
from app.services.diagnostic_calculator import DiagnosticCalculator
from app.services.snapshot_scoring_service import calculate_snapshot_score

router = APIRouter(prefix="/api/v1/diagnostic", tags=["diagnostic"])

# Initialize database service
db_service = DatabaseService()


def _normalize_free_answers(raw: Any) -> Dict[str, int]:
    """Coerce the free-diagnostic answers payload into {question_id: int}.

    Accepts either a dict ({q_id: value}) or a list of
    {question_id, answer|selected_option|value} objects.
    """
    answers: Dict[str, int] = {}
    if isinstance(raw, dict):
        items = raw.items()
    elif isinstance(raw, list):
        items = []
        for entry in raw:
            if not isinstance(entry, dict):
                continue
            qid = entry.get("question_id") or entry.get("id")
            val = entry.get("answer", entry.get("selected_option", entry.get("value")))
            if qid is not None:
                items.append((qid, val))
    else:
        return answers

    for qid, val in items:
        try:
            answers[str(qid)] = int(val)
        except (TypeError, ValueError):
            # Leave invalid values out; validate_answers will flag if required.
            continue
    return answers


def _normalize_snapshot_answers(raw: Any) -> List[Dict[str, Any]]:
    """Coerce snapshot answers into the [{question_id, selected_option}] shape
    expected by calculate_snapshot_score. Accepts a dict or a list."""
    result: List[Dict[str, Any]] = []
    if isinstance(raw, dict):
        for qid, val in raw.items():
            result.append({"question_id": str(qid), "selected_option": val})
    elif isinstance(raw, list):
        for entry in raw:
            if isinstance(entry, dict) and ("question_id" in entry or "id" in entry):
                result.append({
                    "question_id": str(entry.get("question_id") or entry.get("id")),
                    "selected_option": entry.get("selected_option", entry.get("answer", entry.get("value", 0))),
                })
    return result


@router.post("/free")
async def submit_free_diagnostic(request: Request):
    """Submit a free diagnostic and get deterministically-scored results."""
    try:
        data = await request.json()
        answers = _normalize_free_answers(data.get("answers", {}))
        company_name = data.get("company_name")
        user_id = data.get("user_id")
        user_email = data.get("user_email")
        industry = data.get("industry")

        if not answers:
            raise HTTPException(status_code=400, detail="answers is required and must be non-empty")

        # Deterministic scoring — raises ValueError on invalid/missing answers.
        result = DiagnosticCalculator.calculate_complete_result(answers)

        diagnostic_id = str(uuid4())
        now_iso = datetime.utcnow().isoformat()

        await db_service.store_diagnostic(
            diagnostic_id=diagnostic_id,
            user_id=user_id,
            user_email=user_email,
            company_name=company_name,
            industry=industry,
            answers=[{"question_id": k, "selected_option": v} for k, v in answers.items()],
            score=result["score"],
            category=result["category"],
        )

        return JSONResponse(
            status_code=200,
            content={
                "diagnostic_id": diagnostic_id,
                "user_id": user_id,
                "company_name": company_name,
                "type": "free",
                "score": result["score"],
                "category": result["category"],
                "category_explanation": result["category_explanation"],
                "insights": result["insights"],
                "recommendations": result["recommendations"],
                "timestamp": now_iso,
            },
        )

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"Error submitting free diagnostic: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/paid")
async def submit_paid_diagnostic(request: Request):
    """Submit a paid/deep diagnostic and get weighted, objective-based results."""
    try:
        data = await request.json()
        snapshot_answers = _normalize_snapshot_answers(data.get("answers", {}))
        company_name = data.get("company_name")
        user_id = data.get("user_id")
        user_email = data.get("user_email")
        industry = data.get("industry")

        if not snapshot_answers:
            raise HTTPException(status_code=400, detail="answers is required and must be non-empty")

        # Deterministic weighted snapshot scoring.
        result = calculate_snapshot_score(snapshot_answers)

        score = result["readiness_score"]
        category = result["readiness_level"]

        diagnostic_id = str(uuid4())
        now_iso = datetime.utcnow().isoformat()

        await db_service.store_diagnostic(
            diagnostic_id=diagnostic_id,
            user_id=user_id,
            user_email=user_email,
            company_name=company_name,
            industry=industry,
            answers=snapshot_answers,
            score=score,
            category=category,
        )

        return JSONResponse(
            status_code=200,
            content={
                "diagnostic_id": diagnostic_id,
                "user_id": user_id,
                "company_name": company_name,
                "type": "paid",
                "premium": True,
                "score": score,
                "readiness_level": result["readiness_level"],
                "category_scores": result["category_scores"],
                "weights_used": result["weights_used"],
                "strength_category": result["strength_category"],
                "strength_index": result["strength_index"],
                "bottleneck_category": result["bottleneck_category"],
                "bottleneck_index": result["bottleneck_index"],
                "top_recommendations": result["top_recommendations"],
                "priority_score": result["priority_score"],
                "deployment_phase_suggestion": result["deployment_phase_suggestion"],
                "primary_objective": result["primary_objective"],
                "timestamp": now_iso,
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error submitting paid diagnostic: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/results/{share_token}")
async def get_diagnostic_result(share_token: str):
    """Get a diagnostic result by share token (public view, no sensitive data)."""
    try:
        all_records = db_service.load_all_json("diagnostics")
        match = next((r for r in all_records if r.get("share_token") == share_token), None)
        if not match:
            raise HTTPException(status_code=404, detail="Diagnostic not found")

        return JSONResponse(
            status_code=200,
            content={
                "diagnostic_id": match.get("diagnostic_id"),
                "score": match.get("score"),
                "category": match.get("category"),
                "company_name": match.get("company_name"),
                "type": match.get("type"),
                "timestamp": match.get("created_at"),
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error retrieving diagnostic by share token: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/history")
async def get_diagnostic_history(_auth: dict = Depends(require_auth)):
    """Get the authenticated user's diagnostic history.

    Declared BEFORE the dynamic /{diagnostic_id} route so it is not
    captured as a diagnostic id.
    """
    try:
        user_id = _auth.get("user_id") or _auth.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Unauthenticated")

        diagnostics = await db_service.list_diagnostics_by_user(user_id)
        return JSONResponse(status_code=200, content=diagnostics)

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error retrieving diagnostic history: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{diagnostic_id}")
async def get_diagnostic(diagnostic_id: str):
    """Get a diagnostic result by ID. Must stay LAST among GET routes so the
    dynamic path does not shadow /history or /results/{share_token}."""
    try:
        record = await db_service.get_diagnostic(diagnostic_id)
        if not record:
            raise HTTPException(status_code=404, detail="Diagnostic not found")

        return JSONResponse(status_code=200, content=record)

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error retrieving diagnostic: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("")
async def list_diagnostics(_admin: dict = Depends(require_admin)):
    """List all diagnostics - admin only."""
    try:
        diagnostics = db_service.load_all_json("diagnostics")
        diagnostics.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "diagnostics": diagnostics,
                "total": len(diagnostics),
                "timestamp": datetime.utcnow().isoformat(),
            },
        )

    except Exception as e:
        print(f"Error listing diagnostics: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

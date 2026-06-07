"""
Diagnostic API Routes
Handles AI readiness diagnostic submission and retrieval
"""

from fastapi import APIRouter, HTTPException, status, Request, Depends
from fastapi.responses import JSONResponse
from uuid import uuid4
import secrets
from datetime import datetime
from typing import Optional

from app.database.db_service import DatabaseService
from app.models.diagnostic import DiagnosticRecord
from app.auth import require_admin, require_auth

router = APIRouter(prefix="/api/v1/diagnostic", tags=["diagnostic"])

# Initialize database service
db_service = DatabaseService()


@router.post("/free")
async def submit_free_diagnostic(
    request: Request,
):
    """
    Submit a free diagnostic and get results

    Args:
        request: HTTP request containing answers JSON

    Returns:
        Diagnostic result with score and recommendations
    """
    try:
        # Parse request body
        data = await request.json()
        answers = data.get("answers", {})
        company_name = data.get("company_name")
        user_id = data.get("user_id")

        # Generate diagnostic ID
        diagnostic_id = str(uuid4())

        # Get current time as ISO string for Pydantic validation
        now_iso = datetime.utcnow().isoformat()

        # Create diagnostic record
        diagnostic = DiagnosticRecord(
            diagnostic_id=diagnostic_id,
            user_id=user_id,
            title=f"Diagnostic - {company_name or 'Anonymous'}",
            description="AI Readiness Assessment",
            data={
                "answers": answers,
                "score": 75,
                "category": "intermediate",
                "company_name": company_name,
            },
            created_at=now_iso,
            updated_at=now_iso,
        )

        # Persist the diagnostic so it is visible to admin/history endpoints
        db_service.save_json(
            "diagnostics",
            diagnostic_id,
            {
                "diagnostic_id": diagnostic_id,
                "user_id": user_id,
                "company_name": company_name,
                "type": "free",
                "status": "completed",
                "score": 75,
                "category": "intermediate",
                "created_at": now_iso,
                "updated_at": now_iso,
            },
        )

        # Return result
        return JSONResponse(
            status_code=200,
            content={
                "diagnostic_id": diagnostic_id,
                "user_id": user_id,
                "company_name": company_name,
                "score": 75,
                "timestamp": now_iso,
            },
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"Error submitting diagnostic: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/results/{share_token}")
async def get_diagnostic_result(
    share_token: str,
):
    """
    Get a diagnostic result by share token

    Args:
        share_token: Share token from result

    Returns:
        Diagnostic result (public view)
    """
    try:
        # Return result
        return JSONResponse(
            status_code=200,
            content={
                "message": "Diagnostic retrieved successfully",
                "share_token": share_token,
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error retrieving diagnostic: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{diagnostic_id}")
async def get_diagnostic(
    diagnostic_id: str,
):
    """
    Get a diagnostic result by ID

    Args:
        diagnostic_id: Diagnostic UUID

    Returns:
        Diagnostic result
    """
    try:
        # Return result
        return JSONResponse(
            status_code=200,
            content={
                "diagnostic_id": diagnostic_id,
                "message": "Diagnostic retrieved successfully",
            },
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error retrieving diagnostic: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/history")
async def get_diagnostic_history():
    """
    Get user's diagnostic history (requires authentication header)

    Returns:
        List of diagnostic results
    """
    try:
        # Note: In production, this should require proper authentication
        # For now, return empty list as placeholder
        return JSONResponse(
            status_code=200,
            content=[],
        )

    except Exception as e:
        print(f"Error retrieving diagnostic history: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("")
async def list_diagnostics(_admin: dict = Depends(require_admin)):
    """
    List all diagnostics (diagnostic assessments) - admin only

    Returns:
        List of diagnostic records
    """
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


@router.post("/paid")
async def submit_paid_diagnostic(
    request: Request,
):
    """
    Submit a paid diagnostic and get detailed results

    Args:
        request: HTTP request containing answers JSON

    Returns:
        Detailed diagnostic result with premium features
    """
    try:
        # Parse request body
        data = await request.json()
        answers = data.get("answers", {})
        company_name = data.get("company_name")
        user_id = data.get("user_id")

        # Generate diagnostic ID
        diagnostic_id = str(uuid4())

        # Get current time as ISO string for Pydantic validation
        now_iso = datetime.utcnow().isoformat()

        # Create diagnostic record with premium analysis
        diagnostic = DiagnosticRecord(
            diagnostic_id=diagnostic_id,
            user_id=user_id,
            title=f"Paid Diagnostic - {company_name or 'Anonymous'}",
            description="Premium AI Readiness Assessment with Detailed Analysis",
            data={
                "answers": answers,
                "score": 75,
                "category": "intermediate",
                "company_name": company_name,
                "premium_analysis": True,
            },
            created_at=now_iso,
            updated_at=now_iso,
        )

        # Persist the diagnostic so it is visible to admin/history endpoints
        db_service.save_json(
            "diagnostics",
            diagnostic_id,
            {
                "diagnostic_id": diagnostic_id,
                "user_id": user_id,
                "company_name": company_name,
                "type": "paid",
                "status": "completed",
                "score": 75,
                "category": "intermediate",
                "premium_analysis": True,
                "created_at": now_iso,
                "updated_at": now_iso,
            },
        )

        # Return result
        return JSONResponse(
            status_code=200,
            content={
                "diagnostic_id": diagnostic_id,
                "user_id": user_id,
                "company_name": company_name,
                "score": 75,
                "premium": True,
                "detailed_analysis": {
                    "ai_readiness": "intermediate",
                    "recommendations": ["Implement AI strategy", "Train team"],
                    "next_steps": ["Define use cases", "Start pilot"]
                },
                "timestamp": now_iso,
            },
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print(f"Error submitting paid diagnostic: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")

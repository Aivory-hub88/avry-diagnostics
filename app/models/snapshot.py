"""
Snapshot data models for persistence and API.
"""

from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Dict, Any
from datetime import datetime


class SnapshotAnswer(BaseModel):
    """Single snapshot question answer."""
    question_id: str = Field(description="Question identifier")
    selected_option: int = Field(ge=0, le=4, description="Selected option index (0-4)")


class SnapshotSubmission(BaseModel):
    """Request to submit snapshot diagnostic."""
    diagnostic_id: Optional[str] = Field(default=None, description="Source diagnostic ID")
    user_id: Optional[str] = Field(default=None, description="User identifier")
    user_email: Optional[EmailStr] = Field(default=None, description="User email")
    company_name: Optional[str] = Field(default=None, description="Company name")
    industry: Optional[str] = Field(default=None, description="Industry sector")
    snapshot_answers: List[SnapshotAnswer] = Field(description="Snapshot answers (30 questions)")
    language: str = Field(default="en", description="Language code")


class SnapshotResult(BaseModel):
    """Result of snapshot assessment."""
    snapshot_id: str = Field(description="Unique snapshot identifier")
    diagnostic_id: Optional[str] = Field(description="Source diagnostic ID")
    user_id: Optional[str] = Field(description="User identifier")
    user_email: Optional[str] = Field(description="User email")
    company_name: Optional[str] = Field(description="Company name")
    industry: Optional[str] = Field(description="Industry sector")
    readiness_score: int = Field(ge=0, le=100, description="Readiness score")
    readiness_level: str = Field(description="Readiness level")
    strength_index: int = Field(description="Strength index")
    bottleneck_index: int = Field(description="Bottleneck index")
    top_recommendations: List[str] = Field(description="Top system recommendations")
    priority_score: int = Field(description="Priority score")
    deployment_phase_suggestion: str = Field(description="Deployment phase")
    category_scores: Dict[str, float] = Field(description="Category scores")
    strength_category: str = Field(description="Strongest category")
    bottleneck_category: str = Field(description="Weakest category")
    primary_objective: str = Field(description="Primary business objective")
    weights_used: Dict[str, float] = Field(description="Weights applied")
    pain_points: List[str] = Field(default_factory=list, description="Extracted pain points")
    workflows: List[str] = Field(default_factory=list, description="Extracted workflows")
    key_processes: List[str] = Field(default_factory=list, description="Key processes")
    automation_level: str = Field(default="unknown", description="Current automation level")
    data_quality_score: int = Field(default=0, description="Data quality score")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Creation timestamp")


class SnapshotRecord(BaseModel):
    """Database record for snapshot."""
    snapshot_id: str
    diagnostic_id: Optional[str]
    user_id: Optional[str]
    user_email: Optional[str]
    company_name: Optional[str]
    industry: Optional[str]
    answers: List[Dict[str, Any]]  # JSON serialized
    readiness_score: int
    category_scores: Dict[str, float]
    primary_objective: str
    top_recommendations: List[str]
    pain_points: List[str]
    workflows: List[str]
    key_processes: List[str]
    automation_level: str
    data_quality_score: int
    created_at: datetime

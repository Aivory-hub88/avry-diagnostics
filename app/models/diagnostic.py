"""
Diagnostic Model - Pydantic model for storing AI readiness diagnostic results
"""

from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
import uuid


class DiagnosticRecord(BaseModel):
    """
    Pydantic model for storing AI readiness diagnostic results
    """
    id: str = ""
    user_id: Optional[str] = None
    answers: Dict[str, Any] = {}
    score: int = 0
    category: str = ""
    category_explanation: str = ""
    insights: List[str] = []
    recommendations: List[str] = []
    badge_svg: Optional[str] = None
    company_name: Optional[str] = None
    share_token: Optional[str] = None
    is_public: bool = False
    view_count: int = 0
    last_viewed: Optional[str] = None
    created_at: str = ""
    updated_at: str = ""
    
    class Config:
        """Pydantic config"""
        from_attributes = True
    
    def to_dict(self, include_answers: bool = False):
        """Convert diagnostic to dictionary"""
        result = {
            "diagnostic_id": self.id,
            "user_id": self.user_id,
            "score": self.score,
            "category": self.category,
            "category_explanation": self.category_explanation,
            "insights": self.insights or [],
            "recommendations": self.recommendations or [],
            "badge_svg": self.badge_svg,
            "timestamp": self.created_at,
        }
        
        if include_answers:
            result["answers"] = self.answers
        
        return result
    
    def to_share_dict(self):
        """Convert to dictionary for sharing (no sensitive data)"""
        return {
            "diagnostic_id": self.id,
            "score": self.score,
            "category": self.category,
            "category_explanation": self.category_explanation,
            "insights": self.insights or [],
            "recommendations": self.recommendations or [],
            "badge_svg": self.badge_svg,
            "timestamp": self.created_at,
            "view_count": self.view_count,
        }

"""
Data extraction service for snapshot diagnostics.

Extracts structured data from snapshot answers to populate database fields.
"""

import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


class DataExtractionService:
    """
    Extract structured data from snapshot diagnostic answers.
    
    Converts raw answer data into structured fields:
    - pain_points: List of identified pain points
    - workflows: List of workflow descriptions
    - key_processes: List of key business processes
    - automation_level: Current automation maturity
    - data_quality_score: Data readiness score
    """
    
    def extract_pain_points(self, answers: List[Dict[str, Any]]) -> List[str]:
        """
        Extract pain points from snapshot answers.
        
        Looks for answers indicating challenges, bottlenecks, or inefficiencies.
        """
        pain_points = []
        
        for answer in answers:
            question_id = answer.get("question_id", "")
            selected = answer.get("selected_option", 0)
            
            # Map question patterns to pain points
            if "bottleneck" in question_id.lower():
                if selected >= 2:
                    pain_points.append("Workflow bottlenecks identified")
            
            if "manual" in question_id.lower():
                if selected >= 2:
                    pain_points.append("High manual workload")
            
            if "data_quality" in question_id.lower():
                if selected <= 1:
                    pain_points.append("Data quality issues")
            
            if "integration" in question_id.lower():
                if selected <= 1:
                    pain_points.append("System integration challenges")
        
        # Default if none found
        if not pain_points:
            pain_points = ["Process optimization opportunities identified"]
        
        return pain_points
    
    def extract_workflows(self, answers: List[Dict[str, Any]]) -> List[str]:
        """
        Extract workflow descriptions from snapshot answers.
        
        Identifies documented and undocumented workflows.
        """
        workflows = []
        
        for answer in answers:
            question_id = answer.get("question_id", "")
            selected = answer.get("selected_option", 0)
            
            # Map question patterns to workflows
            if "workflow" in question_id.lower():
                if selected >= 2:
                    workflows.append("Documented workflow processes")
                elif selected == 1:
                    workflows.append("Partially documented workflows")
                else:
                    workflows.append("Undocumented workflows")
            
            if "approval" in question_id.lower():
                if selected >= 1:
                    workflows.append("Approval workflows")
            
            if "routing" in question_id.lower():
                if selected >= 1:
                    workflows.append("Routing workflows")
        
        # Default if none found
        if not workflows:
            workflows = ["Core business workflows"]
        
        return workflows
    
    def extract_key_processes(
        self,
        answers: List[Dict[str, Any]],
        primary_objective: str
    ) -> List[str]:
        """
        Extract key business processes based on primary objective.
        
        Tailors process identification to business objective.
        """
        processes = []
        
        # Map objective to typical processes
        objective_map = {
            "cost_reduction": ["Cost analysis", "Resource optimization", "Efficiency tracking"],
            "revenue_growth": ["Sales pipeline", "Customer acquisition", "Revenue tracking"],
            "customer_experience": ["Customer support", "Feedback collection", "Service delivery"],
            "operational_efficiency": ["Process automation", "Workflow optimization", "Performance monitoring"],
            "exploratory": ["Business operations", "Core workflows", "Data management"]
        }
        
        processes = objective_map.get(primary_objective, objective_map["exploratory"])
        
        return processes
    
    def determine_automation_level(self, answers: List[Dict[str, Any]]) -> str:
        """
        Determine current automation maturity level.
        
        Returns: "None", "Partial", "Moderate", "Advanced"
        """
        automation_score = 0
        automation_questions = 0
        
        for answer in answers:
            question_id = answer.get("question_id", "")
            selected = answer.get("selected_option", 0)
            
            # Count automation-related questions
            if any(keyword in question_id.lower() for keyword in ["automation", "automated", "manual"]):
                automation_questions += 1
                automation_score += selected
        
        if automation_questions == 0:
            return "Partial"
        
        # Calculate average automation level
        avg_score = automation_score / automation_questions
        
        if avg_score >= 3:
            return "Advanced"
        elif avg_score >= 2:
            return "Moderate"
        elif avg_score >= 1:
            return "Partial"
        else:
            return "None"
    
    def calculate_data_quality_score(self, answers: List[Dict[str, Any]]) -> int:
        """
        Calculate data quality/readiness score (0-100).
        
        Based on data-related questions in snapshot.
        """
        data_score = 0
        data_questions = 0
        
        for answer in answers:
            question_id = answer.get("question_id", "")
            selected = answer.get("selected_option", 0)
            
            # Count data-related questions
            if any(keyword in question_id.lower() for keyword in ["data", "information", "documentation"]):
                data_questions += 1
                # Normalize to 0-100 scale (assuming 0-4 option range)
                data_score += (selected / 4) * 100
        
        if data_questions == 0:
            return 70  # Default moderate score
        
        # Calculate average
        avg_score = int(data_score / data_questions)
        
        return min(100, max(0, avg_score))

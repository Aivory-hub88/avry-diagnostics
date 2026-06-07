"""
AIVORY INTELLIGENCE ENGINE V2
Snapshot Scoring Service with Weighted Objective-Based Scoring

Scoring Logic:
- Only Q6-Q30 contribute to score (25 questions × 4 = 100 max)
- Questions grouped into 4 categories
- Each category normalized to 0-100
- Weighted based on primary objective
- Final score = weighted sum of category scores
"""

from typing import Dict, List, Tuple
import logging

logger = logging.getLogger(__name__)

# Question ID to category mapping
CATEGORY_MAPPING = {
    # Workflow Maturity (Q6-Q13)
    "workflows_documented": "workflow",
    "manual_tasks_percentage": "workflow",
    "sop_standardization": "workflow",
    "bottlenecks_frequency": "workflow",
    "escalation_clarity": "workflow",
    "cross_team_visibility": "workflow",
    "cycle_time_tracking": "workflow",
    "output_quality_measurement": "workflow",
    
    # Data Infrastructure (Q14-Q20)
    "data_centralized": "data",
    "crm_usage_maturity": "data",
    "api_accessibility": "data",
    "dashboard_maturity": "data",
    "data_accuracy_confidence": "data",
    "data_ownership_clarity": "data",
    "historical_data_volume": "data",
    
    # Automation Exposure (Q21-Q25)
    "existing_automation_tools": "automation",
    "tool_integrations_maturity": "automation",
    "manual_repetitive_tasks": "automation",
    "ticket_lead_volume": "automation",
    "process_duplication": "automation",
    
    # Organizational Readiness (Q26-Q30)
    "leadership_ai_support": "organization",
    "ai_literacy_level": "organization",
    "budget_allocated": "organization",
    "change_resistance": "organization",
    "dedicated_system_owner": "organization"
}

# Questions that need reverse scoring (higher value = lower maturity)
REVERSE_SCORE_QUESTIONS = [
    "manual_tasks_percentage",
    "bottlenecks_frequency",
    "manual_repetitive_tasks",
    "process_duplication",
    "change_resistance"
]

# Default weights (25% each)
DEFAULT_WEIGHTS = {
    "workflow": 0.25,
    "data": 0.25,
    "automation": 0.25,
    "organization": 0.25
}

# Objective-based weight overrides
OBJECTIVE_WEIGHTS = {
    "increase_revenue": {
        "workflow": 0.20,
        "data": 0.30,
        "automation": 0.30,
        "organization": 0.20
    },
    "improve_efficiency": {
        "workflow": 0.35,
        "automation": 0.30,
        "data": 0.20,
        "organization": 0.15
    },
    "improve_response_time": {
        "automation": 0.35,
        "workflow": 0.30,
        "data": 0.20,
        "organization": 0.15
    },
    "improve_decision_speed": {
        "data": 0.40,
        "workflow": 0.25,
        "automation": 0.20,
        "organization": 0.15
    },
    "scale_without_hiring": {
        "workflow": 0.30,
        "automation": 0.35,
        "organization": 0.20,
        "data": 0.15
    }
}

# Objective to system recommendations mapping
OBJECTIVE_SYSTEM_MAPPING = {
    "increase_revenue": [
        "lead_scoring_agent",
        "sales_qualification_agent",
        "conversion_intelligence_dashboard",
        "revenue_forecast_agent"
    ],
    "improve_efficiency": [
        "workflow_automation_engine",
        "task_routing_agent",
        "internal_copilot",
        "process_compression_layer"
    ],
    "improve_response_time": [
        "ai_ticket_triage",
        "smart_auto_reply_agent",
        "escalation_router",
        "sla_monitor_agent"
    ],
    "improve_decision_speed": [
        "executive_summary_agent",
        "weekly_kpi_digest",
        "anomaly_detection_agent",
        "strategic_signal_dashboard"
    ],
    "scale_without_hiring": [
        "internal_ai_copilot",
        "knowledge_base_agent",
        "multi_workflow_orchestrator",
        "ai_hr_assistant"
    ],
    "reduce_cost": [
        "process_compression_layer",
        "workflow_automation_engine",
        "resource_optimization_agent",
        "cost_analysis_dashboard"
    ],
    "improve_data_visibility": [
        "executive_summary_agent",
        "strategic_signal_dashboard",
        "anomaly_detection_agent",
        "real_time_kpi_monitor"
    ],
    "exploratory": [
        "internal_copilot",
        "workflow_automation_engine",
        "executive_summary_agent",
        "task_routing_agent"
    ]
}


def calculate_snapshot_score(answers: List[Dict]) -> Dict:
    """
    Calculate weighted readiness score from 30-question snapshot diagnostic
    
    Args:
        answers: List of {question_id, selected_option} dicts
        
    Returns:
        Dict with readiness_score, category_scores, weights_used, etc.
    """
    # Extract primary objective (Q1)
    primary_objective = None
    for answer in answers:
        if answer.get("question_id") == "primary_objective":
            # Map option index to enum value
            objective_map = [
                "increase_revenue", "improve_efficiency", "reduce_cost",
                "improve_response_time", "scale_without_hiring",
                "improve_decision_speed", "improve_data_visibility", "exploratory"
            ]
            idx = answer.get("selected_option", 0)
            if 0 <= idx < len(objective_map):
                primary_objective = objective_map[idx]
            break
    
    logger.info(f"Primary objective detected: {primary_objective}")
    
    # Get weights based on objective
    weights = OBJECTIVE_WEIGHTS.get(primary_objective, DEFAULT_WEIGHTS)
    logger.info(f"Using weights: {weights}")
    
    # Group answers by category
    category_scores = {
        "workflow": [],
        "data": [],
        "automation": [],
        "organization": []
    }
    
    # Process scoring questions (Q6-Q30)
    for answer in answers:
        question_id = answer.get("question_id")
        selected_option = answer.get("selected_option")
        
        # Skip non-scoring questions (Q1-Q5)
        if question_id not in CATEGORY_MAPPING:
            continue
        
        # Get category
        category = CATEGORY_MAPPING[question_id]
        
        # Apply reverse scoring if needed
        if question_id in REVERSE_SCORE_QUESTIONS:
            score = 4 - selected_option  # Reverse: 0→4, 1→3, 2→2, 3→1, 4→0
        else:
            score = selected_option
        
        category_scores[category].append(score)
    
    # Calculate category averages and normalize to 0-100
    normalized_scores = {}
    for category, scores in category_scores.items():
        if scores:
            avg_score = sum(scores) / len(scores)  # 0-4 scale
            normalized = (avg_score / 4.0) * 100  # Convert to 0-100
            normalized_scores[category] = round(normalized, 2)
        else:
            normalized_scores[category] = 0
    
    logger.info(f"Normalized category scores: {normalized_scores}")
    
    # Calculate weighted final score
    weighted_score = (
        normalized_scores["workflow"] * weights["workflow"] +
        normalized_scores["data"] * weights["data"] +
        normalized_scores["automation"] * weights["automation"] +
        normalized_scores["organization"] * weights["organization"]
    )
    
    final_score = round(weighted_score)
    
    # Determine readiness level
    if final_score >= 75:
        readiness_level = "High"
    elif final_score >= 50:
        readiness_level = "Medium"
    else:
        readiness_level = "Low"
    
    # Calculate strength and bottleneck indices
    strength_category = max(normalized_scores, key=normalized_scores.get)
    bottleneck_category = min(normalized_scores, key=normalized_scores.get)
    
    strength_index = normalized_scores[strength_category]
    bottleneck_index = normalized_scores[bottleneck_category]
    
    # Get top recommendations based on objective
    top_recommendations = OBJECTIVE_SYSTEM_MAPPING.get(
        primary_objective,
        OBJECTIVE_SYSTEM_MAPPING["exploratory"]
    )[:3]  # Top 3
    
    # Determine deployment phase suggestion
    if final_score >= 75:
        deployment_phase = "ready_for_deployment"
    elif final_score >= 50:
        deployment_phase = "foundation_building"
    else:
        deployment_phase = "discovery_phase"
    
    # Calculate priority score (0-100) based on objective alignment and readiness
    priority_score = calculate_priority_score(
        final_score,
        normalized_scores,
        primary_objective
    )
    
    return {
        "readiness_score": final_score,
        "readiness_level": readiness_level,
        "category_scores": normalized_scores,
        "weights_used": weights,
        "strength_category": strength_category,
        "strength_index": round(strength_index),
        "bottleneck_category": bottleneck_category,
        "bottleneck_index": round(bottleneck_index),
        "top_recommendations": top_recommendations,
        "priority_score": priority_score,
        "deployment_phase_suggestion": deployment_phase,
        "primary_objective": primary_objective
    }


def calculate_priority_score(
    readiness_score: int,
    category_scores: Dict[str, float],
    primary_objective: str
) -> int:
    """
    Calculate priority score (0-100) based on:
    - Overall readiness
    - Category balance
    - Objective alignment
    """
    # Base score from readiness
    base_score = readiness_score * 0.6
    
    # Balance bonus (lower variance = higher bonus)
    scores_list = list(category_scores.values())
    variance = sum((s - readiness_score) ** 2 for s in scores_list) / len(scores_list)
    balance_bonus = max(0, 20 - (variance / 10))
    
    # Objective alignment bonus
    alignment_bonus = 20 if primary_objective in OBJECTIVE_WEIGHTS else 10
    
    priority = base_score + balance_bonus + alignment_bonus
    return min(100, round(priority))


def get_system_recommendations(
    primary_objective: str,
    category_scores: Dict[str, float],
    automation_maturity: float
) -> List[str]:
    """
    Get top 3 system recommendations based on:
    - Primary objective
    - Lowest category score (bottleneck)
    - Automation maturity
    """
    base_recommendations = OBJECTIVE_SYSTEM_MAPPING.get(
        primary_objective,
        OBJECTIVE_SYSTEM_MAPPING["exploratory"]
    )
    
    # Return top 3
    return base_recommendations[:3]

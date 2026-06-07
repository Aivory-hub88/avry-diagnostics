"""
Intent Classifier Service
Analyzes user messages to determine intent and provides contextual understanding
"""

import logging
from typing import Dict, Any, Optional
from app.llm.openrouter_client import OpenRouterClient

logger = logging.getLogger(__name__)


class IntentClassifier:
    """Classifies user intents for better AI understanding"""
    
    INTENT_CATEGORIES = {
        "workflow_generation": "Create, build, or design a workflow/automation",
        "workflow_modification": "Modify, edit, or update an existing workflow",
        "diagnostics": "Analyze, assess, or evaluate business readiness",
        "blueprint": "Generate or create a business blueprint",
        "question": "Ask a question or seek information",
        "troubleshooting": "Debug, fix, or troubleshoot an issue",
        "integration": "Connect or integrate with external services",
        "data_analysis": "Analyze data or generate insights",
        "general": "General assistance or conversation"
    }
    
    def __init__(self):
        self.openrouter = OpenRouterClient()
        
    async def classify_intent(self, message: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Classify the intent of a user message
        
        Args:
            message: The user's message
            context: Optional context (tier, user_id, etc.)
            
        Returns:
            Dictionary with intent classification
        """
        try:
            # Use LLM to classify intent
            system_prompt = """You are an intent classifier for an AI automation platform. 
Analyze the user's message and determine their intent.

Respond in JSON format with these fields:
{
    "intent": "one of: workflow_generation, workflow_modification, diagnostics, blueprint, question, troubleshooting, integration, data_analysis, general",
    "confidence": 0.0-1.0,
    "summary": "brief 1-2 sentence summary of what user wants",
    "entities": ["key entities extracted from message"],
    "suggested_actions": ["list of 2-3 specific actions AI should take"]
}

Intent categories:
- workflow_generation: Create, build, or design a workflow/automation
- workflow_modification: Modify, edit, or update an existing workflow
- diagnostics: Analyze, assess, or evaluate business readiness
- blueprint: Generate or create a business blueprint
- question: Ask a question or seek information
- troubleshooting: Debug, fix, or troubleshoot an issue
- integration: Connect or integrate with external services
- data_analysis: Analyze data or generate insights
- general: General assistance or conversation"""

            user_prompt = f"Classify this user message: {message}"
            
            response = await self.openrouter.chat_completion(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                model="qwen/qwen-2.5-72b-instruct",
                temperature=0.3,
                max_tokens=300
            )
            
            # Parse response
            content = response.get("choices", [{}])[0].get("message", {}).get("content", "")
            
            import json
            try:
                # Try to extract JSON from response
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0].strip()
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0].strip()
                    
                classification = json.loads(content)
                
                # Add metadata
                classification["original_message"] = message
                classification["timestamp"] = None  # Will be set by route
                
                return classification
                
            except json.JSONDecodeError:
                logger.error(f"Failed to parse intent classification: {content}")
                return self._get_fallback_classification(message)
                
        except Exception as e:
            logger.error(f"Error classifying intent: {str(e)}")
            return self._get_fallback_classification(message)
    
    def _get_fallback_classification(self, message: str) -> Dict[str, Any]:
        """Fallback classification if LLM fails"""
        # Simple keyword-based fallback
        message_lower = message.lower()
        
        intent_keywords = {
            "workflow_generation": ["create", "build", "design", "make", "setup"],
            "workflow_modification": ["modify", "edit", "update", "change", "fix"],
            "diagnostics": ["analyze", "assess", "evaluate", "diagnose", "check"],
            "blueprint": ["blueprint", "plan", "strategy", "roadmap"],
            "question": ["what", "how", "why", "when", "explain"],
            "troubleshooting": ["error", "bug", "issue", "problem", "not working"],
            "integration": ["connect", "integrate", "link", "sync"],
            "data_analysis": ["analyze", "process", "extract", "insight"]
        }
        
        detected_intent = "general"
        max_matches = 0
        
        for intent, keywords in intent_keywords.items():
            matches = sum(1 for kw in keywords if kw in message_lower)
            if matches > max_matches:
                max_matches = matches
                detected_intent = intent
        
        return {
            "intent": detected_intent,
            "confidence": 0.5,
            "summary": f"User wants to: {message[:100]}",
            "entities": [],
            "suggested_actions": ["Process the user's request"],
            "original_message": message,
            "timestamp": None
        }

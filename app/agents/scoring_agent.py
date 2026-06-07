from app.agents.base import BaseAgent

class ScoringAgent(BaseAgent):
    async def process(self, input_data: dict) -> dict:
        """Evaluate AI readiness based on structured context"""
        context = input_data.get("structured_context", "")
        
        system_prompt = "You are an AI readiness evaluator. Score organizations on data quality, infrastructure, team skills, and use case clarity. Provide scores 1-10 and brief justifications."
        prompt = f"Context: {context}\n\nEvaluate AI readiness across key dimensions."
        
        evaluation = await self.llm.generate(prompt, system_prompt)
        
        return {
            "readiness_evaluation": evaluation,
            "context": context
        }

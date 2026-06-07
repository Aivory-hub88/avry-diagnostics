from app.agents.base import BaseAgent

class DiagnosisAgent(BaseAgent):
    async def process(self, input_data: dict) -> dict:
        """Identify top operational problems based on evaluation"""
        evaluation = input_data.get("readiness_evaluation", "")
        
        system_prompt = "You are an AI operations diagnostician. Identify the top 3-5 operational problems blocking AI adoption or effectiveness."
        prompt = f"Readiness evaluation: {evaluation}\n\nIdentify specific operational problems with root causes."
        
        diagnosis = await self.llm.generate(prompt, system_prompt)
        
        return {
            "diagnosis": diagnosis,
            "evaluation": evaluation
        }

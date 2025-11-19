from app.agents.tuf_agent import generate_answer

class AgentService:
    def ask(self, question: str) -> str:
        return generate_answer(question)

agent_service = AgentService()

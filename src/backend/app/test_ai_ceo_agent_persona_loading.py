import pytest
from src.backend.app.services.ai_ceo_agent import AICeoAgent, load_latest_persona, HORIPRO_2026_PERSONA


class TestAiCeoAgentPersonaLoading:
    def test_load_latest_persona_fallback(self):
        # Without saved persona, should return base
        persona = load_latest_persona()
        assert isinstance(persona, type(HORIPRO_2026_PERSONA))

    def test_ai_ceo_agent_uses_latest_persona(self):
        agent = AICeoAgent()
        assert hasattr(agent, 'persona')
        assert isinstance(agent.persona, type(HORIPRO_2026_PERSONA))
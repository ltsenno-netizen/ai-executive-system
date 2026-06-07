import pytest
from src.backend.app.models.ceo_learning_model import CeoLearningSnapshot, FinancialResultSummary
from src.backend.app.models.ai_ceo_model import AICeoPersona
from src.backend.app.services.ceo_learning_engine import CeoLearningEngine


class TestCeoLearningEngine:
    def test_update_persona_from_history_consecutive_profit_shortfall(self):
        engine = CeoLearningEngine()
        base_persona = AICeoPersona(
            aggressiveness=0.8,
            risk_tolerance=0.6,
            brand_priority=0.7,
            short_term_focus=0.5,
            long_term_focus=0.8,
        )
        history = [
            CeoLearningSnapshot(
                period='2026-01',
                ceo_persona=base_persona,
                financial_result=FinancialResultSummary(revenue=1000000, operating_profit=-10000),
                board_status='rejected',
            ),
            CeoLearningSnapshot(
                period='2026-02',
                ceo_persona=base_persona,
                financial_result=FinancialResultSummary(revenue=1000000, operating_profit=-20000),
                board_status='rejected',
            ),
            CeoLearningSnapshot(
                period='2026-03',
                ceo_persona=base_persona,
                financial_result=FinancialResultSummary(revenue=1000000, operating_profit=-15000),
                board_status='rejected',
            ),
        ]

        new_persona = engine.update_persona_from_history(base_persona, history)

        assert new_persona.aggressiveness < base_persona.aggressiveness
        assert new_persona.risk_tolerance < base_persona.risk_tolerance

    def test_update_persona_from_history_brand_success(self):
        engine = CeoLearningEngine()
        base_persona = AICeoPersona(
            aggressiveness=0.6,
            risk_tolerance=0.6,
            brand_priority=0.5,
            short_term_focus=0.5,
            long_term_focus=0.8,
        )
        history = [
            CeoLearningSnapshot(
                period='2026-01',
                ceo_persona=base_persona,
                financial_result=FinancialResultSummary(revenue=1000000, operating_profit=50000),
                board_status='approved',
            ),
            CeoLearningSnapshot(
                period='2026-02',
                ceo_persona=base_persona,
                financial_result=FinancialResultSummary(revenue=1100000, operating_profit=60000),
                board_status='approved',
            ),
        ]

        new_persona = engine.update_persona_from_history(base_persona, history)

        assert new_persona.brand_priority > base_persona.brand_priority
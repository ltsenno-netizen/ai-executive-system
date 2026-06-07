import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'backend')))

from app.services.ceo_succession_engine import CeoSuccessionEngine
from app.models.ai_ceo_model import AICeoPersona
from app.models.ceo_learning_model import CeoLearningSnapshot, FinancialResultSummary


def test_generate_three_ceo_candidates():
    engine = CeoSuccessionEngine()
    current_persona = AICeoPersona(
        aggressiveness=0.6,
        risk_tolerance=0.5,
        brand_priority=0.7,
        short_term_focus=0.5,
        long_term_focus=0.8,
    )
    history = [
        CeoLearningSnapshot(
            period='2025-10',
            ceo_persona=current_persona,
            financial_result=FinancialResultSummary(revenue=100.0, operating_profit=10.0),
            board_status='approved',
        )
    ]

    candidates = engine.generate_ceo_candidates(current_persona, history)

    assert len(candidates) == 3
    assert {c.candidate_id for c in candidates} == {'A', 'B', 'C'}
    assert candidates[0].similarity_to_current > 0.8
    assert candidates[1].persona.aggressiveness >= current_persona.aggressiveness
    assert candidates[2].persona.risk_tolerance <= current_persona.risk_tolerance


def test_candidate_strengths_and_weaknesses_are_assigned():
    engine = CeoSuccessionEngine()
    current_persona = AICeoPersona(
        aggressiveness=0.6,
        risk_tolerance=0.5,
        brand_priority=0.7,
        short_term_focus=0.5,
        long_term_focus=0.8,
    )
    candidates = engine.generate_ceo_candidates(current_persona, [])

    for candidate in candidates:
        assert candidate.strengths
        assert candidate.weaknesses
        assert 0.0 <= candidate.innovation_bias <= 1.0
        assert 0.0 <= candidate.similarity_to_current <= 1.0

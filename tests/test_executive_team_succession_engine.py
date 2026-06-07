import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'backend')))

from src.backend.executive_team_succession_engine import ExecutiveTeamSuccessionEngine
from src.backend.executive_team_succession_model import ExecutivePersona, ExecutiveRole


def test_generate_three_executive_candidates():
    engine = ExecutiveTeamSuccessionEngine()
    current_persona = ExecutivePersona(
        role=ExecutiveRole.CFO,
        financial_focus=0.6,
        operational_focus=0.5,
        brand_focus=0.7,
        people_focus=0.5,
        risk_tolerance=0.5,
        innovation_bias=0.5,
    )
    history = []

    candidates = engine.generate_executive_candidates(current_persona, ExecutiveRole.CFO, history)

    assert len(candidates) == 3
    assert {c.candidate_id for c in candidates} == {'A', 'B', 'C'}
    assert candidates[0].similarity_to_current > 0.8
    assert candidates[1].persona.innovation_bias >= current_persona.innovation_bias
    assert candidates[2].persona.risk_tolerance <= current_persona.risk_tolerance


def test_candidate_strengths_and_weaknesses_are_assigned():
    engine = ExecutiveTeamSuccessionEngine()
    current_persona = ExecutivePersona(
        role=ExecutiveRole.CFO,
        financial_focus=0.6,
        operational_focus=0.5,
        brand_focus=0.7,
        people_focus=0.5,
        risk_tolerance=0.5,
        innovation_bias=0.5,
    )
    candidates = engine.generate_executive_candidates(current_persona, ExecutiveRole.CFO, [])

    for candidate in candidates:
        assert candidate.strengths
        assert candidate.weaknesses
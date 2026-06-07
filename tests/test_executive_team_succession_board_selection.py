import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'backend')))

from src.backend.app.services.ai_board_agent import AIBoardAgent
from src.backend.executive_team_succession_engine import ExecutiveTeamSuccessionEngine
from src.backend.executive_team_succession_model import ExecutivePersona, ExecutiveRole


def test_board_selects_a_candidate_from_three():
    engine = ExecutiveTeamSuccessionEngine()
    board = AIBoardAgent()
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

    decision = board.select_next_executive(
        role=ExecutiveRole.CFO,
        candidates=candidates,
    )

    assert decision.selected_candidate_id in {'A', 'B', 'C'}
    assert 'financial' in decision.board_votes
    assert 'brand' in decision.board_votes
    assert 'risk' in decision.board_votes
    assert 'org' in decision.board_votes
    assert decision.rationale
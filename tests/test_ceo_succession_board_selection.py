import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'backend')))

from app.services.ai_board_agent import AIBoardAgent
from app.services.ceo_succession_engine import CeoSuccessionEngine
from app.models.ai_ceo_model import AICeoPersona
from app.models.ceo_learning_model import CeoLearningSnapshot, FinancialResultSummary


def test_board_selects_a_candidate_from_three():
    engine = CeoSuccessionEngine()
    board = AIBoardAgent()
    current_persona = AICeoPersona(
        aggressiveness=0.6,
        risk_tolerance=0.5,
        brand_priority=0.7,
        short_term_focus=0.5,
        long_term_focus=0.8,
    )
    candidates = engine.generate_ceo_candidates(current_persona, [])

    decision = board.select_next_ceo(
        candidates=candidates,
        current_financials={'cash_balance': 5.0, 'operating_profit': 2.0},
        market_state={'volatility': 0.1},
        org_state={'units': [{'workload_index': 0.5}]},
    )

    assert decision.selected_candidate_id in {'A', 'B', 'C'}
    assert 'financial' in decision.board_votes
    assert 'brand' in decision.board_votes
    assert 'risk' in decision.board_votes
    assert 'org' in decision.board_votes
    assert decision.rationale

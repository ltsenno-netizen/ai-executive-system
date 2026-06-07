import os
import sys
from unittest.mock import Mock

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'backend')))

from app.services.ai_ceo_agent import AICeoAgent
from app.services.ai_board_agent import AIBoardAgent
from app.models.ai_ceo_model import AICeoPersona
from app.models.external_environment_model_v2 import (
    ExternalEnvironmentState,
    PESTFactors,
    CompetitorAction,
)
from app.models.executive_meeting_model import DecisionOption


def test_environment_influences_ceo_and_board_decisions():
    persona = AICeoPersona(
        aggressiveness=0.4,
        risk_tolerance=0.7,
        brand_priority=0.4,
        short_term_focus=0.5,
        long_term_focus=0.7,
    )

    environment = ExternalEnvironmentState(
        period='2026-01',
        pest=PESTFactors(political=0.5, economic=0.3, social=0.6, technological=0.8),
        competitors=[CompetitorAction(competitor_name='Rival', aggressiveness=0.9, market_share_shift=-0.02)],
        shocks=[],
        market_growth_modifier=-0.02,
        risk_modifier=0.03,
    )

    neutral_environment = ExternalEnvironmentState(
        period='2026-01',
        pest=PESTFactors(political=0.5, economic=0.5, social=0.5, technological=0.5),
        competitors=[CompetitorAction(competitor_name='Rival', aggressiveness=0.2, market_share_shift=0.01)],
        shocks=[],
        market_growth_modifier=0.0,
        risk_modifier=0.0,
    )

    options = [
        DecisionOption(
            id='A',
            label='Aggressive Growth',
            description='High growth initiative',
            growth_score=0.9,
            risk_level='High',
            expected_impact_score=0.9,
            short_term_profit=0.1,
            long_term_value=0.9,
            brand_impact=0.2,
            actions=['expand_market'],
            pros=['Potential scale'],
            cons=['Higher financial risk'],
        ),
        DecisionOption(
            id='B',
            label='Stabilize Core',
            description='Secure existing operations',
            growth_score=0.4,
            risk_level='Low',
            expected_impact_score=0.5,
            short_term_profit=0.6,
            long_term_value=0.5,
            brand_impact=0.3,
            actions=['improve_efficiency'],
            pros=['Lower risk'],
            cons=['Limited upside'],
        ),
    ]

    financials = {'cash_balance': 8.0, 'operating_profit': 3.0}
    market_state = {'market_index_by_segment': {'segment1': 1.0}, 'volatility': 0.2}
    org_state = {'units': [{'workload_index': 0.4}]}

    ceo_with_environment = AICeoAgent(persona=persona, environment=environment)
    ceo_with_neutral = AICeoAgent(persona=persona, environment=neutral_environment)

    score_environment_a = ceo_with_environment._score_option(
        options[0],
        persona,
        cash_balance=8.0,
        market_strength=1.0,
        workload_index=0.4,
        execution_capacity=1.0,
        execution_efficiency=1.0,
        culture=None,
        environment=environment,
    )
    score_neutral_a = ceo_with_neutral._score_option(
        options[0],
        persona,
        cash_balance=8.0,
        market_strength=1.0,
        workload_index=0.4,
        execution_capacity=1.0,
        execution_efficiency=1.0,
        culture=None,
        environment=neutral_environment,
    )

    assert score_environment_a != score_neutral_a

    board = AIBoardAgent()
    board_decision_environment = board.review_ceo_decision(
        ceo_option=options[0],
        ceo_rationale='Test rationale',
        options=options,
        financials=financials,
        market_state=market_state,
        org_state=org_state,
        ceo_persona=persona,
        environment=environment,
    )
    board_decision_neutral = board.review_ceo_decision(
        ceo_option=options[0],
        ceo_rationale='Test rationale',
        options=options,
        financials=financials,
        market_state=market_state,
        org_state=org_state,
        ceo_persona=persona,
        environment=neutral_environment,
    )

    assert isinstance(board_decision_environment.status, str)
    assert isinstance(board_decision_neutral.status, str)

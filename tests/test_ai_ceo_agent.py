import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'backend')))

from app.ai_ceo_agent import AICeoAgent, AICeoPersona, HORIPRO_2026_PERSONA
from app.models.executive_meeting_model import DecisionOption


def make_option(option_id: str, label: str, risk_level: str, expected_score: float) -> DecisionOption:
    return DecisionOption(
        id=option_id,
        label=label,
        actions=[],
        pros=[],
        cons=[],
        risk_level=risk_level,
        expected_impact_score=expected_score,
    )


def test_ai_ceo_prefers_defensive_when_cash_low():
    agent = AICeoAgent()
    options = [
        make_option('A', '攻め', 'High', 0.9),
        make_option('B', '守り', 'Low', 0.4),
        make_option('C', 'バランス', 'Medium', 0.65),
    ]
    financials = {'cash_balance': 1.0}
    market_state = {'market_index_by_segment': {'A': 1.0}, 'active_events': []}
    org_state = {'units': [{'workload_index': 0.8}]}
    execution_state = {'capacity': 0.8, 'efficiency': 0.9}

    selected, rationale = agent.select_option(options, financials, market_state, org_state, execution_state)

    assert selected.id == 'B'
    assert rationale


def test_ai_ceo_prefers_aggressive_when_market_strong():
    agent = AICeoAgent()
    options = [
        make_option('A', '攻め', 'High', 0.9),
        make_option('B', '守り', 'Low', 0.4),
        make_option('C', 'バランス', 'Medium', 0.65),
    ]
    financials = {'cash_balance': 6.0}
    market_state = {'market_index_by_segment': {'AI': 1.5}, 'active_events': []}
    org_state = {'units': [{'workload_index': 0.7}]}
    execution_state = {'capacity': 0.9, 'efficiency': 0.9}

    selected, rationale = agent.select_option(options, financials, market_state, org_state, execution_state)

    assert selected.id == 'A'
    assert rationale


def test_ai_ceo_avoids_aggressive_when_execution_low():
    agent = AICeoAgent()
    options = [
        make_option('A', '攻め', 'High', 0.9),
        make_option('B', '守り', 'Low', 0.4),
        make_option('C', 'バランス', 'Medium', 0.65),
    ]
    financials = {'cash_balance': 8.0}
    market_state = {'market_index_by_segment': {'AI': 1.3}, 'active_events': []}
    org_state = {'units': [{'workload_index': 1.2}]}
    execution_state = {'capacity': 0.4, 'efficiency': 0.6}

    selected, rationale = agent.select_option(options, financials, market_state, org_state, execution_state)

    assert selected.id != 'A'
    assert rationale


def test_ai_ceo_persona_fields_are_available():
    persona = HORIPRO_2026_PERSONA
    assert isinstance(persona, AICeoPersona)
    assert 0.6 <= persona.aggressiveness <= 0.8
    assert persona.brand_priority == 0.8


def test_ai_ceo_rationale_mentions_horipro_style():
    agent = AICeoAgent()
    options = [
        make_option('A', '攻め', 'High', 0.9),
        make_option('B', '守り', 'Low', 0.4),
        make_option('C', 'バランス', 'Medium', 0.65),
    ]
    financials = {'cash_balance': 3.0}
    market_state = {'market_index_by_segment': {'AI': 1.1}, 'active_events': []}
    org_state = {'units': [{'workload_index': 0.7}]}
    execution_state = {'capacity': 0.8, 'efficiency': 0.9}

    _, rationale = agent.select_option(options, financials, market_state, org_state, execution_state)
    assert '攻め×回転率×ブランド戦略' in rationale

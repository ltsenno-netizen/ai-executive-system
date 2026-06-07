import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'backend')))

from app.services.ai_board_agent import AIBoardAgent
from app.models.executive_meeting_model import DecisionOption


def make_decision_options():
    return [
        DecisionOption(
            id='A',
            label='攻めの投資継続',
            actions=['execute_tranche_2'],
            pros=['成長機会を確保'],
            cons=['キャッシュ負担'],
            risk_level='High',
            long_term_value=0.9,
            short_term_profit=0.8,
        ),
        DecisionOption(
            id='B',
            label='守りの投資抑制',
            actions=['delay_tranche_2'],
            pros=['流動性確保'],
            cons=['成長機会の遅延'],
            risk_level='Low',
            long_term_value=0.5,
            short_term_profit=0.6,
        ),
        DecisionOption(
            id='C',
            label='バランス型',
            actions=['partial_tranche'],
            pros=['リスク低減と成長維持'],
            cons=['調整コストが増える'],
            risk_level='Medium',
            long_term_value=0.7,
            short_term_profit=0.55,
        ),
    ]


def test_multi_member_board_aggregation():
    board = AIBoardAgent()
    options = make_decision_options()
    decision = board.review_ceo_decision(
        ceo_option=options[0],  # High risk option
        ceo_rationale='高成長を狙う。',
        options=options,
        financials={'cash_balance': 5.0},
        market_state={'market_index_by_segment': {'AI': 1.0}, 'active_events': []},
        org_state={'units': [{'workload_index': 0.8}]},
        ceo_persona=None,
    )

    # Check that decision has member opinions
    assert len(decision.member_opinions) == 4  # Financial, Brand, Risk, Org directors
    assert decision.status in ['approved', 'conditional', 'rejected']
    assert decision.final_option_id in ['A', 'B', 'C']
    assert decision.board_rationale is not None

    # Check member opinions structure
    for op in decision.member_opinions:
        assert op.member_role in ['financial', 'brand', 'risk', 'org']
        assert op.preferred_option_id in ['A', 'B', 'C']
        assert op.rationale is not None
        assert isinstance(op.risk_flag, bool)


def test_board_rejects_when_multiple_risk_flags():
    board = AIBoardAgent()
    options = make_decision_options()
    decision = board.review_ceo_decision(
        ceo_option=options[0],  # High risk option
        ceo_rationale='高成長を狙う。',
        options=options,
        financials={'cash_balance': 1.0},  # Low cash
        market_state={'market_index_by_segment': {'AI': 0.8}, 'active_events': ['market_crash']},  # Bad market
        org_state={'units': [{'workload_index': 1.5}]},  # High workload
        ceo_persona=None,
    )

    # Should be rejected due to multiple risk flags
    assert decision.status == 'rejected'
    assert len(decision.member_opinions) == 4


def test_board_approves_when_ceo_has_majority_support():
    board = AIBoardAgent()
    options = make_decision_options()
    decision = board.review_ceo_decision(
        ceo_option=options[1],  # Low risk option
        ceo_rationale='安定を重視。',
        options=options,
        financials={'cash_balance': 5.0},
        market_state={'market_index_by_segment': {'AI': 1.0}, 'active_events': []},
        org_state={'units': [{'workload_index': 0.8}]},
        ceo_persona=None,
    )

    # Should be approved if CEO has majority support
    assert decision.status == 'approved'
    assert decision.final_option_id == 'B'
    assert len(decision.member_opinions) == 4


# Legacy tests (commented out as they use old single-board logic)
# def test_board_approves_low_risk_ceo_option():
#     ...

# def test_board_rejects_high_risk_when_cash_low():
#     ...

# def test_board_returns_conditional_for_low_long_term_value():
#     ...

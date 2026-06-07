import os
import sys
import tempfile
from unittest.mock import Mock, patch

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'backend')))

from app.services.quarterly_review_engine import QuarterlyReviewEngine
from app.models.quarterly_review_model import QuarterlyReview
from app.models.mid_term_plan_model import MidTermPlan
from app.models.ai_ceo_model import AICeoPersona
from app.services.ai_board_members import FinancialDirector, BrandDirector, RiskDirector, OrgDirector


def test_build_quarterly_review():
    """Test building a quarterly review"""
    engine = QuarterlyReviewEngine()

    # Mock monthly results
    monthly_results = [
        Mock(
            financials={'revenue': 1000000, 'operating_profit': 100000, 'cash_balance': 2000000},
            execution={'completed_initiatives': ['init1', 'init2'], 'delayed_initiatives': ['init3']},
            org_state={'avg_workload_index': 0.7}
        ),
        Mock(
            financials={'revenue': 1100000, 'operating_profit': 110000, 'cash_balance': 2100000},
            execution={'completed_initiatives': ['init4'], 'delayed_initiatives': []},
            org_state={'avg_workload_index': 0.8}
        ),
        Mock(
            financials={'revenue': 1200000, 'operating_profit': 120000, 'cash_balance': 2200000},
            execution={'completed_initiatives': ['init5', 'init6'], 'delayed_initiatives': ['init7']},
            org_state={'avg_workload_index': 0.6}
        ),
    ]

    # Mock mid-term plan
    mid_term_plan = Mock()
    mid_term_plan.quarterly_targets = {'2026-Q1': {'revenue': 3000000, 'profit': 300000}}

    # Mock CEO persona
    ceo_persona = Mock()
    ceo_persona.aggressiveness = 0.8
    ceo_persona.brand_priority = 0.6

    # Mock board members
    board_members = [FinancialDirector(), BrandDirector(), RiskDirector(), OrgDirector()]

    review = engine.build_quarterly_review(
        quarter='2026-Q1',
        monthly_results=monthly_results,
        mid_term_plan=mid_term_plan,
        ceo_persona=ceo_persona,
        board_members=board_members,
    )

    # Assertions
    assert isinstance(review, QuarterlyReview)
    assert review.quarter == '2026-Q1'
    assert review.financial.revenue_total == 3300000  # 1M + 1.1M + 1.2M
    assert review.financial.operating_profit_total == 330000  # 100K + 110K + 120K
    assert review.financial.cash_end == 2200000
    assert review.execution.initiatives_completed == 5  # 2 + 1 + 2
    assert review.execution.initiatives_delayed == 2  # 1 + 0 + 1
    assert abs(review.execution.org_load_index - 0.7) < 0.01  # Average of 0.7, 0.8, 0.6
    assert review.gap_analysis is not None
    assert len(review.next_quarter_focus) > 0
    assert review.board_review.status in ['approved', 'conditional', 'rejected']
    assert len(review.board_review.member_opinions) == 4


def test_gap_analysis_generation():
    """Test gap analysis generation"""
    engine = QuarterlyReviewEngine()

    financial = Mock()
    financial.revenue_vs_plan = 0.05  # 5% over plan
    financial.profit_vs_plan = -0.1   # 10% under plan

    execution = Mock()
    execution.org_load_index = 0.9
    execution.initiatives_delayed = 5
    execution.initiatives_completed = 10

    mid_term_plan = Mock()

    analysis = engine._build_gap_analysis(financial, execution, mid_term_plan)

    assert '売上' in analysis
    assert '利益' in analysis
    assert '組織負荷' in analysis
    assert '遅延' in analysis


def test_next_quarter_focus_generation():
    """Test next quarter focus generation"""
    engine = QuarterlyReviewEngine()

    gap_analysis = "売上は計画を下回り、利益も計画を下回り、組織負荷が高く、実行力が課題。"
    ceo_persona = Mock()
    ceo_persona.aggressiveness = 0.8
    ceo_persona.brand_priority = 0.7

    focus = engine._generate_next_quarter_focus(gap_analysis, ceo_persona)

    assert isinstance(focus, list)
    assert len(focus) <= 4  # Max 4 items
    assert all(isinstance(item, str) for item in focus)


def test_board_review_conduct():
    """Test board review conduct"""
    engine = QuarterlyReviewEngine()

    financial = Mock()
    financial.revenue_vs_plan = -0.15
    financial.profit_vs_plan = -0.2
    financial.cash_end = 0.5

    execution = Mock()
    execution.org_load_index = 0.95

    gap_analysis = "重大な財務・実行課題あり"

    board_members = [FinancialDirector(), BrandDirector(), RiskDirector(), OrgDirector()]

    board_review = engine._conduct_board_review(
        '2026-Q1', financial, execution, gap_analysis, board_members
    )

    assert board_review.status in ['approved', 'conditional', 'rejected']
    assert board_review.rationale is not None
    assert len(board_review.member_opinions) == 4
    for opinion in board_review.member_opinions:
        assert opinion.member_role in ['financial', 'brand', 'risk', 'org']
        assert opinion.rationale is not None
        assert isinstance(opinion.risk_flag, bool)
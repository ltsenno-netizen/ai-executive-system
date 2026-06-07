import pytest
from src.backend.app.models.mid_term_plan_model import MidTermPlan
from src.backend.app.services.mid_term_plan_engine import MidTermPlanEngine


class TestMidTermPlanEngine:
    def test_build_mid_term_plan_basic(self):
        engine = MidTermPlanEngine()
        history_months = [
            {
                'financials': {'revenue': 1000000, 'operating_profit': 100000},
                'environment': {'market_growth': 0.05}
            }
        ]
        ceo_persona = {'risk_tolerance': 0.5, 'growth_focus': 0.8}
        board_decisions = []
        current_financials = {'revenue': 1000000, 'operating_profit': 100000, 'fiscal_year': 2026}
        current_market_state = {'market_growth': 0.05}
        horizon_years = 3

        plan = engine.build_mid_term_plan(
            history_months=history_months,
            ceo_persona=ceo_persona,
            board_decisions=board_decisions,
            current_financials=current_financials,
            current_market_state=current_market_state,
            horizon_years=horizon_years,
        )

        assert isinstance(plan, MidTermPlan)
        assert plan.start_year == 2026  # current date
        assert plan.end_year == 2028
        assert len(plan.financial.years) == 3
        assert plan.vision is not None
        assert plan.board_comment is not None
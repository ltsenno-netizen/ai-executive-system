import os
import sys
from unittest.mock import Mock, patch

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'backend')))

from app.services.executive_dashboard_service import ExecutiveDashboardService
from app.models.executive_dashboard_model import CeoSuccessionSummary
from app.models.ai_ceo_model import AICeoPersona
from app.models.ceo_succession_model import CeoSuccessionDecision


def test_dashboard_includes_ceo_succession_summary():
    service = ExecutiveDashboardService()
    persona = AICeoPersona(
        aggressiveness=0.5,
        risk_tolerance=0.5,
        brand_priority=0.6,
        short_term_focus=0.4,
        long_term_focus=0.7,
    )
    succession_decision = CeoSuccessionDecision(
        period='2026-01',
        selected_candidate_id='A',
        rationale='多数決で選任。',
        board_votes={
            'financial': 'A',
            'brand': 'A',
            'risk': 'A',
            'org': 'A',
        },
        transition_notes='安定重視の交代。',
    )

    with patch.object(service, 'ceo_succession_service') as mock_succession, \
         patch.object(service, 'integration_service') as mock_integration, \
         patch.object(service, 'execution_service'), \
         patch.object(service, 'portfolio_service') as mock_portfolio, \
         patch.object(service, 'meeting_service'), \
         patch.object(service, 'narrative_service') as mock_narrative, \
         patch.object(service, 'report_service') as mock_report, \
         patch.object(service, 'plan_service') as mock_plan, \
         patch.object(service, 'ceo_learning_service') as mock_learning, \
         patch.multiple(service, **{
             'aggregate_pl': Mock(return_value={
                 'month': 1,
                 'revenue': 0.0,
                 'cost': 0.0,
                 'profit': 0.0,
                 'profit_margin': 0.0,
                 'cash_balance': 0.0,
             }),
             'aggregate_kpis': Mock(return_value={'month': 1, 'kpis': {}}),
             'aggregate_operations': Mock(return_value={'month': 1, 'department_load': {}, 'active_tasks': 0, 'incidents': 0}),
             'aggregate_issues': Mock(return_value={'month': 1, 'issues': []}),
             'aggregate_improvements': Mock(return_value={'month': 1, 'executed_actions': [], 'updated_priorities': {}}),
             'aggregate_portfolio_summary': Mock(return_value=None),
             'aggregate_meeting_summary': Mock(return_value=None),
             'aggregate_meeting_timeline': Mock(return_value=None),
             'aggregate_organization_summary': Mock(return_value={'units': []}),
             'aggregate_financial_summary': Mock(return_value={
                 'cash_reserves': 0.0,
                 'free_cash_flow': 0.0,
                 'short_term_debt': 0.0,
                 'long_term_debt': 0.0,
                 'monthly_debt_service': 0.0,
                 'available_credit_line': 0.0,
                 'committed_capex': 0.0,
                 'liquidity_buffer_months': 0.0,
                 'investment_requests_pending': [],
                 'emergency_playbook': {},
             }),
             'aggregate_execution_summary': Mock(return_value={
                 'capacity': 0.0,
                 'load': 0.0,
                 'efficiency': 0.0,
                 'execution_capacity_score': 0.0,
                 'forecast': [],
             }),
             'aggregate_market_summary': Mock(return_value={'segments': [], 'active_events': [], 'scenario_results_preview': None}),
         }):
        mock_succession.get_latest_succession_decision.return_value = succession_decision
        mock_learning.get_latest_persona.return_value = persona
        mock_integration.company_service.build_customer_summary.return_value = []
        mock_portfolio.corporate_service.load_fundamentals.return_value = Mock()
        mock_narrative.generate_monthly_narrative.return_value = None
        mock_narrative.get_latest_narrative.return_value = None
        mock_report.get_latest_report.return_value = None
        mock_report.list_reports.return_value = []
        mock_plan.get_latest_plan.return_value = None

        dashboard = service.build_dashboard(month=1)

        assert dashboard.ceo_succession is not None
        assert isinstance(dashboard.ceo_succession, CeoSuccessionSummary)
        assert dashboard.ceo_succession.last_succession_period == '2026-01'
        assert dashboard.ceo_succession.new_ceo_persona.aggressiveness == 0.5
        assert dashboard.ceo_succession.rationale == '多数決で選任。'

import os
import sys
from unittest.mock import Mock, patch

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'backend')))

from app.services.executive_dashboard_service import ExecutiveDashboardService
from app.models.executive_dashboard_model import QuarterlyReviewSummary


def test_dashboard_includes_quarterly_review():
    """Test that dashboard includes quarterly review summary"""
    service = ExecutiveDashboardService()

    # Mock quarterly review service
    with patch.object(service, 'quarterly_review_service') as mock_qr_service:
        mock_review = Mock()
        mock_review.quarter = '2026-Q1'
        mock_review.financial.revenue_total = 3200000
        mock_review.financial.operating_profit_total = 410000
        mock_review.board_review.status = 'conditional'
        mock_review.next_quarter_focus = ['Focus 1', 'Focus 2']

        mock_qr_service.get_latest_quarterly_review.return_value = mock_review

        # Mock other dependencies to avoid full dashboard build
        with patch.object(service, 'integration_service') as mock_integration, \
             patch.object(service, 'operational_service'), \
             patch.object(service, 'cycle_service'), \
             patch.object(service, 'portfolio_service') as mock_portfolio, \
             patch.object(service, 'execution_service'), \
             patch.object(service, 'meeting_service'), \
             patch.object(service, 'narrative_service') as mock_narrative, \
             patch.object(service, 'report_service') as mock_report, \
             patch.object(service, 'plan_service') as mock_plan, \
             patch.object(service, 'ceo_learning_service'), \
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
            mock_integration.company_service.build_customer_summary.return_value = []
            mock_portfolio.corporate_service.load_fundamentals.return_value = Mock()
            mock_narrative.generate_monthly_narrative.return_value = None
            mock_narrative.get_latest_narrative.return_value = None
            mock_report.get_latest_report.return_value = None
            mock_report.list_reports.return_value = []
            mock_plan.get_latest_plan.return_value = None

            dashboard = service.build_dashboard(month=1)

            assert dashboard.quarterly_review is not None
            assert isinstance(dashboard.quarterly_review, QuarterlyReviewSummary)
            assert dashboard.quarterly_review.quarter == '2026-Q1'
            assert dashboard.quarterly_review.revenue_total == 3200000
            assert dashboard.quarterly_review.profit_total == 410000
            assert dashboard.quarterly_review.board_status == 'conditional'
            assert dashboard.quarterly_review.next_quarter_focus == ['Focus 1', 'Focus 2']


def test_dashboard_without_quarterly_review():
    """Test dashboard when no quarterly review is available"""
    service = ExecutiveDashboardService()

    # Mock quarterly review service to return None
    with patch.object(service, 'quarterly_review_service') as mock_qr_service:
        mock_qr_service.get_latest_quarterly_review.return_value = None

        # Mock other dependencies
        with patch.object(service, 'integration_service') as mock_integration, \
             patch.object(service, 'operational_service'), \
             patch.object(service, 'cycle_service'), \
             patch.object(service, 'portfolio_service') as mock_portfolio, \
             patch.object(service, 'execution_service'), \
             patch.object(service, 'meeting_service'), \
             patch.object(service, 'narrative_service') as mock_narrative, \
             patch.object(service, 'report_service') as mock_report, \
             patch.object(service, 'plan_service') as mock_plan, \
             patch.object(service, 'ceo_learning_service'), \
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
            mock_integration.company_service.build_customer_summary.return_value = []
            mock_portfolio.corporate_service.load_fundamentals.return_value = Mock()
            mock_narrative.generate_monthly_narrative.return_value = None
            mock_narrative.get_latest_narrative.return_value = None
            mock_report.get_latest_report.return_value = None
            mock_report.list_reports.return_value = []
            mock_plan.get_latest_plan.return_value = None

            dashboard = service.build_dashboard(month=1)

            assert dashboard.quarterly_review is None


def test_quarterly_review_error_handling():
    """Test error handling when quarterly review service fails"""
    service = ExecutiveDashboardService()

    # Mock quarterly review service to raise exception
    with patch.object(service, 'quarterly_review_service') as mock_qr_service:
        mock_qr_service.get_latest_quarterly_review.side_effect = Exception('Service unavailable')

        # Mock other dependencies
        with patch.object(service, 'integration_service') as mock_integration, \
             patch.object(service, 'operational_service'), \
             patch.object(service, 'cycle_service'), \
             patch.object(service, 'portfolio_service') as mock_portfolio, \
             patch.object(service, 'execution_service'), \
             patch.object(service, 'meeting_service'), \
             patch.object(service, 'narrative_service') as mock_narrative, \
             patch.object(service, 'report_service') as mock_report, \
             patch.object(service, 'plan_service') as mock_plan, \
             patch.object(service, 'ceo_learning_service'), \
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
            mock_integration.company_service.build_customer_summary.return_value = []
            mock_portfolio.corporate_service.load_fundamentals.return_value = Mock()
            mock_narrative.generate_monthly_narrative.return_value = None
            mock_narrative.get_latest_narrative.return_value = None
            mock_report.get_latest_report.return_value = None
            mock_report.list_reports.return_value = []
            mock_plan.get_latest_plan.return_value = None

            dashboard = service.build_dashboard(month=1)

            # Should handle error gracefully and set quarterly_review to None
            assert dashboard.quarterly_review is None
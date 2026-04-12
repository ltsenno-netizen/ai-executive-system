import json
import os
import shutil
import tempfile
from typing import Dict, List, Optional

from ..models.executive_dashboard_model import (
    ExecutiveDashboard,
    ExecutiveCustomerSegmentSummary,
    ExecutiveCustomerSummary,
    ExecutiveFinancialSummary,
    ExecutiveMarketEventSummary,
    ExecutiveMarketSegmentSummary,
    ExecutiveMarketSummary,
    ExecutiveImprovementSummary,
    ExecutiveIssueSummary,
    ExecutiveKPISummary,
    ExecutiveOpsSummary,
    ExecutivePLSummary,
    ExecutivePortfolioSummary,
    ExecutiveMeetingSummary,
    ExecutiveOrganizationSummary,
    ExecutiveOrganizationUnitSummary,
)
from ..models.improvement_cycle_model import ContinuousImprovementState
from .business_portfolio_service import BusinessPortfolioService
from .company_operations_integration_service import CompanyOperationsIntegrationService
from .executive_meeting_service import ExecutiveMeetingService
from .executive_narrative_service import ExecutiveNarrativeService
from .improvement_cycle_service import ImprovementCycleService
from .operational_issues_service import OperationalIssuesService


class ExecutiveDashboardService:
    def __init__(self):
        self.integration_service = CompanyOperationsIntegrationService()
        self.operational_service = OperationalIssuesService()
        self.cycle_service = ImprovementCycleService()
        self.portfolio_service = BusinessPortfolioService()
        self.meeting_service = ExecutiveMeetingService()
        self.narrative_service = ExecutiveNarrativeService()
        self.state_file = os.path.abspath(
            os.path.join(os.path.dirname(__file__), '../../../../data/samples/improvement_cycle_state.json')
        )
        self._dashboard_cache: Dict[int, ExecutiveDashboard] = {}

    def load_cycle_state(self) -> ContinuousImprovementState:
        return self.cycle_service.load_cycle_state()

    def _sum_money(self, value):
        if isinstance(value, dict):
            return float(sum(value.values()))
        if isinstance(value, (int, float)):
            return float(value)
        return 0.0

    def aggregate_pl(self, month: int) -> ExecutivePLSummary:
        monthly_state = self.integration_service.simulate_month_full(month)
        pl = monthly_state.get('pl', {})

        return ExecutivePLSummary(
            month=month,
            revenue=self._sum_money(pl.get('revenue', 0.0)),
            cost=self._sum_money(pl.get('cost', 0.0)),
            profit=float(pl.get('profit', 0.0)),
            profit_margin=float(pl.get('profit_margin', 0.0)),
            cash_balance=float(pl.get('cash_balance', 0.0)),
        )

    def aggregate_kpis(self, month: int) -> ExecutiveKPISummary:
        monthly_state = self.integration_service.simulate_month_full(month)
        kpis = monthly_state.get('pl', {}).get('kpis', {})

        return ExecutiveKPISummary(
            month=month,
            kpis={k: float(v) for k, v in kpis.items()},
        )

    def aggregate_operations(self, month: int) -> ExecutiveOpsSummary:
        monthly_state = self.integration_service.simulate_month_full(month)
        operations = monthly_state.get('operations', {})
        generated_tasks = operations.get('generated_tasks', []) if isinstance(operations, dict) else []
        generated_incidents = operations.get('generated_incidents', []) if isinstance(operations, dict) else []

        return ExecutiveOpsSummary(
            month=month,
            department_load={k: float(v) for k, v in operations.get('department_load', {}).items()} if isinstance(operations, dict) else {},
            active_tasks=len(generated_tasks),
            incidents=len(generated_incidents),
        )

    def aggregate_issues(self, month: int) -> ExecutiveIssueSummary:
        monthly_state = self.integration_service.simulate_month_full(month)
        company_kpis = monthly_state.get('pl', {}).get('kpis', {})
        issues = self.operational_service.detect_issues(monthly_state, company_kpis, month)

        issue_summary = [
            {
                'issue_id': issue.issue_id,
                'severity': issue.severity,
                'related_departments': next(
                    (
                        definition.related_departments
                        for definition in self.operational_service.load_issues_model().issues
                        if definition.id == issue.issue_id
                    ),
                    [],
                ),
            }
            for issue in issues
        ]

        return ExecutiveIssueSummary(month=month, issues=issue_summary)

    def aggregate_improvements(self, month: int) -> ExecutiveImprovementSummary:
        state = self.load_cycle_state()
        executed_actions = [action for action in state.executed_actions if action.month == month]

        return ExecutiveImprovementSummary(
            month=month,
            executed_actions=[action.model_dump() for action in executed_actions],
            updated_priorities=state.updated_priorities,
        )

    def aggregate_portfolio_summary(self, month: int) -> ExecutivePortfolioSummary:
        state = self.portfolio_service.simulate_portfolio_cycle(month)
        invest_targets = [d.business_unit_id for d in state.decisions if d.decision == 'Invest']
        reduce_targets = [d.business_unit_id for d in state.decisions if d.decision == 'Reduce']
        exit_candidates = [d.business_unit_id for d in state.decisions if d.decision == 'Exit']
        new_business_candidates = [d.business_unit_id for d in state.decisions if d.decision == 'NewBusiness']
        total_required_budget = float(sum(d.required_budget for d in state.decisions if d.decision in {'Invest', 'NewBusiness'}))
        cash_reserves = float(self.portfolio_service.corporate_service.load_fundamentals().financials.cash_reserves)

        return ExecutivePortfolioSummary(
            month=month,
            invest_targets=invest_targets,
            reduce_targets=reduce_targets,
            exit_candidates=exit_candidates,
            new_business_candidates=new_business_candidates,
            total_required_budget=round(total_required_budget, 3),
            remaining_budget=round(max(0.0, cash_reserves - total_required_budget), 3),
        )

    def forecast_next_month(self, month: int) -> Dict[str, object]:
        if month < 1 or month > 11:
            raise ValueError('month must be between 1 and 11 for forecast')

        with tempfile.TemporaryDirectory() as temp_dir:
            forecast_state_file = os.path.join(temp_dir, 'improvement_cycle_state.json')
            shutil.copyfile(self.state_file, forecast_state_file)
            forecast_service = ImprovementCycleService(data_path=temp_dir)
            return forecast_service.simulate_month_cycle(month)

    def aggregate_meeting_summary(self, month: int) -> ExecutiveMeetingSummary:
        state = self.meeting_service.load_latest_state_for_month(month)
        approved = sum(1 for d in state.decisions if d.decision == 'Approve')
        rejected = sum(1 for d in state.decisions if d.decision == 'Reject')
        modified = sum(1 for d in state.decisions if d.decision == 'Modify')
        held = sum(1 for d in state.decisions if d.decision == 'Hold')
        projection = state.next_month_projection
        highlight = f"Next month projection: revenue {projection.get('revenue', 0.0):.3f}, profit {projection.get('profit', 0.0):.3f}, margin {projection.get('profit_margin', 0.0):.3f}."

        return ExecutiveMeetingSummary(
            month=month,
            agenda_count=len(state.agenda),
            approved_count=approved,
            rejected_count=rejected,
            modified_count=modified,
            held_count=held,
            next_month_highlight=highlight,
        )

    def aggregate_organization_summary(self, month: int) -> ExecutiveOrganizationSummary:
        org_state = self.integration_service.organization_service.load_organization_state(month=month)
        unit_summaries = [
            ExecutiveOrganizationUnitSummary(
                name=unit.name,
                headcount=unit.headcount,
                workload_index=unit.workload_index,
                skill_highlights=[f"{skill}:{round(value, 3)}" for skill, value in unit.skill_profile.items()],
                open_positions=sum(1 for open_position in org_state.open_positions if open_position.unit_id == unit.id),
                monthly_personnel_cost=round(unit.headcount * unit.monthly_cost_per_fte, 3),
            )
            for unit in org_state.units
        ]

        return ExecutiveOrganizationSummary(units=unit_summaries)

    def aggregate_financial_summary(self, month: int) -> ExecutiveFinancialSummary:
        from .financial_service import FinancialService

        financial_service = FinancialService()
        financials = financial_service.load_financials()
        pending_requests = financial_service.load_pending_requests()

        return ExecutiveFinancialSummary(
            cash_reserves=financials.cash_reserves,
            free_cash_flow=financials.free_cash_flow,
            short_term_debt=financials.short_term_debt,
            long_term_debt=financials.long_term_debt,
            monthly_debt_service=financials.monthly_debt_service,
            available_credit_line=financials.available_credit_line,
            committed_capex=financials.committed_capex,
            liquidity_buffer_months=financials.liquidity_buffer_months,
            investment_requests_pending=[
                {
                    'id': request.id,
                    'business_unit_id': request.business_unit_id,
                    'requested_amount': request.requested_amount,
                    'expected_return_rate': request.expected_return_rate,
                    'payback_period_months': request.payback_period_months,
                    'strategic_priority': request.strategic_priority,
                    'requested_by': request.requested_by,
                    'requested_month': request.requested_month,
                    'tranche_count': request.tranche_count,
                    'tranche_interval_months': request.tranche_interval_months,
                }
                for request in pending_requests
            ],
            emergency_playbook=financial_service.generate_emergency_playbook(financials),
        )

    def aggregate_market_summary(self, month: int) -> ExecutiveMarketSummary:
        from .external_environment_service import ExternalEnvironmentService
        from .scenario_service import ScenarioService

        environment_service = ExternalEnvironmentService()
        scenario_service = ScenarioService()
        environment_state = environment_service.build_environment_state(month, 2026)

        market_segments = [
            ExecutiveMarketSegmentSummary(
                id=segment.id,
                name=segment.name,
                current_index=environment_state.get('market_index_by_segment', {}).get(segment.id, 1.0),
                growth_rate=segment.growth_rate,
                volatility=segment.volatility,
            )
            for segment in environment_service.load_external_environment().segments
        ]

        active_events = [
            ExecutiveMarketEventSummary(
                id=event['id'],
                type=event.get('type', ''),
                impact_map=event.get('impact_map', {}),
                duration_months=int(event.get('duration_months', 0)),
                source=event.get('source', ''),
                notes=event.get('notes', ''),
            )
            for event in environment_state.get('active_events', [])
        ]

        scenario_preview = scenario_service.get_last_preview()

        return ExecutiveMarketSummary(
            segments=market_segments,
            active_events=active_events,
            scenario_results_preview=scenario_preview if scenario_preview else None,
        )

    def build_dashboard(self, month: int, include_forecast: bool = False) -> ExecutiveDashboard:
        if month < 1 or month > 12:
            raise ValueError('month must be between 1 and 12')

        if month in self._dashboard_cache and not include_forecast:
            return self._dashboard_cache[month]

        narrative = None
        try:
            narrative = self.narrative_service.generate_monthly_narrative(month)
        except Exception:
            narrative = None

        fundamentals = self.portfolio_service.corporate_service.load_fundamentals()
        customer_segments = self.integration_service.company_service.build_customer_summary(fundamentals)

        dashboard = ExecutiveDashboard(
            month=month,
            pl=self.aggregate_pl(month),
            kpis=self.aggregate_kpis(month),
            operations=self.aggregate_operations(month),
            issues=self.aggregate_issues(month),
            improvements=self.aggregate_improvements(month),
            portfolio_summary=self.aggregate_portfolio_summary(month),
            meeting_summary=self.aggregate_meeting_summary(month),
            narrative_summary=(
                {
                    'story_highlights': [section.title for section in narrative.sections],
                    'sentiment': narrative.sentiment,
                    'key_drivers': narrative.key_drivers,
                    'risks': narrative.risks,
                    'opportunities': narrative.opportunities,
                }
                if narrative
                else None
            ),
            customer_summary=ExecutiveCustomerSummary(segments=[
                ExecutiveCustomerSegmentSummary(**segment)
                for segment in customer_segments
            ]),
            organization_summary=self.aggregate_organization_summary(month),
            financial_summary=self.aggregate_financial_summary(month),
            market_summary=self.aggregate_market_summary(month),
            forecast=self.forecast_next_month(month) if include_forecast else None,
        )

        if not include_forecast:
            self._dashboard_cache[month] = dashboard

        return dashboard

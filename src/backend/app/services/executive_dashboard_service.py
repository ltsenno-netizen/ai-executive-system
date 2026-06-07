import json
import os
import shutil
import tempfile
from typing import Dict, List, Optional

from ..models.executive_dashboard_model import (
    ExecutiveDashboard,
    ExecutiveCustomerSegmentSummary,
    ExecutiveCustomerSummary,
    ExecutiveExecutionSummary,
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
    ExecutiveMeetingTimelineItem,
    ExecutiveOrganizationSummary,
    ExecutiveOrganizationUnitSummary,
    ExternalEnvironmentSummary,
    MidTermPlanSummary,
    CeoPersonaSummary,
    CeoSuccessionSummary,
    CultureSummary,
    ReportSummary,
    QuarterlyReviewSummary,
    StrategyV2Summary,
    ExecutiveSimulationSummary,
)
from ..models.improvement_cycle_model import ContinuousImprovementState
from .business_portfolio_service import BusinessPortfolioService
from .company_operations_integration_service import CompanyOperationsIntegrationService
from .executive_meeting_service import ExecutiveMeetingService
from .scenario_simulation_service import ScenarioSimulationService
from .executive_narrative_service import ExecutiveNarrativeService
from .executive_report_service import ExecutiveReportService
from .improvement_cycle_service import ImprovementCycleService
from .execution_capacity_service import ExecutionCapacityService
from .mid_term_plan_service import MidTermPlanService
from .operational_issues_service import OperationalIssuesService
from .ceo_learning_service import CeoLearningService
from .quarterly_review_service import QuarterlyReviewService
from .ceo_succession_service import CeoSuccessionService
from .culture_service import CultureService
from .external_environment_service_v2 import ExternalEnvironmentServiceV2


class ExecutiveDashboardService:
    def __init__(self):
        self.integration_service = CompanyOperationsIntegrationService()
        self.operational_service = OperationalIssuesService()
        self.cycle_service = ImprovementCycleService()
        self.portfolio_service = BusinessPortfolioService()
        self.execution_service = ExecutionCapacityService()
        self.meeting_service = ExecutiveMeetingService()
        self.narrative_service = ExecutiveNarrativeService()
        self.report_service = ExecutiveReportService()
        self.plan_service = MidTermPlanService()
        self.ceo_learning_service = CeoLearningService()
        self.quarterly_review_service = QuarterlyReviewService()
        self.ceo_succession_service = CeoSuccessionService()
        self.culture_service = CultureService()
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

        selected_label = None
        risk_level = 'Medium'
        if state.selected_option_id == 'A':
            risk_level = 'High'
        elif state.selected_option_id == 'B':
            risk_level = 'Low'
        elif state.selected_option_id == 'C':
            risk_level = 'Medium'

        if state.decision_options:
            selected_option = next(
                (option for option in state.decision_options if option.id == state.selected_option_id),
                None,
            )
            if selected_option:
                selected_label = selected_option.label

        summary = ExecutiveMeetingSummary(
            month=month,
            agenda_count=len(state.agenda),
            approved_count=approved,
            rejected_count=rejected,
            modified_count=modified,
            held_count=held,
            next_month_highlight=highlight,
            selected_option_id=state.selected_option_id,
            selected_option_label=selected_label,
            ceo_selected_option_label=state.ceo_selected_option_label,
            ceo_decision_rationale=state.ceo_decision_rationale,
            decision_actor=state.decision_actor,
            meeting_risk_level=risk_level,
        )

        board = state.board_decision
        if board:
            summary.board_status = board.status
            summary.board_final_option_label = board.final_option_label
            summary.board_rationale = board.board_rationale
            summary.board_conditions = board.conditions
            summary.board_member_opinions = board.member_opinions
        else:
            summary.board_status = None
            summary.board_final_option_label = None
            summary.board_rationale = None
            summary.board_conditions = None
            summary.board_member_opinions = []

        return summary

    def aggregate_meeting_timeline(self, month: int, months: int = 6) -> List[ExecutiveMeetingTimelineItem]:
        timeline = []
        for offset in range(months - 1, -1, -1):
            target_month = month - offset
            if target_month < 1:
                continue
            try:
                state = self.meeting_service.load_latest_state_for_month(target_month)
            except Exception:
                continue

            approved = sum(1 for d in state.decisions if d.decision == 'Approve')
            rejected = sum(1 for d in state.decisions if d.decision == 'Reject')
            modified = sum(1 for d in state.decisions if d.decision == 'Modify')
            held = sum(1 for d in state.decisions if d.decision == 'Hold')
            projection = state.next_month_projection
            highlight = f"{target_month} → revenue {projection.get('revenue', 0.0):.3f}, profit {projection.get('profit', 0.0):.3f}."
            selected_label = None
            risk_level = 'Medium'
            if state.selected_option_id == 'A':
                risk_level = 'High'
            elif state.selected_option_id == 'B':
                risk_level = 'Low'
            elif state.selected_option_id == 'C':
                risk_level = 'Medium'
            if state.decision_options:
                selected_option = next(
                    (option for option in state.decision_options if option.id == state.selected_option_id),
                    None,
                )
                if selected_option:
                    selected_label = selected_option.label

            timeline.append(ExecutiveMeetingTimelineItem(
                month=target_month,
                selected_option_id=state.selected_option_id,
                selected_option_label=selected_label,
                approved_count=approved,
                rejected_count=rejected,
                modified_count=modified,
                held_count=held,
                next_month_highlight=highlight,
                meeting_risk_level=risk_level,
            ))
        return timeline

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

        simulation_summary = None
        try:
            simulation_service = ScenarioSimulationService()
            simulation_preview = simulation_service.get_latest_simulation_preview()
            if simulation_preview:
                simulation_summary = simulation_preview
        except Exception:
            simulation_summary = None

        return ExecutiveMarketSummary(
            segments=market_segments,
            active_events=active_events,
            scenario_results_preview=scenario_preview if scenario_preview else None,
            scenario_simulation_summary=simulation_summary,
        )

    def build_dashboard(self, month: int, include_forecast: bool = False) -> ExecutiveDashboard:
        if month < 1 or month > 12:
            raise ValueError('month must be between 1 and 12')

        if month in self._dashboard_cache and not include_forecast:
            return self._dashboard_cache[month]

        # Get latest quarterly review
        quarterly_review_summary = None
        try:
            latest_review = self.quarterly_review_service.get_latest_quarterly_review()
            if latest_review:
                quarterly_review_summary = QuarterlyReviewSummary(
                    quarter=latest_review.quarter,
                    revenue_total=latest_review.financial.revenue_total,
                    profit_total=latest_review.financial.operating_profit_total,
                    board_status=latest_review.board_review.status,
                    next_quarter_focus=latest_review.next_quarter_focus,
                )
        except Exception:
            quarterly_review_summary = None

        ceo_succession_summary = None
        try:
            latest_succession = self.ceo_succession_service.get_latest_succession_decision()
            if latest_succession:
                latest_persona = self.ceo_learning_service.get_latest_persona()
                if latest_persona:
                    ceo_succession_summary = CeoSuccessionSummary(
                        last_succession_period=latest_succession.period,
                        new_ceo_persona=CeoPersonaSummary(
                            aggressiveness=latest_persona.aggressiveness,
                            risk_tolerance=latest_persona.risk_tolerance,
                            brand_priority=latest_persona.brand_priority,
                            short_term_focus=latest_persona.short_term_focus,
                            long_term_focus=latest_persona.long_term_focus,
                        ),
                        rationale=latest_succession.rationale,
                    )
        except Exception:
            ceo_succession_summary = None

        narrative = None
        try:
            narrative = self.narrative_service.generate_monthly_narrative(month)
        except Exception:
            narrative = None

        fundamentals = self.portfolio_service.corporate_service.load_fundamentals()
        customer_segments = self.integration_service.company_service.build_customer_summary(fundamentals)

        latest_narrative = None
        try:
            latest_narrative = self.narrative_service.get_latest_narrative()
        except Exception:
            pass

        latest_report = None
        report_history = []
        try:
            latest_report = self.report_service.get_latest_report()
            report_history = self.report_service.list_reports(limit=6)
        except Exception:
            latest_report = None
            report_history = []

        latest_plan_summary = None
        try:
            latest_plan = self.plan_service.get_latest_plan()
            if latest_plan:
                latest_plan_summary = MidTermPlanSummary(
                    start_year=latest_plan.start_year,
                    end_year=latest_plan.end_year,
                    vision=latest_plan.vision,
                    board_approved=latest_plan.board_approved,
                )
        except Exception:
            latest_plan_summary = None

        ceo_persona_summary = None
        try:
            persona = self.ceo_learning_service.get_latest_persona()
            if persona:
                ceo_persona_summary = CeoPersonaSummary(
                    aggressiveness=persona.aggressiveness,
                    risk_tolerance=persona.risk_tolerance,
                    brand_priority=persona.brand_priority,
                    short_term_focus=persona.short_term_focus,
                    long_term_focus=persona.long_term_focus,
                )
        except Exception:
            ceo_persona_summary = None

        culture_summary = None
        try:
            latest_culture = self.culture_service.get_latest_culture()
            if latest_culture:
                culture_summary = CultureSummary(
                    aggressiveness=latest_culture.aggressiveness_culture,
                    risk_aversion=latest_culture.risk_aversion_culture,
                    brand=latest_culture.brand_culture,
                    cost=latest_culture.cost_culture,
                    people=latest_culture.people_culture,
                    execution=latest_culture.execution_culture,
                    innovation=latest_culture.innovation_culture,
                    stability=latest_culture.stability_culture,
                )
        except Exception:
            culture_summary = None

        environment_summary = None
        try:
            env_service = ExternalEnvironmentServiceV2()
            period = f"2026-{month:02d}"
            latest_env = env_service.get_environment(period)
            if latest_env:
                environment_summary = ExternalEnvironmentSummary(
                    economic=latest_env.pest.economic,
                    competitor_pressure=sum(c.aggressiveness for c in latest_env.competitors),
                    shock_summary=[s.shock_type for s in latest_env.shocks],
                )
        except Exception:
            environment_summary = None

        dashboard = ExecutiveDashboard(
            month=month,
            pl=self.aggregate_pl(month),
            kpis=self.aggregate_kpis(month),
            operations=self.aggregate_operations(month),
            issues=self.aggregate_issues(month),
            improvements=self.aggregate_improvements(month),
            portfolio_summary=self.aggregate_portfolio_summary(month),
            meeting=self.aggregate_meeting_summary(month),
            meeting_timeline=self.aggregate_meeting_timeline(month),
            mid_term_plan_summary=latest_plan_summary,
            ceo_persona=ceo_persona_summary,
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
            latest_narrative_period=latest_narrative.period if latest_narrative else None,
            latest_narrative_summary=(
                latest_narrative.summary
                if latest_narrative and hasattr(latest_narrative, 'summary')
                else (
                    ' '.join(section.title + ': ' + section.content for section in getattr(latest_narrative, 'sections', []))
                    if latest_narrative
                    else None
                )
            ),
            latest_report_period=latest_report.period if latest_report else None,
            latest_report_title=latest_report.title if latest_report else None,
            latest_report_summary=latest_report.management_summary[:200] if latest_report else None,
            reports=[
                ReportSummary(
                    period=report['period'],
                    title=report['title'],
                    summary=report.get('summary', '')[:100],
                )
                for report in report_history
            ],
            customer_summary=ExecutiveCustomerSummary(segments=[
                ExecutiveCustomerSegmentSummary(**segment)
                for segment in customer_segments
            ]),
            organization_summary=self.aggregate_organization_summary(month),
            financial_summary=self.aggregate_financial_summary(month),
            quarterly_review=quarterly_review_summary,
            ceo_succession=ceo_succession_summary,
            culture=culture_summary,
            environment=environment_summary,
            execution_summary=self.aggregate_execution_summary(month),
            market_summary=self.aggregate_market_summary(month),
            forecast=self.forecast_next_month(month) if include_forecast else None,
            corporate_memory_summary=self.aggregate_corporate_memory_summary(),
            strategy_v2_summary=self._aggregate_strategy_v2_summary(),
            multi_company_comparison_summary=self._aggregate_multi_company_comparison_summary(),
            executive_simulation_summary=self._aggregate_executive_simulation_summary(),
        )

        if not include_forecast:
            self._dashboard_cache[month] = dashboard

        return dashboard

    def _aggregate_multi_company_comparison_summary(self):
        """Get multi-company comparison summary if available."""
        try:
            # Delayed import to avoid circular dependency
            from .multi_company_comparative_service import MultiCompanyComparativeService
            multi_service = MultiCompanyComparativeService()
            report = multi_service.get_last_comparison()
            if report is None:
                return None
            
            # Convert to summary format
            all_scores = {}
            for metric in report.metrics:
                for company_id, value in metric.values.items():
                    if company_id not in all_scores:
                        all_scores[company_id] = []
                    all_scores[company_id].append(value)
            
            avg_scores = {cid: sum(scores) / len(scores) for cid, scores in all_scores.items()}
            strongest = max(avg_scores, key=avg_scores.get) if avg_scores else None
            weakest = min(avg_scores, key=avg_scores.get) if avg_scores else None
            
            cluster_dict = {c.cluster_name: c.company_ids for c in report.clusters}
            
            from ..models.multi_company_comparative_model import MultiCompanyComparisonSummary
            return MultiCompanyComparisonSummary(
                companies=[c.name for c in report.companies],
                strongest_company=strongest,
                weakest_company=weakest,
                cluster_count=len(report.clusters),
                cluster_labels=cluster_dict,
                key_insight=report.narrative_summary.split("\n")[0] if report.narrative_summary else "No insights",
                last_compared=report.comparison_date,
            )
        except Exception:
            return None

    def _aggregate_executive_simulation_summary(self):
        """Get the latest executive simulation summary."""
        try:
            from .executive_simulation_service import ExecutiveSimulationService
            from ..models.executive_simulation_model import ExecutiveStance

            simulation_service = ExecutiveSimulationService()
            simulation = simulation_service.get_latest()
            if simulation is None:
                return None

            opposed_roles = [
                v.role.value for v in simulation.votes
                if v.stance in {ExecutiveStance.CONCERNED, ExecutiveStance.OPPOSE}
            ]

            return ExecutiveSimulationSummary(
                last_simulation_id=simulation.simulation_id,
                scenario_type=simulation.scenario_type,
                consensus_level=simulation.consensus_level,
                approved=simulation.approved,
                key_roles_opposed=opposed_roles,
                last_run_at=simulation.timestamp,
            )
        except Exception:
            return None

    def _aggregate_enterprise_autopilot_summary(self):
        """Get the latest enterprise autopilot cycle summary."""
        try:
            from .enterprise_autopilot_service import EnterpriseAutopilotService
            from ..models.enterprise_autopilot_model import AutopilotSummary

            autopilot_service = EnterpriseAutopilotService()
            cycle = autopilot_service.get_latest_cycle()
            if cycle is None:
                return None

            success_rate = 0.0
            if cycle.phases:
                success_rate = sum(1 for phase in cycle.phases if phase.succeeded) / len(cycle.phases)

            return AutopilotSummary(
                last_cycle_id=cycle.cycle_id,
                last_run_at=cycle.completed_at,
                overall_status=cycle.overall_status,
                latest_summary=cycle.summary,
                recent_actions=cycle.key_actions[:3],
                next_focus=[phase.phase.value for phase in cycle.phases if not phase.succeeded][:3],
                average_phase_success_rate=success_rate,
            )
        except Exception:
            return None
        """Get the latest enterprise autopilot cycle summary."""
        try:
            from .enterprise_autopilot_service import EnterpriseAutopilotService
            from ..models.enterprise_autopilot_model import AutopilotSummary

            autopilot_service = EnterpriseAutopilotService()
            cycle = autopilot_service.get_latest_cycle()
            if cycle is None:
                return None

            success_rate = 0.0
            if cycle.phases:
                success_rate = sum(1 for phase in cycle.phases if phase.succeeded) / len(cycle.phases)

            return AutopilotSummary(
                last_cycle_id=cycle.cycle_id,
                last_run_at=cycle.completed_at,
                overall_status=cycle.overall_status,
                latest_summary=cycle.summary,
                recent_actions=cycle.key_actions[:3],
                next_focus=[phase.phase.value for phase in cycle.phases if not phase.succeeded][:3],
                average_phase_success_rate=success_rate,
            )
        except Exception:
            return None

    def _aggregate_strategy_v2_summary(self):
        """Get the latest Strategy Engine V2 summary if available."""
        try:
            from .strategy_engine_v2_service import StrategyEngineV2Service
            strategy_service = StrategyEngineV2Service()
            report = strategy_service.get_latest_report()
            if report is None:
                return None

            return StrategyV2Summary(
                scenario_type=report.scenario_type.value,
                alignment_score=report.alignment_score,
                risk_resilience_score=report.risk_resilience_score,
                frontier_health_score=report.frontier_health_score,
                recommended_actions=report.recommended_actions[:3],
                top_directives=[directive.name for directive in report.strategy_directives[:3]],
                executive_summary=report.executive_summary,
                generated_at=report.generated_at,
            )
        except Exception:
            return None

    def aggregate_execution_summary(self, month: int) -> ExecutiveExecutionSummary:
        state = self.execution_service.get_current_state()
        return ExecutiveExecutionSummary(
            capacity=state.get('capacity', 0.0),
            load=state.get('load', 0.0),
            efficiency=state.get('efficiency', 0.0),
            execution_capacity_score=state.get('execution_capacity_score', 0.0),
            forecast=self.execution_service.forecast_next_months(3),
        )

    def aggregate_corporate_memory_summary(self):
        """Aggregate corporate memory summary for the dashboard."""
        try:
            from .corporate_memory_service import CorporateMemoryService
            memory_service = CorporateMemoryService()
            return memory_service.get_memory_summary(max_recent=5, max_critical=3)
        except Exception:
            return None

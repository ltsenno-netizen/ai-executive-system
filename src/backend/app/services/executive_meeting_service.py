import json
import os
from copy import deepcopy
from typing import Dict, List, Optional

from ..models.executive_meeting_model import (
    DecisionOption,
    ExecutiveAgent,
    ExecutiveDebateSummary,
    ExecutiveMeetingState,
    MeetingAgendaItem,
    MeetingDecision,
    MeetingMinutes,
)
from .ai_ceo_agent import AICeoAgent
from .business_portfolio_service import BusinessPortfolioService
from .company_operations_integration_service import CompanyOperationsIntegrationService
from .external_environment_service_v2 import ExternalEnvironmentServiceV2
from .executive_meeting_engine import ExecutiveMeetingEngine
from .improvement_cycle_service import ImprovementCycleService
from .operational_issues_service import OperationalIssuesService


class ExecutiveMeetingService:
    def __init__(self):
        self.data_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), '../../../../data/samples')
        )
        self.state_file = os.path.join(self.data_path, 'executive_meeting_state.json')
        self.integration_service = CompanyOperationsIntegrationService()
        self.issues_service = OperationalIssuesService()
        self.improvement_service = ImprovementCycleService()
        self.portfolio_service = BusinessPortfolioService()
        self.engine = ExecutiveMeetingEngine()

    def save_meeting_state(self, state: ExecutiveMeetingState) -> None:
        with open(self.state_file, 'w', encoding='utf-8') as f:
            f.write(state.model_dump_json(indent=2, ensure_ascii=False))

    def load_meeting_state(self) -> ExecutiveMeetingState:
        if not os.path.exists(self.state_file):
            raise FileNotFoundError(f'Executive meeting state not found: {self.state_file}')

        with open(self.state_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        return ExecutiveMeetingState(**data)

    def build_meeting_agenda(self, month: int) -> List[MeetingAgendaItem]:
        if month < 1 or month > 12:
            raise ValueError('month must be between 1 and 12')

        monthly_state = self.integration_service.simulate_month_full(month)
        pl = monthly_state.get('pl', {})
        kpis = pl.get('kpis', {})
        operations = monthly_state.get('operations', {})
        issues = self.issues_service.detect_issues(monthly_state, kpis, month)
        improvements = self.issues_service.generate_recommendations(issues)
        portfolio_state = self.portfolio_service.simulate_portfolio_cycle(month)

        agenda = []
        agenda.append(MeetingAgendaItem(
            id=f'{month}-pl',
            category='PL',
            title='PL Summary',
            summary=f"Revenue {sum(pl.get('revenue', {}).values()):.3f}, Profit {float(pl.get('profit', 0.0)):.3f}, Margin {float(pl.get('profit_margin', 0.0)):.3f}",
            ai_recommendation='Maintain margin focus and validate cost discipline while monitoring revenue mix.',
            impact={
                'revenue': sum(pl.get('revenue', {}).values()),
                'profit': float(pl.get('profit', 0.0)),
                'profit_margin': float(pl.get('profit_margin', 0.0)),
            },
        ))
        agenda.append(MeetingAgendaItem(
            id=f'{month}-kpi',
            category='KPI',
            title='KPI Summary',
            summary=f"License {kpis.get('license_ratio', 0.0):.3f}, Digital {kpis.get('digital_ratio', 0.0):.3f}, Talent LTV {kpis.get('talent_ltv_index', 0.0):.3f}",
            ai_recommendation='Ensure KPI trajectory is aligned with margin priorities and highlight digital acceleration opportunities.',
            impact={
                'license_ratio': float(kpis.get('license_ratio', 0.0)),
                'digital_ratio': float(kpis.get('digital_ratio', 0.0)),
                'talent_ltv_index': float(kpis.get('talent_ltv_index', 0.0)),
            },
        ))
        agenda.append(MeetingAgendaItem(
            id=f'{month}-ops',
            category='Operations',
            title='Operations Summary',
            summary=f"Active tasks {len(operations.get('generated_tasks', []))}, incidents {len(operations.get('generated_incidents', []))}",
            ai_recommendation='Focus on operational resilience and convert issue recommendations into clear execution steps.',
            impact={
                'active_tasks': float(len(operations.get('generated_tasks', []))),
                'incidents': float(len(operations.get('generated_incidents', []))),
            },
        ))
        agenda.append(MeetingAgendaItem(
            id=f'{month}-issues',
            category='Issues',
            title='Issues Summary',
            summary=f"Detected {len(issues)} issue(s); recommend prioritizing top corrective actions.",
            ai_recommendation='Approve high-impact issue resolutions and defer low-value items after assessing resource tradeoffs.',
            impact={
                'issue_count': float(len(issues)),
                'recommended_actions': float(len(improvements)),
            },
        ))
        agenda.append(MeetingAgendaItem(
            id=f'{month}-improvements',
            category='Improvements',
            title='Improvement Actions',
            summary=f"Prepared {len(improvements)} improvement actions to address detected issues.",
            ai_recommendation='Approve the most impactful actions with measurable KPI effects and track execution progress.',
            impact={
                'improvement_actions': float(len(improvements)),
            },
        ))

        portfolio_decisions = ', '.join({d.decision for d in portfolio_state.decisions}) or 'No decisions generated.'
        agenda.append(MeetingAgendaItem(
            id=f'{month}-portfolio',
            category='Portfolio',
            title='Portfolio Decisions',
            summary=f"Portfolio actions: {portfolio_decisions}",
            ai_recommendation='Prioritize investments in high-growth digital and maintain stable license businesses while exiting high-risk low-growth units.',
            impact={
                'invest_targets': float(len([d for d in portfolio_state.decisions if d.decision == 'Invest'])),
                'exit_candidates': float(len([d for d in portfolio_state.decisions if d.decision == 'Exit'])),
            },
        ))

        return agenda

    def build_executive_agents(self, agenda: List[MeetingAgendaItem]) -> List[ExecutiveAgent]:
        return self.engine.generate_executive_agents(agenda)

    def run_executive_debate(self, agenda: List[MeetingAgendaItem], agents: List[ExecutiveAgent]) -> ExecutiveDebateSummary:
        return self.engine.run_strategic_debate(agenda, agents)

    def generate_decision_options(self, agenda: List[MeetingAgendaItem]) -> List[DecisionOption]:
        return self.engine.generate_decision_options(agenda)

    def _derive_decisions_from_option(self, option_id: str, agenda: List[MeetingAgendaItem]) -> List[Dict[str, object]]:
        mapped_decisions = []
        for item in agenda:
            if option_id == 'A':
                if item.category in {'Portfolio', 'PL', 'Improvements'}:
                    decision = 'Approve'
                elif item.category == 'Operations':
                    decision = 'Modify'
                else:
                    decision = 'Approve'
            elif option_id == 'B':
                if item.category in {'Portfolio', 'Improvements'}:
                    decision = 'Hold'
                elif item.category == 'Operations':
                    decision = 'Reject'
                else:
                    decision = 'Reject'
            else:
                if item.category in {'Portfolio', 'Operations'}:
                    decision = 'Modify'
                elif item.category == 'Improvements':
                    decision = 'Approve'
                else:
                    decision = 'Approve'

            comment_map = {
                'Approve': 'Approved by the executive team for next-month implementation.',
                'Modify': 'Approved with adjustments to reduce risk and improve execution.',
                'Reject': 'Not approved at this time due to strategic or capacity concerns.',
                'Hold': 'Deferred to the next meeting pending additional analysis.',
            }
            mapped_decisions.append({
                'agenda_id': item.id,
                'decision': decision,
                'comment': comment_map.get(decision, ''),
            })

        return mapped_decisions

    def apply_decision_option(self, option_id: str, month: int, ceo_comment: str | None = None) -> List[MeetingDecision]:
        agenda = self.build_meeting_agenda(month)
        selected_decisions = self._derive_decisions_from_option(option_id, agenda)
        applied_decisions = self.apply_decisions_to_system(selected_decisions, month)
        for decision in applied_decisions:
            if ceo_comment:
                decision.comment += f' CEO comment: {ceo_comment}'
        return applied_decisions

    def _transform_decision(self, item: MeetingAgendaItem, decision: str) -> Dict[str, float]:
        factor = 0.0
        if decision == 'Approve':
            factor = 1.0
        elif decision == 'Modify':
            factor = 0.8
        elif decision == 'Reject':
            factor = 0.0
        elif decision == 'Hold':
            factor = 0.0

        return {key: round(value * factor, 4) for key, value in item.impact.items()}

    def apply_decisions_to_system(self, decisions: List[Dict[str, object]], month: int) -> List[MeetingDecision]:
        agenda = {item.id: item for item in self.build_meeting_agenda(month)}
        applied_decisions: List[MeetingDecision] = []

        for decision_data in decisions:
            agenda_id = decision_data.get('agenda_id', '')
            decision_type = decision_data.get('decision', 'Hold')
            comment = decision_data.get('comment', '')
            agenda_item = agenda.get(agenda_id)
            if agenda_item is None:
                continue

            applied_effect = self._transform_decision(agenda_item, decision_type)
            if decision_type == 'Modify':
                comment = comment or 'Modified to a reduced scope; 80% of recommended effect is applied.'
            elif decision_type == 'Reject':
                comment = comment or 'Rejected by management; no effect will be applied.'
            elif decision_type == 'Hold':
                comment = comment or 'Deferred to the next meeting; no action is applied this cycle.'
            elif decision_type == 'Approve':
                comment = comment or 'Approved by management; applied effect will be reflected in next month projection.'

            applied_decisions.append(MeetingDecision(
                agenda_id=agenda_id,
                decision=decision_type,
                comment=comment,
                applied_effect=applied_effect,
            ))

        return applied_decisions

    def project_next_month_after_meeting(self, month: int, applied_decisions: List[MeetingDecision]) -> Dict[str, float]:
        next_month = month + 1
        if next_month > 12:
            next_month = month

        next_state = self.integration_service.simulate_month_full(next_month)
        pl = next_state.get('pl', {})
        base_revenue = sum(pl.get('revenue', {}).values())
        base_profit = float(pl.get('profit', 0.0))
        base_kpis = {k: float(v) for k, v in pl.get('kpis', {}).items()}

        revenue_delta = sum(decision.applied_effect.get('revenue', 0.0) for decision in applied_decisions)
        profit_delta = sum(decision.applied_effect.get('profit', 0.0) for decision in applied_decisions)
        predicted_revenue = round(base_revenue + revenue_delta, 3)
        predicted_profit = round(base_profit + profit_delta, 3)
        predicted_profit_margin = round((predicted_profit / predicted_revenue) if predicted_revenue else 0.0, 4)

        predicted_kpis = deepcopy(base_kpis)
        for decision in applied_decisions:
            for key, value in decision.applied_effect.items():
                if key in predicted_kpis:
                    predicted_kpis[key] = round(predicted_kpis.get(key, 0.0) + value, 4)

        return {
            'month': next_month,
            'revenue': predicted_revenue,
            'profit': predicted_profit,
            'profit_margin': predicted_profit_margin,
            **predicted_kpis,
        }

    def _build_execution_state(self, org_state: Dict[str, object]) -> Dict[str, object]:
        units = org_state.get('units', [])
        if not isinstance(units, list) or not units:
            return {'capacity': 1.0, 'load': 0.0, 'efficiency': 1.0}

        workload_values = [unit.get('workload_index', 0.0) for unit in units if isinstance(unit, dict)]
        avg_workload = float(sum(workload_values) / len(workload_values)) if workload_values else 0.0
        return {
            'capacity': max(0.0, 1.2 - avg_workload),
            'load': avg_workload,
            'efficiency': max(0.0, 1.0 - avg_workload * 0.2),
        }

    def simulate_executive_meeting(self, month: int, decisions: List[Dict[str, object]] = None) -> ExecutiveMeetingState:
        if month < 1 or month > 12:
            raise ValueError('month must be between 1 and 12')

        if not decisions:
            return self.simulate_executive_meeting_with_ai_ceo(month)

        agenda = self.build_meeting_agenda(month)
        applied_decisions = self.apply_decisions_to_system(decisions or [], month)
        executive_agents = self.build_executive_agents(agenda)
        debate_summary = self.run_executive_debate(agenda, executive_agents)
        decision_options = self.generate_decision_options(agenda)
        meeting_minutes = self.engine.compile_meeting_minutes(
            month=month,
            agenda=agenda,
            debate_summary=debate_summary,
            decisions=[decision.model_dump() for decision in applied_decisions],
        )
        next_month_projection = self.project_next_month_after_meeting(month, applied_decisions)

        state = ExecutiveMeetingState(
            month=month,
            agenda=agenda,
            decisions=applied_decisions,
            next_month_projection=next_month_projection,
            executive_agents=executive_agents,
            debate_summary=debate_summary,
            decision_options=decision_options,
            meeting_minutes=meeting_minutes,
        )

        self.save_meeting_state(state)
        try:
            from .executive_narrative_service import ExecutiveNarrativeService

            monthly_state = self.integration_service.simulate_month_full(month)
            market_state = monthly_state.get('environment', {})
            financials = monthly_state.get('financials', {})
            org_state = self.integration_service.organization_service.load_organization_state(month=month)
            if hasattr(org_state, 'model_dump'):
                org_state = org_state.model_dump()
            narrative_service = ExecutiveNarrativeService()
            narrative = narrative_service.generate_and_store_narrative(
                period=f"2026-{month:02d}",
                financials=financials,
                market_state=market_state,
                org_state=org_state,
                meeting_state=state.model_dump(),
            )
            self.integration_service.store_executive_report(
                period=f"2026-{month:02d}",
                narrative=narrative,
                financials=financials,
                market_state=market_state,
                org_state=org_state,
                meeting_state=state.model_dump(),
            )
        except Exception:
            pass

        return state

    def simulate_executive_meeting_with_option(
        self,
        month: int,
        option_id: str,
        ceo_comment: str | None = None,
    ) -> ExecutiveMeetingState:
        if month < 1 or month > 12:
            raise ValueError('month must be between 1 and 12')

        agenda = self.build_meeting_agenda(month)
        executive_agents = self.build_executive_agents(agenda)
        debate_summary = self.run_executive_debate(agenda, executive_agents)
        decision_options = self.generate_decision_options(agenda)
        applied_decisions = self.apply_decision_option(option_id, month, ceo_comment)
        meeting_minutes = self.engine.compile_meeting_minutes(
            month=month,
            agenda=agenda,
            debate_summary=debate_summary,
            decisions=[decision.model_dump() for decision in applied_decisions],
            selected_option_id=option_id,
            ceo_comment=ceo_comment,
        )
        next_month_projection = self.project_next_month_after_meeting(month, applied_decisions)

        state = ExecutiveMeetingState(
            month=month,
            agenda=agenda,
            decisions=applied_decisions,
            next_month_projection=next_month_projection,
            executive_agents=executive_agents,
            debate_summary=debate_summary,
            decision_options=decision_options,
            meeting_minutes=meeting_minutes,
            selected_option_id=option_id,
            ceo_comment=ceo_comment,
        )

        self.save_meeting_state(state)
        try:
            from .executive_narrative_service import ExecutiveNarrativeService

            monthly_state = self.integration_service.simulate_month_full(month)
            market_state = monthly_state.get('environment', {})
            financials = monthly_state.get('financials', {})
            org_state = self.integration_service.organization_service.load_organization_state(month=month)
            if hasattr(org_state, 'model_dump'):
                org_state = org_state.model_dump()
            narrative_service = ExecutiveNarrativeService()
            narrative = narrative_service.generate_and_store_narrative(
                period=f"2026-{month:02d}",
                financials=financials,
                market_state=market_state,
                org_state=org_state,
                meeting_state=state.model_dump(),
            )
            self.integration_service.store_executive_report(
                period=f"2026-{month:02d}",
                narrative=narrative,
                financials=financials,
                market_state=market_state,
                org_state=org_state,
                meeting_state=state.model_dump(),
            )
        except Exception:
            pass

        return state

    def simulate_executive_meeting_with_ai_ceo(
        self,
        month: int,
        ceo_comment: str | None = None,
    ) -> ExecutiveMeetingState:
        if month < 1 or month > 12:
            raise ValueError('month must be between 1 and 12')

        agenda = self.build_meeting_agenda(month)
        executive_agents = self.build_executive_agents(agenda)
        debate_summary = self.run_executive_debate(agenda, executive_agents)
        decision_options = self.generate_decision_options(agenda)

        env_service = ExternalEnvironmentServiceV2()
        period = f"2026-{month:02d}"
        environment = env_service.get_environment(period)
        if environment is None:
            environment = env_service.generate_and_store_environment(period)

        monthly_state = self.integration_service.simulate_month_full(month, environment_state=environment.model_dump())
        market_state = monthly_state.get('environment', {})
        financials = monthly_state.get('financials', {})
        org_state = self.integration_service.organization_service.load_organization_state(month=month)
        if hasattr(org_state, 'model_dump'):
            org_state = org_state.model_dump()

        execution_state = self._build_execution_state(org_state)
        selected_option, rationale, ceo_persona = self.engine.select_ceo_option(
            decision_options,
            financials,
            market_state,
            org_state,
            execution_state,
            environment=environment,
        )

        board_decision = self.engine.review_board_decision(
            ceo_option=selected_option,
            ceo_rationale=rationale,
            options=decision_options,
            financials=financials,
            market_state=market_state,
            org_state=org_state,
            ceo_persona=ceo_persona,
            environment=monthly_state.get('environment'),
        )

        final_option_id = board_decision.final_option_id
        final_option = next(
            (opt for opt in decision_options if opt.id == final_option_id),
            selected_option,
        )

        applied_decisions = self.apply_decision_option(final_option.id, month, ceo_comment)
        meeting_minutes = self.engine.compile_meeting_minutes(
            month=month,
            agenda=agenda,
            debate_summary=debate_summary,
            decisions=[decision.model_dump() for decision in applied_decisions],
            selected_option_id=final_option.id,
            ceo_comment=ceo_comment,
        )
        next_month_projection = self.project_next_month_after_meeting(month, applied_decisions)

        state = ExecutiveMeetingState(
            month=month,
            agenda=agenda,
            decisions=applied_decisions,
            next_month_projection=next_month_projection,
            executive_agents=executive_agents,
            debate_summary=debate_summary,
            decision_options=decision_options,
            meeting_minutes=meeting_minutes,
            selected_option_id=final_option.id,
            ceo_comment=ceo_comment,
            ceo_selected_option_id=selected_option.id,
            ceo_selected_option_label=selected_option.label,
            ceo_decision_rationale=rationale,
            ceo_persona=ceo_persona.model_dump(),
            board_decision=board_decision,
            decision_actor='AI CEO + Board',
        )

        self.save_meeting_state(state)
        try:
            from .executive_narrative_service import ExecutiveNarrativeService

            narrative_service = ExecutiveNarrativeService()
            narrative = narrative_service.generate_and_store_narrative(
                period=f"2026-{month:02d}",
                financials=financials,
                market_state=market_state,
                org_state=org_state,
                meeting_state=state.model_dump(),
            )
            self.integration_service.store_executive_report(
                period=f"2026-{month:02d}",
                narrative=narrative,
                financials=financials,
                market_state=market_state,
                org_state=org_state,
                meeting_state=state.model_dump(),
            )
        except Exception:
            pass

        return state

    def load_latest_state_for_month(self, month: int) -> ExecutiveMeetingState:
        try:
            state = self.load_meeting_state()
            if state.month == month:
                return state
        except FileNotFoundError:
            pass

        return self.simulate_executive_meeting_with_ai_ceo(month)

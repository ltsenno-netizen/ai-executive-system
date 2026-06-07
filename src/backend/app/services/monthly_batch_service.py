from typing import Dict, List, Optional, Tuple

from pydantic import BaseModel, Field

from .company_operations_integration_service import CompanyOperationsIntegrationService
from .executive_dashboard_service import ExecutiveDashboardService
from .executive_meeting_service import ExecutiveMeetingService
from .executive_narrative_service import ExecutiveNarrativeService
from .executive_report_service import ExecutiveReportService
from .ceo_learning_service import CeoLearningService
from .ceo_succession_service import CeoSuccessionService
from .culture_service import CultureService
from .external_environment_service_v2 import ExternalEnvironmentServiceV2


class MonthlyBatchResult(BaseModel):
    period: str
    simulation_ok: bool = False
    meeting_ok: bool = False
    narrative_ok: bool = False
    report_ok: bool = False
    ceo_learning_ok: bool = False
    succession_ok: bool = False
    culture_ok: bool = False
    errors: List[str] = Field(default_factory=list)


class MonthlyBatchService:
    def __init__(self):
        self.integration_service = CompanyOperationsIntegrationService()
        self.meeting_service = ExecutiveMeetingService()
        self.narrative_service = ExecutiveNarrativeService()
        self.report_service = ExecutiveReportService()
        self.dashboard_service = ExecutiveDashboardService()
        self.ceo_learning_service = CeoLearningService()
        self.ceo_succession_service = CeoSuccessionService()
        self.culture_service = CultureService()
        self.environment_service = ExternalEnvironmentServiceV2()

    def _parse_period(self, period: str) -> Tuple[int, int]:
        if not isinstance(period, str):
            raise ValueError('period must be a string in YYYY-MM format')

        parts = period.split('-')
        if len(parts) != 2:
            raise ValueError('period must be a string in YYYY-MM format')

        year = int(parts[0])
        month = int(parts[1])
        if month < 1 or month > 12:
            raise ValueError('month must be between 1 and 12')
        return year, month

    def _format_period(self, year: int, month: int) -> str:
        return f"{year:04d}-{month:02d}"

    def _next_period(self, period: str) -> str:
        year, month = self._parse_period(period)
        month += 1
        if month > 12:
            year += 1
            month = 1
        return self._format_period(year, month)

    def _build_meeting_state(
        self,
        agenda: List[Dict[str, object]],
        decision_options: List[Dict[str, object]],
        applied_decisions: List[object],
    ) -> Dict[str, object]:
        return {
            'selected_option_id': 'A',
            'agenda': [item.model_dump() if hasattr(item, 'model_dump') else item for item in agenda],
            'decision_options': decision_options,
            'decisions': [
                decision.model_dump() if hasattr(decision, 'model_dump') else decision
                for decision in applied_decisions
            ],
        }

    def run_monthly_cycle(self, period: str) -> MonthlyBatchResult:
        result = MonthlyBatchResult(period=period)

        try:
            year, month = self._parse_period(period)

            environment = self.environment_service.generate_and_store_environment(period)
            monthly_state = self.integration_service.simulate_month_full(
                month,
                year=year,
                environment_state=environment.model_dump(),
            )
            result.simulation_ok = True

            agenda = self.meeting_service.build_meeting_agenda(month)
            decision_options = self.meeting_service.generate_decision_options(agenda)
            applied_decisions = self.meeting_service.apply_decision_option('A', month)
            result.meeting_ok = True

            meeting_state = self._build_meeting_state(agenda, decision_options, applied_decisions)
            org_state = self.integration_service.organization_service.load_organization_state(month=month)

            narrative = self.narrative_service.generate_and_store_narrative(
                period,
                monthly_state.get('financials', {}),
                monthly_state.get('environment', {}),
                org_state,
                meeting_state,
            )
            result.narrative_ok = True

            self.report_service.generate_and_store_report(
                period,
                narrative,
                monthly_state.get('environment', {}),
                org_state,
                meeting_state,
            )
            result.report_ok = True

            self.dashboard_service.build_dashboard(month)

            current_persona = self.ceo_learning_service.get_latest_persona() or self.ceo_learning_service._get_base_persona()
            if self._should_trigger_succession(period, current_persona, monthly_state, org_state, meeting_state):
                self.ceo_succession_service.run_ceo_succession(
                    period,
                    current_financials=monthly_state.get('financials', {}),
                    market_state=monthly_state.get('environment', {}),
                    org_state=org_state,
                )
                result.succession_ok = True
                result.ceo_learning_ok = True
            else:
                self.ceo_learning_service.update_and_store_ceo_persona(period)
            result.ceo_learning_ok = True

            # 企業文化を更新
            self.culture_service.update_and_store_culture(period, environment=environment)
            result.culture_ok = True

        except Exception as exc:
            result.errors.append(str(exc))

        return result

    def run_multi_month_cycle(self, start_period: str, months: int) -> List[MonthlyBatchResult]:
        if months < 1:
            raise ValueError('months must be 1 or greater')

        results: List[MonthlyBatchResult] = []
        current_period = start_period
        for _ in range(months):
            results.append(self.run_monthly_cycle(current_period))
            current_period = self._next_period(current_period)

        return results

    def _should_trigger_succession(
        self,
        period: str,
        current_persona,
        monthly_state: Dict[str, object],
        org_state: Dict[str, object],
        meeting_state: Dict[str, object],
    ) -> bool:
        financials = monthly_state.get('financials', {})
        cash_balance = float(financials.get('cash_balance', 0.0))
        operating_profit = float(financials.get('operating_profit', 0.0))

        # 任期満了の想定（3年=36ヶ月）
        try:
            year, month = map(int, period.split('-'))
            if month % 12 == 0 and (year % 3) == 0:
                return True
        except Exception:
            pass

        # 財務悪化時
        if operating_profit < 0 or cash_balance < 1.0:
            return True

        # CEO persona が極端に偏っている場合
        if (
            current_persona.aggressiveness >= 0.9
            or current_persona.risk_tolerance >= 0.9
            or current_persona.aggressiveness <= 0.1
            or current_persona.risk_tolerance <= 0.1
        ):
            return True

        # Board が CEO のパフォーマンスを問題視した場合（meeting_state内情報がある場合）
        board_status = None
        if isinstance(meeting_state, dict):
            board_decision = meeting_state.get('board_decision')
            if isinstance(board_decision, dict):
                board_status = board_decision.get('status')

        if board_status in {'rejected', 'conditional'}:
            return True

        # 組織負荷が高い場合の交代検討
        units = org_state.get('units', []) if isinstance(org_state, dict) else []
        avg_load = 0.0
        if units:
            workload_values = [unit.get('workload_index', 0.0) for unit in units if isinstance(unit, dict)]
            avg_load = float(sum(workload_values) / len(workload_values)) if workload_values else 0.0
        if avg_load > 1.0:
            return True

        return False

import json
import os
import uuid
from typing import Dict, List, Optional

from ..models.execution_model import ExecutionRequirement
from ..models.financial_model import (
    FinancialFundamentals,
    InvestmentDecisionRecord,
    InvestmentRequest,
)
from .business_portfolio_service import BusinessPortfolioService
from .execution_capacity_service import ExecutionCapacityService
from .organization_service import OrganizationService

TAX_RATE = 0.25


def _safe_float(value: Optional[float]) -> float:
    return float(value or 0.0)


class FinancialService:
    def __init__(self):
        self.data_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), '../../../../data/samples')
        )
        self.financial_file = os.path.join(self.data_path, 'financial_fundamentals_sample.json')
        self.pending_requests_file = os.path.join(self.data_path, 'financial_pending_requests.json')
        self.alert_template_file = os.path.join(self.data_path, 'emergency_playbook_templates.json')
        self.execution_log_file = os.path.join(self.data_path, 'executed_playbook_log.json')
        self.execution_capacity_service = ExecutionCapacityService()
        self.portfolio_service = BusinessPortfolioService()
        self.org_service = OrganizationService()

    def load_financials(self) -> FinancialFundamentals:
        if not os.path.exists(self.financial_file):
            raise FileNotFoundError(f'Financial fundamentals data not found: {self.financial_file}')

        with open(self.financial_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        return FinancialFundamentals(**data)

    def save_financials(self, financials: FinancialFundamentals) -> None:
        with open(self.financial_file, 'w', encoding='utf-8') as f:
            f.write(financials.model_dump_json(indent=2, ensure_ascii=False))

    def load_pending_requests(self) -> List[InvestmentRequest]:
        if not os.path.exists(self.pending_requests_file):
            return []

        with open(self.pending_requests_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        return [InvestmentRequest(**item) for item in data]

    def save_pending_requests(self, requests: List[InvestmentRequest]) -> None:
        with open(self.pending_requests_file, 'w', encoding='utf-8') as f:
            f.write(json.dumps([request.model_dump() for request in requests], indent=2, ensure_ascii=False))

    def calculate_monthly_free_cash_flow(
        self,
        pl_monthly: Dict[str, float],
        financials: FinancialFundamentals,
        working_capital_change: float = 0.0,
    ) -> FinancialFundamentals:
        revenue_value = pl_monthly.get('revenue', 0.0)
        if isinstance(revenue_value, dict):
            revenue = float(sum(revenue_value.values()))
        else:
            revenue = _safe_float(revenue_value)

        operating_expenses = _safe_float(financials.monthly_operating_expenses)
        operating_income = revenue - operating_expenses
        tax = max(0.0, operating_income * TAX_RATE)
        fcf = operating_income - tax - _safe_float(financials.monthly_debt_service) - working_capital_change
        financials.free_cash_flow = round(fcf, 3)
        return financials

    def _simulate_health_ratio_changes(
        self,
        requested_amount: float,
        financials: FinancialFundamentals,
    ) -> Dict[str, float]:
        indicators = financials.financial_health_indicators.copy()
        debt_to_equity = _safe_float(indicators.get('debt_to_equity'))
        current_ratio = _safe_float(indicators.get('current_ratio'))

        equity_pressure = requested_amount / max(financials.cash_reserves, 1.0)
        indicators['debt_to_equity'] = round(debt_to_equity + equity_pressure * 0.08, 3)
        indicators['current_ratio'] = round(max(0.1, current_ratio - equity_pressure * 0.15), 3)

        return indicators

    def _evaluate_repayability(
        self,
        request: InvestmentRequest,
    ) -> bool:
        payback_years = request.payback_period_months / 12.0
        expected_return = request.expected_return_rate * payback_years
        return expected_return >= 0.15 and payback_years <= 5.0

    def schedule_tranche_execution(
        self,
        request: InvestmentRequest,
        approved_amount: float,
        financials: FinancialFundamentals,
    ) -> List[Dict[str, object]]:
        tranche_count = request.tranche_count or 1
        interval = request.tranche_interval_months or 1
        tranche_buffer = float(financials.investment_policy.get('tranche_buffer', 1.0))
        tranche_amount = round(approved_amount / tranche_count, 3) if tranche_count > 0 else 0.0
        schedule: List[Dict[str, object]] = []

        execution_state = self.execution_capacity_service.load_state()
        execution_capacity_score = self.execution_capacity_service.calculate_execution_capacity_score(
            execution_state.capacity,
            execution_state.load,
            execution_state.efficiency,
        )

        for tranche_index in range(tranche_count):
            scheduled_month = (request.requested_month or 1) + tranche_index * interval
            required_cash_threshold = round(
                financials.minimum_cash_threshold + tranche_buffer,
                3,
            )
            status = 'pending'
            if financials.cash_reserves < required_cash_threshold:
                status = 'deferred'
            elif execution_capacity_score < tranche_amount:
                status = 'delayed'

            schedule.append(
                {
                    'tranche_index': tranche_index + 1,
                    'scheduled_month': scheduled_month,
                    'tranche_amount': tranche_amount,
                    'required_cash_threshold': required_cash_threshold,
                    'status': status,
                }
            )

        return schedule

    def evaluate_investment_request(
        self,
        investment_request: InvestmentRequest,
        financials: FinancialFundamentals,
        portfolio_unit: Optional[object] = None,
        org_service: Optional[OrganizationService] = None,
    ) -> InvestmentDecisionRecord:
        request = investment_request
        if request.requested_month is None:
            request.requested_month = 0

        cash_reserves = _safe_float(financials.cash_reserves)
        min_cash = _safe_float(financials.minimum_cash_threshold)
        max_pct = float(financials.investment_policy.get('max_investment_pct_of_cash', 0.25))
        max_allowed = round(cash_reserves * max_pct, 3)
        capacity = 1.0
        if org_service is not None:
            try:
                capacity = self.org_service.estimate_execution_capacity(
                    self.org_service.load_organization_state(month=request.requested_month or 1),
                    request.business_unit_id,
                )
            except Exception:
                capacity = 1.0

        active_requests = self.load_pending_requests()
        execution_requirements = [
            ExecutionRequirement(
                investment_request_id=pending.id,
                required_capacity=pending.required_capacity or 0.0,
                duration_months=pending.tranche_interval_months or 1,
            )
            for pending in active_requests
        ]
        execution_requirements.append(
            ExecutionRequirement(
                investment_request_id=request.id,
                required_capacity=request.required_capacity or 0.0,
                duration_months=request.tranche_interval_months or 1,
            )
        )

        execution_capacity = self.execution_capacity_service.load_state()
        execution_capacity_score = self.execution_capacity_service.calculate_execution_capacity_score(
            execution_capacity.capacity,
            self.execution_capacity_service.calculate_load(execution_requirements),
            execution_capacity.efficiency,
        )

        suggested_amount = request.requested_amount
        decision = 'Approved'
        reason_list: List[str] = []
        impact = -round(min(request.requested_amount, cash_reserves), 3)
        partial_candidate = None

        if request.required_capacity is not None and execution_capacity_score < request.required_capacity:
            decision = 'Deferred'
            reason_list.append('Insufficient execution capacity for this investment.')
            reason_list.append(
                f'Execution score {execution_capacity_score} is lower than required {request.required_capacity:.3f}.'
            )

        if cash_reserves - request.requested_amount < min_cash:
            decision = 'Rejected'
            reason_list.append('流動性閾値を下回るため投資は却下されました。')
        elif request.requested_amount > max_allowed:
            partial_amount = max_allowed
            partial_candidate = partial_amount
            if partial_amount >= min_cash:
                decision = 'Partial'
                suggested_amount = partial_amount
                reason_list.append(
                    f'投資ポリシーにより最大{partial_amount:.3f}まで部分承認します。'
                )
            else:
                decision = 'Rejected'
                reason_list.append('投資額が現金比率の最大許容値を超えています。')
        elif not self._evaluate_repayability(request):
            decision = 'Deferred'
            reason_list.append('期待リターンと回収期間の組み合わせが保守的ではないため保留とします。')
        elif capacity < 0.35:
            decision = 'Deferred'
            reason_list.append('組織実行力が不足しているため投資判断を保留します。')
        elif portfolio_unit is not None and portfolio_unit.strategic_fit < 0.35 and request.strategic_priority < 3:
            decision = 'Deferred'
            reason_list.append('戦略適合性が低く、優先度も低いため保留としました。')

        if decision == 'Approved':
            approved_amount = request.requested_amount
        elif decision == 'Partial':
            approved_amount = suggested_amount
        else:
            approved_amount = 0.0

        tranche_schedule = None
        if approved_amount > 0.0 and request.tranche_count:
            tranche_schedule = self.schedule_tranche_execution(
                request=request,
                approved_amount=approved_amount,
                financials=financials,
            )
            if tranche_schedule:
                reason_list.append('部分承認トランシェスケジュールが生成されました。')

        indicators = self._simulate_health_ratio_changes(approved_amount, financials)
        reason_list.append(
            f'推定 debt_to_equity={indicators["debt_to_equity"]:.3f}, current_ratio={indicators["current_ratio"]:.3f}。'
        )

        if not reason_list:
            reason_list.append('財務制約と戦略適合性を確認し、投資可否を判定しました。')

        return InvestmentDecisionRecord(
            id=str(uuid.uuid4()),
            investment_request_id=request.id,
            decision=decision,
            approved_amount=round(approved_amount, 3),
            partial_candidate=round(partial_candidate, 3) if partial_candidate is not None else None,
            tranche_schedule=tranche_schedule,
            reason=' '.join(reason_list),
            impact_on_cash=round(-approved_amount, 3),
            applied_month=request.requested_month,
        )

    def apply_investment_decision(
        self,
        decision_record: InvestmentDecisionRecord,
        financials: FinancialFundamentals,
        business_unit_id: Optional[str] = None,
    ) -> FinancialFundamentals:
        applied_amount = decision_record.approved_amount
        if decision_record.decision in {'Approved', 'Partial'} and applied_amount > 0.0:
            if decision_record.tranche_index is not None:
                # 単一トランシェ分を適用する場合
                applied_amount = round(applied_amount, 3)

            financials.cash_reserves = round(
                max(0.0, financials.cash_reserves - applied_amount),
                3,
            )
            financials.committed_capex = round(
                financials.committed_capex + applied_amount,
                3,
            )
            if business_unit_id:
                self.portfolio_service.record_investment_execution(decision_record, business_unit_id)

        return financials

    def simulate_financial_cycle(
        self,
        month: int,
        pl_monthly: Dict[str, float],
        financials: FinancialFundamentals,
        pending_requests: List[InvestmentRequest],
        portfolio_service: Optional[BusinessPortfolioService] = None,
        org_service: Optional[OrganizationService] = None,
    ) -> Dict[str, object]:
        updated_financials = self.calculate_monthly_free_cash_flow(pl_monthly, financials)
        decisions: List[InvestmentDecisionRecord] = []

        for request in pending_requests:
            decision = self.evaluate_investment_request(
                request,
                updated_financials,
                portfolio_unit=None,
                org_service=org_service,
            )
            if decision.decision in {'Approved', 'Partial'}:
                updated_financials = self.apply_investment_decision(decision, updated_financials)
            decisions.append(decision)

        updated_financials.cash_reserves = round(
            max(0.0, updated_financials.cash_reserves + updated_financials.free_cash_flow),
            3,
        )

        return {
            'month': month,
            'financials': updated_financials.model_dump(),
            'free_cash_flow': updated_financials.free_cash_flow,
            'investment_decisions': [decision.model_dump() for decision in decisions],
            'emergency_measures': self.emergency_liquidity_measures(updated_financials),
        }

    def emergency_liquidity_measures(self, financials: FinancialFundamentals) -> List[str]:
        measures: List[str] = []
        if financials.cash_reserves < financials.minimum_cash_threshold:
            measures.append('すべての新規投資を一時停止してください。')
            measures.append('広告・マーケティング支出を縮小し、キャッシュアウトを抑制します。')
            measures.append('外注費と非コア支出を優先的に見直します。')
            if financials.available_credit_line > 0.0:
                measures.append(
                    f'与信枠を活用し、最大{financials.available_credit_line:.3f}の流動性を確保することを検討します。'
                )
        elif financials.cash_reserves < financials.minimum_cash_threshold + financials.liquidity_buffer_months:
            measures.append('流動性緩和のため、追加の予備資金を確保するオプションを評価します。')
        else:
            measures.append('現時点では緊急措置は不要です。')

        return measures

    def generate_emergency_playbook(
        self,
        financials: FinancialFundamentals,
        market_state: Optional[Dict[str, object]] = None,
        org_state: Optional[Dict[str, object]] = None,
    ) -> Dict[str, object]:
        current_cash = financials.cash_reserves
        buffer_threshold = round(financials.minimum_cash_threshold + financials.liquidity_buffer_months, 3)
        threshold = round(financials.minimum_cash_threshold, 3)

        if current_cash < threshold:
            trigger = 'cash_below_threshold'
            status = 'critical'
        elif current_cash < buffer_threshold:
            trigger = 'cash_below_buffer'
            status = 'warning'
        else:
            trigger = 'stable'
            status = 'stable'

        actions = [
            {
                'id': 'suspend_tranches',
                'label': 'Suspend all pending tranches',
                'impact': '+2.0',
            },
            {
                'id': 'reduce_production_cost',
                'label': 'Reduce production cost',
                'impact': '+0.5',
            },
            {
                'id': 'pause_advertising',
                'label': 'Pause advertising for 1 month',
                'impact': '+0.3',
            },
        ]
        if financials.available_credit_line > 0.0:
            actions.append(
                {
                    'id': 'use_credit_line',
                    'label': 'Use credit line',
                    'impact': f'+{financials.available_credit_line:.1f}',
                }
            )

        recommended_priority = ['suspend_tranches', 'reduce_production_cost', 'pause_advertising']

        return {
            'trigger': trigger,
            'cash': round(current_cash, 3),
            'threshold': threshold,
            'status': status,
            'actions': actions,
            'recommended_priority': recommended_priority,
        }

    def load_emergency_alert_templates(self) -> Dict[str, str]:
        if not os.path.exists(self.alert_template_file):
            raise FileNotFoundError(f'Emergency alert template file not found: {self.alert_template_file}')

        with open(self.alert_template_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def build_emergency_alert_templates(self, playbook: Dict[str, object]) -> Dict[str, str]:
        try:
            templates = self.load_emergency_alert_templates()
        except FileNotFoundError:
            templates = {
                'slack_template': (
                    '🚨 Emergency Triggered: {trigger}\n'
                    'Current Cash: {cash}\n'
                    'Threshold: {threshold}\n\n'
                    'Recommended Actions:\n{actions}\n\n'
                    'Run Playbook: /api/financials/execute-playbook'
                ),
                'email_subject_template': '[Alert] Emergency Liquidity Triggered',
                'email_body_template': (
                    'Subject: [Alert] Emergency Liquidity Triggered\n\n'
                    'Cash has fallen below the threshold.\n\n'
                    'Current: {cash}\n'
                    'Threshold: {threshold}\n\n'
                    'Recommended Actions:\n{action_lines}\n\n'
                    'You can execute the playbook via:\nPOST /api/financials/execute-playbook\n'
                ),
            }

        actions = playbook.get('actions', [])
        numbered_actions = '\n'.join(
            [f"{idx + 1}. {action['label']} ({action['impact']})" for idx, action in enumerate(actions)]
        )
        bullet_actions = '\n'.join([f"- {action['label']}" for action in actions])

        slack_text = templates['slack_template'].format(
            trigger=playbook.get('trigger', 'unknown'),
            cash=playbook.get('cash', 'unknown'),
            threshold=playbook.get('threshold', 'unknown'),
            actions=numbered_actions,
            action_lines=bullet_actions,
        )
        email_subject = templates['email_subject_template']
        email_body = templates['email_body_template'].format(
            cash=playbook.get('cash', 'unknown'),
            threshold=playbook.get('threshold', 'unknown'),
            action_lines=bullet_actions,
            actions=numbered_actions,
        )

        return {
            'slack': slack_text,
            'email_subject': email_subject,
            'email_body': email_body,
        }

    def dispatch_emergency_alerts(self, playbook: Dict[str, object]) -> None:
        if playbook.get('trigger') not in {'cash_below_threshold', 'cash_below_buffer'}:
            return

        from .notification_service import send_email_alert, send_slack_alert

        templates = self.build_emergency_alert_templates(playbook)
        send_slack_alert(templates['slack'])
        send_email_alert(templates['email_subject'], templates['email_body'])

    def add_pending_request(self, request: InvestmentRequest) -> None:
        pending = self.load_pending_requests()
        pending.append(request)
        self.save_pending_requests(pending)

    def log_playbook_execution(self, executed_actions: List[str], timestamp: str) -> None:
        log_entry = {
            'executed_actions': executed_actions,
            'timestamp': timestamp,
        }
        logs: List[Dict[str, object]] = []
        if os.path.exists(self.execution_log_file):
            try:
                with open(self.execution_log_file, 'r', encoding='utf-8') as f:
                    logs = json.load(f)
            except Exception:
                logs = []

        logs.append(log_entry)
        with open(self.execution_log_file, 'w', encoding='utf-8') as f:
            json.dump(logs, f, indent=2, ensure_ascii=False)

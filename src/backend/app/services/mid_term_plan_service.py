import json
import os
from typing import Dict, List, Optional

from ..models.mid_term_plan_model import MidTermPlan
from ..services.mid_term_plan_engine import MidTermPlanEngine
from .company_operations_integration_service import CompanyOperationsIntegrationService
from .executive_meeting_service import ExecutiveMeetingService
from ..models.executive_meeting_model import BoardDecision


class MidTermPlanService:
    def __init__(self, plan_root: Optional[str] = None):
        self.integration_service = CompanyOperationsIntegrationService()
        self.meeting_service = ExecutiveMeetingService()
        self.engine = MidTermPlanEngine()
        self.plan_root = plan_root or os.path.abspath(
            os.path.join(os.path.dirname(__file__), '../../../../plans/midterm')
        )
        os.makedirs(self.plan_root, exist_ok=True)

    def generate_and_store_mid_term_plan(self, start_year: int, horizon_years: int = 3) -> MidTermPlan:
        history_months = self._collect_history_months()
        market_state = history_months[-1].get('environment', {}) if history_months else {}
        financials = history_months[-1].get('financials', {}) if history_months else {}
        financials['fiscal_year'] = start_year
        board_decisions = self._collect_board_decisions()
        ceo_persona = self._load_ceo_persona()

        plan = self.engine.build_mid_term_plan(
            history_months=history_months,
            ceo_persona=ceo_persona,
            board_decisions=board_decisions,
            current_financials=financials,
            current_market_state=market_state,
            horizon_years=horizon_years,
        )

        filename = f'{start_year}-{start_year + horizon_years - 1}'
        self._save_plan_json(plan, filename)
        self._save_plan_markdown(plan, filename)
        return plan

    def get_latest_plan(self) -> Optional[MidTermPlan]:
        candidates = []
        for filename in os.listdir(self.plan_root):
            if filename.endswith('.json'):
                base = filename[:-5]
                parts = base.split('-')
                if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
                    candidates.append((int(parts[0]), int(parts[1]), filename))
        if not candidates:
            return None
        candidates.sort(key=lambda item: (item[0], item[1]), reverse=True)
        return self.get_plan_by_period(f'{candidates[0][0]}-{candidates[0][1]}')

    def get_plan_by_period(self, period: str) -> MidTermPlan:
        json_file = os.path.join(self.plan_root, f'{period}.json')
        if not os.path.exists(json_file):
            raise FileNotFoundError(f'Mid-term plan not found: {json_file}')
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return MidTermPlan(**data)

    def _collect_history_months(self) -> List[Dict[str, object]]:
        history_months = []
        for month in range(1, 13):
            history_months.append(self.integration_service.simulate_month_full(month))
        return history_months

    def _collect_board_decisions(self) -> List[BoardDecision]:
        decisions: List[BoardDecision] = []
        try:
            state = self.meeting_service.load_meeting_state()
            if state.board_decision:
                decisions.append(state.board_decision)
        except FileNotFoundError:
            pass
        return decisions

    def _load_ceo_persona(self) -> Optional[Dict[str, float]]:
        try:
            state = self.meeting_service.load_meeting_state()
            return state.ceo_persona
        except FileNotFoundError:
            return None

    def _save_plan_json(self, plan: MidTermPlan, filename: str) -> None:
        path = os.path.join(self.plan_root, f'{filename}.json')
        with open(path, 'w', encoding='utf-8') as f:
            f.write(plan.model_dump_json(indent=2, ensure_ascii=False))

    def _save_plan_markdown(self, plan: MidTermPlan, filename: str) -> None:
        path = os.path.join(self.plan_root, f'{filename}.md')
        with open(path, 'w', encoding='utf-8') as f:
            f.write(self._render_markdown(plan))

    def _render_markdown(self, plan: MidTermPlan) -> str:
        lines = [
            f'# 中期経営計画（{plan.start_year}–{plan.end_year}）',
            '',
            '## 1. ビジョン',
            plan.vision,
            '',
            '## 2. 財務目標',
            '| 年度 | 売上目標 | 営業利益目標 | 投資計画 |',
            '|------|----------|--------------|----------|',
        ]
        for year, revenue, profit, capex in zip(
            plan.financial.years,
            plan.financial.revenue_targets,
            plan.financial.operating_profit_targets,
            plan.financial.capex_plan,
        ):
            lines.append(f'| {year} | {revenue:.3f} | {profit:.3f} | {capex:.3f} |')
        lines.extend([
            '',
            '## 3. 組織計画',
        ])
        for year, headcount in plan.organization.headcount_plan.items():
            lines.append(f'- {year}: ヘッドカウント {headcount}名')
        lines.append('- 重点ケイパビリティ:')
        for capability in plan.organization.key_capabilities:
            lines.append(f'  - {capability}')
        lines.extend([
            '',
            '## 4. 市場・事業戦略',
            '- フォーカスセグメント:',
        ])
        for segment in plan.market.focus_segments:
            lines.append(f'  - {segment}')
        lines.append('- 成長テーマ:')
        for theme in plan.market.growth_themes:
            lines.append(f'  - {theme}')
        lines.extend([
            '',
            '## 5. リスクとガバナンス',
            '- 主なリスク:',
        ])
        for risk in plan.risk.key_risks:
            lines.append(f'  - {risk}')
        lines.append('- 対応策:')
        for mitigation in plan.risk.mitigations:
            lines.append(f'  - {mitigation}')
        lines.extend([
            '',
            '## 6. 取締役会コメント',
            f'- 承認ステータス: {plan.board_comment.approval_status}',
            f'- コメント: {plan.board_comment.comment}',
            '',
        ])
        return '\n'.join(lines)
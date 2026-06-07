from typing import Dict, List, Optional

from ..models.mid_term_plan_model import (
    BoardComment,
    MidTermFinancialPlan,
    MidTermMarketPlan,
    MidTermOrgPlan,
    MidTermPlan,
    MidTermRiskPlan,
)
from ..models.executive_meeting_model import BoardDecision


class MidTermPlanEngine:
    def build_mid_term_plan(
        self,
        history_months: List[Dict[str, object]],
        ceo_persona: Optional[Dict[str, float]],
        board_decisions: List[BoardDecision],
        current_financials: Dict[str, object],
        current_market_state: Dict[str, object],
        horizon_years: int = 3,
    ) -> MidTermPlan:
        if not history_months:
            raise ValueError('history_months must contain at least one month of data')

        revenue_trend = self._estimate_revenue_growth(history_months)
        profit_margin = self._estimate_profit_margin(current_financials)
        conservatism = self._estimate_conservatism(ceo_persona, board_decisions)
        growth_rate = max(0.02, revenue_trend - conservatism)

        start_year = current_financials.get('fiscal_year', 2026)
        end_year = start_year + horizon_years - 1

        financial_plan = self._build_financial_plan(
            start_year,
            horizon_years,
            float(current_financials.get('revenue', 0.0)),
            float(current_financials.get('profit', 0.0)),
            profit_margin,
            growth_rate,
        )
        organization_plan = self._build_organization_plan(
            history_months,
            current_market_state,
            ceo_persona,
            start_year,
        )
        market_plan = self._build_market_plan(current_market_state)
        risk_plan = self._build_risk_plan(board_decisions, current_market_state)
        vision = self._build_vision(start_year, end_year, growth_rate, ceo_persona)
        board_comment = self._review_mid_term_plan(board_decisions, growth_rate)
        board_approved = board_comment.approval_status in ['承認済み', '条件付き承認']

        return MidTermPlan(
            start_year=start_year,
            end_year=end_year,
            vision=vision,
            financial=financial_plan,
            organization=organization_plan,
            market=market_plan,
            risk=risk_plan,
            board_approved=board_approved,
            board_comment=board_comment,
        )

    def _estimate_revenue_growth(self, history_months: List[Dict[str, object]]) -> float:
        revenues = []
        for month in history_months:
            revenue = month.get('financials', {}).get('revenue', {})
            if isinstance(revenue, dict):
                revenues.append(float(sum(revenue.values())))
            elif isinstance(revenue, (int, float)):
                revenues.append(float(revenue))
        if len(revenues) < 2:
            return 0.05

        growth_rates = []
        for prev, curr in zip(revenues, revenues[1:]):
            if prev > 0:
                growth_rates.append((curr - prev) / prev)
        if not growth_rates:
            return 0.05
        return float(sum(growth_rates) / len(growth_rates))

    def _estimate_profit_margin(self, current_financials: Dict[str, object]) -> float:
        return float(current_financials.get('profit_margin', 0.15))

    def _estimate_conservatism(
        self,
        ceo_persona: Optional[Dict[str, float]],
        board_decisions: List[BoardDecision],
    ) -> float:
        conservatism = 0.0
        if ceo_persona:
            if ceo_persona.get('aggressiveness', 0.6) < 0.5:
                conservatism += 0.02
            if ceo_persona.get('risk_tolerance', 0.6) < 0.5:
                conservatism += 0.01
        if board_decisions:
            statuses = [decision.status for decision in board_decisions if hasattr(decision, 'status')]
            if 'rejected' in statuses:
                conservatism += 0.04
            elif 'conditional' in statuses:
                conservatism += 0.02
        return conservatism

    def _build_financial_plan(
        self,
        start_year: int,
        horizon_years: int,
        base_revenue: float,
        base_profit: float,
        profit_margin: float,
        growth_rate: float,
    ) -> MidTermFinancialPlan:
        years = [start_year + offset for offset in range(horizon_years)]
        revenue_targets = []
        operating_profit_targets = []
        capex_plan = []

        current_revenue = max(base_revenue, 1.0)
        for offset in range(horizon_years):
            target_revenue = round(current_revenue * ((1 + growth_rate) ** offset), 3)
            revenue_targets.append(target_revenue)
            target_profit = round(target_revenue * profit_margin, 3)
            operating_profit_targets.append(target_profit)
            capex_plan.append(round(target_revenue * 0.12, 3))

        return MidTermFinancialPlan(
            years=years,
            revenue_targets=revenue_targets,
            operating_profit_targets=operating_profit_targets,
            capex_plan=capex_plan,
        )

    def _build_organization_plan(
        self,
        history_months: List[Dict[str, object]],
        current_market_state: Dict[str, object],
        ceo_persona: Optional[Dict[str, float]],
        start_year: int,
    ) -> MidTermOrgPlan:
        headcount_plan = {}
        latest_headcount = 120
        for month in reversed(history_months):
            org = month.get('organization', {})
            if isinstance(org, dict):
                units = org.get('units', [])
                if isinstance(units, list) and units:
                    latest_headcount = sum(int(unit.get('headcount', 0)) for unit in units if isinstance(unit, dict))
                    break

        growth_factor = 1.0
        if ceo_persona and ceo_persona.get('aggressiveness', 0.6) >= 0.7:
            growth_factor = 1.08
        elif ceo_persona and ceo_persona.get('aggressiveness', 0.6) <= 0.4:
            growth_factor = 0.98

        for offset in range(len(history_months) and 3 or 3):
            year = offset + 1
            headcount_plan[year] = int(round(latest_headcount * (growth_factor ** offset)))

        capabilities = [
            '舞台制作力',
            'IPマネジメント',
            'デジタル配信運営',
        ]
        if current_market_state.get('market_index_by_segment'):
            segments = list(current_market_state.get('market_index_by_segment', {}).keys())
            if 'デジタル' in segments and 'デジタル配信運営' not in capabilities:
                capabilities.append('デジタル配信運営')

        return MidTermOrgPlan(
            headcount_plan={start_year + i: headcount for i, headcount in enumerate(headcount_plan.values())},
            key_capabilities=capabilities,
        )

    def _build_market_plan(self, current_market_state: Dict[str, object]) -> MidTermMarketPlan:
        segments = []
        market_index = current_market_state.get('market_index_by_segment', {})
        if isinstance(market_index, dict):
            segments = sorted(market_index, key=lambda k: market_index.get(k, 0.0), reverse=True)[:3]

        growth_themes = [
            'IP横断展開',
            'ライブ・イベント強化',
            '海外展開',
        ]
        return MidTermMarketPlan(
            focus_segments=segments or ['舞台・エンタメ全体'],
            growth_themes=growth_themes,
        )

    def _build_risk_plan(
        self,
        board_decisions: List[BoardDecision],
        current_market_state: Dict[str, object],
    ) -> MidTermRiskPlan:
        key_risks = ['興行不振', 'キャッシュフロー悪化', '市場環境変動']
        mitigations = ['投資上限ルール', 'Boardによる大型投資の事前承認']
        if any(current_market_state.get('active_events', [])):
            key_risks.append('市場ショックの長期化')
        if any(getattr(decision, 'status', None) == 'rejected' for decision in board_decisions):
            mitigations.append('意思決定プロセスの再評価とリスクモニタリング強化')

        return MidTermRiskPlan(key_risks=key_risks, mitigations=mitigations)

    def _build_vision(
        self,
        start_year: int,
        end_year: int,
        growth_rate: float,
        ceo_persona: Optional[Dict[str, float]],
    ) -> str:
        tone = '攻め' if ceo_persona and ceo_persona.get('aggressiveness', 0.6) >= 0.7 else '安定' if ceo_persona and ceo_persona.get('aggressiveness', 0.6) <= 0.4 else 'バランス'
        return (
            f"{start_year}–{end_year}年のホリプロは、{tone}の成長とブランド価値を両立し、" 
            f"収益性の改善と市場機会の最大化を目指します。成長率は年間{growth_rate * 100:.1f}%前後を想定します。"
        )

    def _review_mid_term_plan(
        self,
        board_decisions: List[BoardDecision],
        growth_rate: float,
    ) -> BoardComment:
        if not board_decisions:
            return BoardComment(approval_status='未レビュー', comment='取締役会による過去のレビューが存在しないため、仮の計画とします。')

        latest_review = board_decisions[-1]
        if latest_review.status == 'approved':
            return BoardComment(approval_status='承認済み', comment='取締役会は現行の方針を承認しました。')
        if latest_review.status == 'conditional':
            return BoardComment(approval_status='条件付き承認', comment='条件付き承認です。キャッシュと進捗を定期的に確認します。')
        return BoardComment(approval_status='要再検証', comment='過去の取締役会でリスクが指摘されており、計画の再検証が必要です。')

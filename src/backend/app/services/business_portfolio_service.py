import json
import os
from typing import Dict, List

from ..models.business_portfolio_model import (
    BusinessPortfolioUnit,
    BusinessPortfolioState,
    InvestmentDecision,
)
from .corporate_fundamentals_service import CorporateFundamentalsService
from .company_operations_integration_service import CompanyOperationsIntegrationService
from .external_environment_service import ExternalEnvironmentService
from .organization_service import OrganizationService


class BusinessPortfolioService:
    def __init__(self):
        self.data_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), '../../../../data/samples')
        )
        self.portfolio_state_file = os.path.join(self.data_path, 'business_portfolio_state.json')
        self.corporate_service = CorporateFundamentalsService()
        self.environment_service = ExternalEnvironmentService()
        self.integration_service = CompanyOperationsIntegrationService()
        self.organization_service = OrganizationService()

    def load_portfolio_state(self) -> BusinessPortfolioState:
        if not os.path.exists(self.portfolio_state_file):
            raise FileNotFoundError(f'Business portfolio state not found: {self.portfolio_state_file}')

        with open(self.portfolio_state_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        return BusinessPortfolioState(**data)

    def _map_revenue_for_unit(self, unit, pl_data: Dict[str, object]) -> float:
        revenue = 0.0

        if isinstance(unit.revenue_model, list):
            for category in unit.revenue_model:
                revenue += float(pl_data.get('revenue', {}).get(category, 0.0))
        else:
            revenue_map = {
                'stage_market': ['performance'],
                'digital_distribution_market': ['license'],
                'cm_ad_market': ['talent'],
                'md_market': ['md'],
            }
            for category in revenue_map.get(unit.revenue_model, []):
                revenue += float(pl_data.get('revenue', {}).get(category, 0.0))

        if revenue == 0.0:
            revenue = float(sum(pl_data.get('revenue', {}).values()) or 0.0) * 0.1

        return round(revenue, 3)

    def _normalize(self, value: float) -> float:
        return max(0.0, min(1.0, value))

    def _calculate_strategic_fit(self, unit, fundamentals) -> float:
        average_kpi = sum(unit.kpis.values()) / max(len(unit.kpis), 1)
        advantage_text = ' '.join(fundamentals.profile.competitive_advantages).lower()
        match_bonus = 0.0
        if any(term in advantage_text for term in ['digital', 'license', 'performance', 'stage', 'md']):
            match_bonus = 0.12
        return self._normalize((average_kpi * 0.4) + match_bonus)

    def _calculate_growth_rate(self, unit, environment_state: Dict[str, object]) -> float:
        segment_id = None
        if unit.linked_market_segments:
            segment_id = unit.linked_market_segments[0]
        elif isinstance(unit.revenue_model, str):
            segment_id = unit.revenue_model

        if not segment_id:
            return 0.0

        market_size = float(environment_state.get('market_size_by_segment', {}).get(segment_id, 0.0))
        base_size = float(environment_state.get('base_size_by_segment', {}).get(segment_id, 1.0))
        if base_size == 0:
            return 0.0
        growth = (market_size / base_size) - 1.0
        return round(growth, 4)

    def _calculate_risk_score(self, unit, market_alignment: float, competitive_pressure: float) -> float:
        risk_score = 0.2 + len(unit.risk_factors) * 0.08 + (1.0 - market_alignment) * 0.25 + competitive_pressure * 0.25
        return self._normalize(risk_score)

    def _calculate_investment_need(self, revenue: float, risk_score: float) -> float:
        return round(max(0.5, revenue * (0.12 + risk_score * 0.15)), 3)

    def _calculate_return_rate(self, growth_rate: float, competitive_pressure: float, strategic_fit: float) -> float:
        base = 0.07 + growth_rate * 0.4 + strategic_fit * 0.12 - competitive_pressure * 0.1
        return round(max(0.03, min(0.35, base)), 3)

    def build_portfolio_units(
        self,
        month: int,
        fundamentals,
        environment_state: Dict[str, object],
        pl_data: Dict[str, object],
    ) -> List[BusinessPortfolioUnit]:
        units: List[BusinessPortfolioUnit] = []

        for unit in fundamentals.business_units:
            revenue = self._map_revenue_for_unit(unit, pl_data)
            profit_margin = float(pl_data.get('profit_margin', 0.0))
            profit = round(revenue * profit_margin, 3)

            growth_rate = self._calculate_growth_rate(unit, environment_state)
            market_alignment = self._normalize(0.4 + growth_rate + sum(unit.kpis.values()) * 0.04)
            segment_id = unit.linked_market_segments[0] if unit.linked_market_segments else unit.revenue_model if isinstance(unit.revenue_model, str) else None
            competitive_pressure = float(environment_state.get('competitive_pressure_by_segment', {}).get(segment_id, 0.0))
            strategic_fit = self._calculate_strategic_fit(unit, fundamentals)
            risk_score = self._calculate_risk_score(unit, market_alignment, competitive_pressure)
            investment_need = self._calculate_investment_need(revenue, risk_score)
            investment_return_rate = self._calculate_return_rate(growth_rate, competitive_pressure, strategic_fit)

            units.append(
                BusinessPortfolioUnit(
                    id=f'portfolio_{unit.id}_{month}',
                    business_unit_id=unit.id,
                    revenue=revenue,
                    profit=profit,
                    profit_margin=round(profit_margin, 4),
                    growth_rate=growth_rate,
                    market_alignment=market_alignment,
                    competitive_pressure=competitive_pressure,
                    risk_score=risk_score,
                    investment_need=investment_need,
                    investment_return_rate=investment_return_rate,
                    strategic_fit=strategic_fit,
                )
            )

        return units

    def evaluate_investment_decision(
        self,
        unit: BusinessPortfolioUnit,
        financials,
        management_style: str,
    ) -> InvestmentDecision:
        cash_reserves = float(financials.cash_reserves)
        style = management_style.lower()
        decision = 'Maintain'
        reason = '現在のパフォーマンスは安定しているため維持を推奨します。'
        expected_impact = {
            'revenue': unit.revenue * 0.12,
            'profit': unit.profit * 0.1,
            'growth_rate': unit.growth_rate,
        }
        required_budget = unit.investment_need

        if cash_reserves < unit.investment_need * 1.2:
            if unit.risk_score > 0.7:
                decision = 'Exit'
                reason = '投資余力が不足しているため、撤退または資金集約が必要です。'
            else:
                decision = 'Reduce'
                reason = 'キャッシュリザーブが限定的なため、投資を抑制します。'
        elif 'aggressive' in style:
            if unit.growth_rate > unit.competitive_pressure:
                decision = 'Invest'
                reason = '成長性が競争圧を上回っているため、積極投資を推奨します。'
            elif unit.risk_score > 0.75:
                decision = 'Reduce'
                reason = 'リスクが高いため、慎重な資本配分が必要です。'
        elif 'balanced' in style:
            if unit.profit_margin >= 0.15 and unit.investment_return_rate >= 0.12:
                decision = 'Invest'
                reason = '利益率と回収見込みが良好なため、投資を検討します。'
            elif unit.risk_score > 0.8:
                decision = 'Reduce'
                reason = 'リスクが高いため、投資規模を縮小します。'
        elif 'conservative' in style:
            if unit.risk_score > 0.7 or unit.competitive_pressure > 0.8:
                decision = 'Exit'
                reason = '保守的な経営スタイルのため、高リスク事業は撤退を検討します。'
            elif unit.growth_rate > 0.12 and unit.investment_return_rate > 0.13:
                decision = 'Invest'
                reason = '低リスクかつ成長性が高い場合に限り投資を推奨します。'

        if decision == 'Invest' and cash_reserves < unit.investment_need:
            decision = 'Maintain'
            reason = '投資余力不足により、現状維持へ修正しました。'

        if decision == 'Maintain' and unit.growth_rate < 0.02 and unit.risk_score > 0.7:
            decision = 'Reduce'
            reason = '成長性が低く、リスクが高いため、縮小を推奨します。'

        if decision == 'Reduce' and unit.growth_rate < 0.0 and unit.risk_score > 0.75:
            decision = 'Exit'
            reason = '市場状況が悪化しており、撤退を検討します。'

        return InvestmentDecision(
            business_unit_id=unit.business_unit_id,
            decision=decision,
            reason=reason,
            expected_impact=expected_impact,
            required_budget=round(required_budget, 3),
        )

    def generate_portfolio_decisions(
        self,
        portfolio_units: List[BusinessPortfolioUnit],
        fundamentals,
        org_state=None,
    ) -> List[InvestmentDecision]:
        decisions: List[InvestmentDecision] = []
        cash_reserves = float(fundamentals.financials.cash_reserves)

        for unit in portfolio_units:
            decision = self.evaluate_investment_decision(unit, fundamentals.financials, fundamentals.profile.management_style)
            if org_state is not None:
                capacity = self.organization_service.estimate_execution_capacity(org_state, unit.business_unit_id)
                if decision.decision == 'Invest' and capacity < 0.4:
                    decision = InvestmentDecision(
                        business_unit_id=unit.business_unit_id,
                        decision='Maintain',
                        reason='組織実行力が限定されているため、投資を保留します。',
                        expected_impact=decision.expected_impact,
                        required_budget=decision.required_budget,
                    )
                elif decision.decision == 'Invest' and capacity < 0.2:
                    decision = InvestmentDecision(
                        business_unit_id=unit.business_unit_id,
                        decision='Reduce',
                        reason='組織実行力が不足しているため、投資規模を縮小します。',
                        expected_impact=decision.expected_impact,
                        required_budget=decision.required_budget,
                    )
            decisions.append(decision)

        opportunity_score = 0.0
        for unit in portfolio_units:
            opportunity_score = max(opportunity_score, unit.growth_rate * unit.strategic_fit)

        if opportunity_score > 0.12 and cash_reserves > 1.5:
            decisions.append(
                InvestmentDecision(
                    business_unit_id='new_business_opportunity',
                    decision='NewBusiness',
                    reason='市場成長と企業の強みが一致しており、新規事業開発の余地があります。',
                    expected_impact={
                        'revenue': round(sum(unit.revenue for unit in portfolio_units) * 0.08, 3),
                        'profit': round(sum(unit.profit for unit in portfolio_units) * 0.06, 3),
                        'growth_rate': round(opportunity_score * 0.8, 4),
                    },
                    required_budget=round(min(2.5, cash_reserves * 0.4), 3),
                )
            )

        return decisions

    def record_investment_execution(self, decision_record, business_unit_id: str):
        try:
            state = self.load_portfolio_state()
            for unit in state.portfolio_units:
                if unit.business_unit_id == business_unit_id:
                    unit.investment_need = round(
                        max(0.0, unit.investment_need - decision_record.approved_amount),
                        3,
                    )
            return state
        except Exception:
            return None

    def simulate_portfolio_cycle(self, month: int, year: int = 2026) -> BusinessPortfolioState:
        if month < 1 or month > 12:
            raise ValueError('month must be between 1 and 12')

        fundamentals = self.corporate_service.load_fundamentals()
        environment_state = self.environment_service.build_environment_state(month, year)
        org_state = self.organization_service.load_organization_state(month=month)
        integration_result = self.integration_service.simulate_month_full(month, year)
        pl_data = integration_result.get('pl_with_fundamentals', integration_result.get('pl', {}))

        portfolio_units = self.build_portfolio_units(month, fundamentals, environment_state, pl_data)
        decisions = self.generate_portfolio_decisions(portfolio_units, fundamentals, org_state=org_state)

        return BusinessPortfolioState(
            month=month,
            portfolio_units=portfolio_units,
            decisions=decisions,
        )

import json
import os
from typing import Dict, List

from ..models.corporate_fundamentals_model import (
    CorporateFundamentalsModel,
    CorporateHistoryEvent,
)
from ..models.operational_issues_model import IssueInstance
from ..models.midterm_strategy_model import StrategyRecommendation


class CorporateFundamentalsService:
    def __init__(self):
        self.data_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), '../../../../data/samples')
        )
        self.fundamentals_file = os.path.join(self.data_path, 'corporate_fundamentals_model.json')

    def load_fundamentals(self) -> CorporateFundamentalsModel:
        if not os.path.exists(self.fundamentals_file):
            raise FileNotFoundError(f'Corporate fundamentals data not found: {self.fundamentals_file}')

        with open(self.fundamentals_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        return CorporateFundamentalsModel(**data)

    def build_monthly_fundamentals_impact(self, month_number: int, year: int = 2026) -> Dict[str, object]:
        from .company_operating_service import CompanyOperatingService
        from .external_environment_service import ExternalEnvironmentService

        fundamentals = self.load_fundamentals()
        company_service = CompanyOperatingService()
        environment_service = ExternalEnvironmentService()

        model = company_service.prepare_company_model()
        monthly = next((item for item in model.monthly_pl if item.month == month_number), None)
        if monthly is None:
            raise ValueError(f'Month {month_number} is not defined in the company model')

        matching_kpi = next((kpi for kpi in model.kpis if kpi.month == month_number), None)
        if matching_kpi is None:
            raise ValueError(f'KPI for month {month_number} is not defined in the company model')

        environment_state = environment_service.build_environment_state(month_number, year)
        company_service.apply_external_environment_to_pl(monthly, environment_state)
        company_service.calculate_cash_flow(model)
        company_service.calculate_kpis(model)

        baseline = {
            'month': monthly.month,
            'revenue': monthly.revenue.copy(),
            'cost': monthly.cost.copy(),
            'profit': monthly.profit,
            'profit_margin': monthly.profit_margin,
            'cash_flow': monthly.cash_flow,
            'kpis': {
                'gross_profit': matching_kpi.gross_profit,
                'operating_profit': matching_kpi.operating_profit,
                'license_ratio': matching_kpi.license_ratio,
                'digital_ratio': matching_kpi.digital_ratio,
                'talent_ltv_index': matching_kpi.talent_ltv_index,
            },
        }

        self.apply_fundamentals_to_pl(monthly, fundamentals)
        self.apply_fundamentals_to_kpis(matching_kpi, fundamentals)

        adjusted = {
            'month': monthly.month,
            'revenue': monthly.revenue.copy(),
            'cost': monthly.cost.copy(),
            'profit': monthly.profit,
            'profit_margin': monthly.profit_margin,
            'cash_flow': monthly.cash_flow,
            'kpis': {
                'gross_profit': matching_kpi.gross_profit,
                'operating_profit': matching_kpi.operating_profit,
                'license_ratio': matching_kpi.license_ratio,
                'digital_ratio': matching_kpi.digital_ratio,
                'talent_ltv_index': matching_kpi.talent_ltv_index,
            },
        }

        return {
            'month': monthly.month,
            'year': year,
            'fundamentals': fundamentals.model_dump(),
            'environment_state': environment_state,
            'baseline_pl': baseline,
            'adjusted_pl': adjusted,
            'adjusted_kpis': adjusted['kpis'],
        }

    def apply_fundamentals_to_pl(self, month, fundamentals: CorporateFundamentalsModel) -> None:
        def matches_category(category: str, unit) -> bool:
            category_map = {
                'talent': ['bu_ai_talent', 'bu_advertising'],
                'performance': ['bu_live_entertainment'],
                'license': ['bu_digital_ip'],
                'md': ['bu_md'],
                'digital': ['bu_digital_ip', 'bu_ai_solutions'],
            }
            if unit.id in category_map.get(category, []):
                return True
            if isinstance(unit.revenue_model, list):
                if any(model.lower() in category.lower() for model in unit.revenue_model):
                    return True
            else:
                if unit.revenue_model.lower() in category.lower():
                    return True
            return unit.name.lower() in category.lower()

        for key, amount in fundamentals.financials.fixed_costs.items():
            month.cost[key] = round(month.cost.get(key, 0.0) + amount, 3)

        for unit in fundamentals.business_units:
            for category, revenue_amount in month.revenue.items():
                if matches_category(category, unit):
                    rate = sum(unit.cost_structure.values())
                    month.cost[category] = round(
                        month.cost.get(category, 0.0) + revenue_amount * rate,
                        3,
                    )

        revenue_total = sum(month.revenue.values())
        cost_total = sum(month.cost.values())
        month.profit = round(revenue_total - cost_total, 3)
        month.profit_margin = round((month.profit / revenue_total) if revenue_total else 0.0, 3)

    def apply_fundamentals_to_kpis(self, kpi, fundamentals: CorporateFundamentalsModel) -> None:
        for unit in fundamentals.business_units:
            name = unit.name.lower()
            if 'digital' in name:
                kpi.digital_ratio = round(min(1.0, kpi.digital_ratio + sum(unit.kpis.values()) * 0.01), 3)
            if 'license' in name:
                kpi.license_ratio = round(min(1.0, kpi.license_ratio + sum(unit.kpis.values()) * 0.01), 3)
            if 'performance' in name or 'stage' in name:
                if hasattr(kpi, 'performance_profit_margin'):
                    kpi.performance_profit_margin = round(
                        min(1.0, kpi.performance_profit_margin + sum(unit.kpis.values()) * 0.005),
                        3,
                    )

        for segment in fundamentals.customer_segments:
            if 'frequency' in segment.behavior_patterns:
                kpi.license_ratio = round(
                    min(1.0, kpi.license_ratio + segment.behavior_patterns.get('frequency', 0.0) * 0.01),
                    3,
                )

    def apply_fundamentals_to_issues(
        self,
        issues: List[IssueInstance],
        fundamentals: CorporateFundamentalsModel,
    ) -> List[IssueInstance]:
        low_skill_units = [
            unit for unit in fundamentals.organization_units
            if sum(unit.skill_profile.values()) / max(len(unit.skill_profile), 1) < 0.6
        ]
        cautious_units = [
            unit for unit in fundamentals.organization_units
            if '慎重' in unit.culture_traits or 'conservative' in unit.culture_traits
        ]

        for issue in issues:
            if low_skill_units and issue.severity != 'Critical':
                issue.severity = 'High'
            if cautious_units and issue.status == 'Open':
                issue.severity = 'Medium' if issue.severity == 'Low' else issue.severity

        return issues

    def apply_fundamentals_to_strategy(
        self,
        recommendations: List[StrategyRecommendation],
        fundamentals: CorporateFundamentalsModel,
    ) -> List[StrategyRecommendation]:
        advantage_text = ' '.join(fundamentals.profile.competitive_advantages).lower()
        sorted_recommendations = []

        for rec in recommendations:
            score = 1.0
            if any(term in advantage_text for term in ['license', 'digital', 'performance', 'md', '海外']):
                score += 0.2
            sorted_recommendations.append((score, rec))

        sorted_recommendations.sort(key=lambda item: item[0], reverse=True)
        return [rec for _, rec in sorted_recommendations]

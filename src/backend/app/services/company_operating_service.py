import json
import os
from collections import defaultdict
from typing import Dict, Optional, Union
from ..models.company_operating_model import (
    CompanyOperatingModel,
    MonthlySimulationResult
)
from ..models.corporate_fundamentals_model import CorporateFundamentalsModel
from ..models.external_environment_model_v2 import ExternalEnvironmentState
from .organization_service import OrganizationService
from ..models.organization_model import OrganizationState

class CompanyOperatingService:
    def __init__(self):
        self.data_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), '../../../../data/samples')
        )
        self.company_file = os.path.join(self.data_path, 'company_operating_model.json')
        self.initial_cash_balance = 30.0

    def load_company_model(self) -> CompanyOperatingModel:
        if not os.path.exists(self.company_file):
            raise FileNotFoundError(f'Company operating data not found: {self.company_file}')

        with open(self.company_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        return CompanyOperatingModel(**data)

    def apply_seasonality(self, model: CompanyOperatingModel) -> CompanyOperatingModel:
        factor_map = {item.month: item for item in model.seasonality}

        for month in model.monthly_pl:
            factor = factor_map.get(month.month)
            if factor is None:
                continue

            month.revenue = {
                category: round(amount * factor.revenue_multiplier.get(category, 1.0), 3)
                for category, amount in month.revenue.items()
            }
            month.cost = {
                category: round(amount * factor.cost_multiplier.get(category, 1.0), 3)
                for category, amount in month.cost.items()
            }

        return model

    def calculate_monthly_pl(self, model: CompanyOperatingModel, environment_state: Optional[Union[Dict[str, object], ExternalEnvironmentState]] = None) -> CompanyOperatingModel:
        for month in model.monthly_pl:
            # Apply market_growth_modifier
            market_growth_modifier = 0.0
            shocks = []
            if environment_state is not None:
                if isinstance(environment_state, dict):
                    market_growth_modifier = float(environment_state.get('market_growth_modifier', 0.0))
                    shocks = environment_state.get('shocks', []) or environment_state.get('active_shocks', [])
                else:
                    market_growth_modifier = float(getattr(environment_state, 'market_growth_modifier', 0.0))
                    shocks = getattr(environment_state, 'shocks', []) or getattr(environment_state, 'active_shocks', [])

            if market_growth_modifier:
                for category in month.revenue:
                    month.revenue[category] *= (1 + market_growth_modifier)

            # Apply shocks
            for shock in shocks:
                if isinstance(shock, dict):
                    shock_type = shock.get('shock_type') or shock.get('type')
                    severity = float(shock.get('severity', 0.0))
                else:
                    shock_type = getattr(shock, 'shock_type', None) or getattr(shock, 'type', None)
                    severity = float(getattr(shock, 'severity', 0.0))

                if shock_type == "currency":
                    # 原価率上昇
                    for category in month.cost:
                        month.cost[category] *= (1 + severity * 0.05)
                elif shock_type == "recession":
                    # 興行・広告の売上減少
                    if 'performance' in month.revenue:
                        month.revenue['performance'] *= (1 - severity * 0.1)
                    if 'advertising' in month.revenue:
                        month.revenue['advertising'] *= (1 - severity * 0.1)

            revenue_total = sum(month.revenue.values())
            cost_total = sum(month.cost.values())
            profit = round(revenue_total - cost_total, 3)
            profit_margin = round((profit / revenue_total) if revenue_total else 0.0, 3)

            month.profit = profit
            month.profit_margin = profit_margin

        return model

    def calculate_cash_flow(self, model: CompanyOperatingModel) -> CompanyOperatingModel:
        cash_balance = self.initial_cash_balance

        for month in model.monthly_pl:
            investment_amount = sum(
                investment.amount
                for investment in model.investments
                if investment.start_month <= month.month <= investment.end_month
            )
            month.cash_flow = round(month.profit - investment_amount, 3)
            cash_balance = round(cash_balance + month.cash_flow, 3)

            matching_kpi = next((kpi for kpi in model.kpis if kpi.month == month.month), None)
            if matching_kpi is not None:
                matching_kpi.cash_balance = cash_balance

        return model

    def calculate_kpis(self, model: CompanyOperatingModel) -> CompanyOperatingModel:
        for month in model.monthly_pl:
            revenue_total = sum(month.revenue.values())
            cost_total = sum(month.cost.values())
            gross_profit = round(
                revenue_total
                - (month.cost.get('talent_related', 0.0) + month.cost.get('production', 0.0)),
                3
            )
            operating_profit = round(revenue_total - cost_total, 3)

            matching_kpi = next((kpi for kpi in model.kpis if kpi.month == month.month), None)
            if matching_kpi is None:
                continue

            matching_kpi.gross_profit = gross_profit
            matching_kpi.operating_profit = operating_profit
            matching_kpi.license_ratio = round(
                (month.revenue.get('license', 0.0) / revenue_total) if revenue_total else 0.0,
                3,
            )
            if matching_kpi.digital_ratio == 0.0:
                matching_kpi.digital_ratio = 0.13
            if matching_kpi.talent_ltv_index == 0.0:
                matching_kpi.talent_ltv_index = 1.0

        return model

    def apply_external_environment_to_pl(self, month, environment_state: Dict[str, object]) -> None:
        category_segment_map = {
            'license': 'digital_distribution_market',
            'digital': 'digital_distribution_market',
            'performance': 'stage_market',
            'advertising': 'cm_ad_market',
            'md': 'md_market',
        }
        market_sizes = environment_state.get('market_size_by_segment', {})
        base_sizes = environment_state.get('base_size_by_segment', {})
        pressure = environment_state.get('competitive_pressure_by_segment', {})

        for category, value in month.revenue.items():
            segment_id = category_segment_map.get(category)
            if not segment_id or segment_id not in market_sizes or segment_id not in base_sizes:
                continue

            market_coef = market_sizes[segment_id] / max(base_sizes[segment_id], 1.0)
            pressure_coef = max(0.4, 1.0 - float(pressure.get(segment_id, 0.0)))
            adjusted = round(value * market_coef * pressure_coef, 3)
            month.revenue[category] = adjusted

        revenue_total = sum(month.revenue.values())
        cost_total = sum(month.cost.values())
        month.profit = round(revenue_total - cost_total, 3)
        month.profit_margin = round((month.profit / revenue_total) if revenue_total else 0.0, 3)

    def apply_environment_to_kpis(self, kpi, environment_state: Dict[str, object]) -> None:
        trend_effects = environment_state.get('trend_effects', {})
        digital_impact = sum(
            effect.get('digital_distribution_market', 0.0)
            for effect in trend_effects.values()
            if isinstance(effect, dict)
        )
        stage_impact = sum(
            effect.get('stage_market', 0.0)
            for effect in trend_effects.values()
            if isinstance(effect, dict)
        )

        kpi.digital_ratio = round(max(0.0, min(1.0, kpi.digital_ratio + digital_impact * 0.5)), 3)
        kpi.license_ratio = round(max(0.0, min(1.0, kpi.license_ratio + stage_impact * 0.2)), 3)

    def apply_environment_to_issues(self, issues, environment_state: Dict[str, object]):
        stage_size = environment_state.get('market_size_by_segment', {}).get('stage_market', 0.0)
        base_stage_size = environment_state.get('base_size_by_segment', {}).get('stage_market', 1.0)
        if stage_size < base_stage_size * 0.9:
            for issue in issues:
                if getattr(issue, 'issue_id', None) == 'weak_performance_profit_margin':
                    setattr(issue, 'severity', 'Critical')
        return issues

    def apply_corporate_fundamentals_to_result(
        self,
        result: Dict[str, object],
        fundamentals: CorporateFundamentalsModel,
    ) -> Dict[str, object]:
        for key, amount in fundamentals.financials.fixed_costs.items():
            result['cost'][key] = round(result['cost'].get(key, 0.0) + amount, 3)

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

        for unit in fundamentals.business_units:
            for category, revenue_amount in result['revenue'].items():
                if matches_category(category, unit):
                    rate = sum(unit.cost_structure.values())
                    result['cost'][category] = round(
                        result['cost'].get(category, 0.0) + revenue_amount * rate,
                        3,
                    )

        revenue_total = sum(result['revenue'].values())
        cost_total = sum(result['cost'].values())
        result['profit'] = round(revenue_total - cost_total, 3)
        result['profit_margin'] = round((result['profit'] / revenue_total) if revenue_total else 0.0, 3)

        kpis = result.get('kpis', {})
        for unit in fundamentals.business_units:
            name = unit.name.lower()
            if 'digital' in name:
                kpis['digital_ratio'] = round(
                    min(1.0, kpis.get('digital_ratio', 0.0) + sum(unit.kpis.values()) * 0.01),
                    3,
                )
            if 'license' in name:
                kpis['license_ratio'] = round(
                    min(1.0, kpis.get('license_ratio', 0.0) + sum(unit.kpis.values()) * 0.01),
                    3,
                )
            if 'performance' in name or 'stage' in name:
                kpis['performance_profit_margin'] = round(
                    min(1.0, kpis.get('performance_profit_margin', 0.0) + sum(unit.kpis.values()) * 0.005),
                    3,
                )

        result['kpis'] = kpis
        return result

    def prepare_company_model(self, environment_state: Optional[Dict[str, object]] = None) -> CompanyOperatingModel:
        model = self.load_company_model()
        self.apply_seasonality(model)
        self.calculate_monthly_pl(model, environment_state=environment_state)
        self.calculate_cash_flow(model)
        self.calculate_kpis(model)
        return model

    def get_customer_count_for_segment(self, segment) -> int:
        return {
            'seg_core_fans': 12000,
            'seg_light_fans': 24000,
            'seg_advertisers': 220,
            'seg_digital_platforms': 310,
            'seg_enterprise_clients': 90,
        }.get(segment.id, 1000)

    def build_customer_summary(self, fundamentals: CorporateFundamentalsModel):
        summary = []
        for segment in fundamentals.customer_segments:
            summary.append({
                'name': segment.name,
                'estimated_customers': float(self.get_customer_count_for_segment(segment)),
                'avg_spend': segment.behavior_patterns.get('avg_spend', 0.0),
                'purchase_frequency': segment.behavior_patterns.get('purchase_frequency', 0.0),
                'linked_business_units': segment.linked_business_units,
            })
        return summary

    def apply_customers_to_revenue(
        self,
        monthly,
        fundamentals: CorporateFundamentalsModel,
        environment_state: Optional[Dict[str, object]] = None,
    ) -> None:
        category_potentials = defaultdict(float)
        business_unit_map = {unit.id: unit for unit in fundamentals.business_units}

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

        def get_environment_factor(unit) -> float:
            if not environment_state:
                return 1.0
            segment_factors = []
            for segment_id in getattr(unit, 'linked_market_segments', []):
                base_size = float(environment_state.get('base_size_by_segment', {}).get(segment_id, 1.0))
                market_size = float(environment_state.get('market_size_by_segment', {}).get(segment_id, base_size))
                pressure = float(environment_state.get('competitive_pressure_by_segment', {}).get(segment_id, 0.0))
                if base_size <= 0:
                    continue
                segment_factors.append((market_size / base_size) * max(0.6, 1.0 - pressure))
            return float(sum(segment_factors) / len(segment_factors)) if segment_factors else 1.0

        for segment in fundamentals.customer_segments:
            customers = self.get_customer_count_for_segment(segment)
            purchase_frequency = float(segment.behavior_patterns.get('purchase_frequency', 0.0))
            avg_spend = float(segment.behavior_patterns.get('avg_spend', 0.0))
            if customers <= 0 or purchase_frequency <= 0 or avg_spend <= 0:
                continue

            raw_potential = customers * purchase_frequency * avg_spend
            demand_coefficient = 0.8 + 0.4 * (
                float(segment.sensitivity.get('price', 0.0))
                + float(segment.sensitivity.get('trend', 0.0))
                + float(segment.sensitivity.get('promotion', 0.0))
            ) / 3.0
            linked_units = [business_unit_map.get(unit_id) for unit_id in segment.linked_business_units]
            linked_units = [unit for unit in linked_units if unit is not None]
            if not linked_units:
                continue

            for unit in linked_units:
                categories = [category for category in monthly.revenue if matches_category(category, unit)]
                if not categories:
                    continue
                per_category_share = raw_potential / max(len(categories), 1)
                env_factor = get_environment_factor(unit)
                for category in categories:
                    category_potentials[category] += per_category_share * env_factor * demand_coefficient

        for category, potential in category_potentials.items():
            current_revenue = float(monthly.revenue.get(category, 0.0))
            if current_revenue <= 0:
                continue
            demand_ratio = min(1.0, potential / max(current_revenue, 1.0))
            multiplier = 1.0 + 0.25 * demand_ratio
            multiplier = max(0.8, min(1.2, multiplier))
            monthly.revenue[category] = round(current_revenue * multiplier, 3)

        try:
            from .market_integration_service import MarketIntegrationService
            MarketIntegrationService().apply_market_factors_to_revenue(
                monthly,
                environment_state or {},
                fundamentals,
            )
        except Exception:
            pass

    def simulate_month(
        self,
        month_number: int,
        environment_state: Optional[Dict[str, object]] = None,
        org_state: Optional[OrganizationState] = None,
    ) -> MonthlySimulationResult:
        if month_number < 1 or month_number > 12:
            raise ValueError('month must be between 1 and 12')

        model = self.prepare_company_model(environment_state=environment_state)
        monthly = next((item for item in model.monthly_pl if item.month == month_number), None)
        if monthly is None:
            raise ValueError(f'Month {month_number} is not defined in the model')

        if org_state is None:
            org_service = OrganizationService()
            org_state = org_service.load_organization_state(month=month_number)

        org_service = OrganizationService()
        org_cost = org_service.compute_organization_costs(org_state)
        monthly.cost['organization_personnel'] = round(
            monthly.cost.get('organization_personnel', 0.0) + org_cost,
            3,
        )

        matching_kpi = next((kpi for kpi in model.kpis if kpi.month == month_number), None)
        if matching_kpi is None:
            raise ValueError(f'KPI for month {month_number} is not defined')

        fundamentals = None
        try:
            from .corporate_fundamentals_service import CorporateFundamentalsService
            fundamentals = CorporateFundamentalsService().load_fundamentals()
        except Exception:
            fundamentals = None

        if fundamentals is not None:
            self.apply_customers_to_revenue(monthly, fundamentals, environment_state)

        if environment_state is not None:
            self.apply_external_environment_to_pl(monthly, environment_state)

        from .financial_service import FinancialService
        financial_service = FinancialService()
        financials = financial_service.load_financials()
        financials.monthly_revenue = sum(monthly.revenue.values())
        financials = financial_service.calculate_monthly_free_cash_flow(monthly.model_dump(), financials)

        self.calculate_cash_flow(model)
        self.calculate_kpis(model)
        matching_kpi = next((kpi for kpi in model.kpis if kpi.month == month_number), None)
        if matching_kpi is None:
            raise ValueError(f'KPI for month {month_number} is not defined')

        if environment_state is not None:
            self.apply_environment_to_kpis(matching_kpi, environment_state)

        return MonthlySimulationResult(
            month=monthly.month,
            revenue=monthly.revenue,
            cost=monthly.cost,
            profit=monthly.profit,
            profit_margin=monthly.profit_margin,
            cash_flow=monthly.cash_flow,
            cash_balance=matching_kpi.cash_balance,
            free_cash_flow=financials.free_cash_flow,
            kpis={
                'gross_profit': matching_kpi.gross_profit,
                'operating_profit': matching_kpi.operating_profit,
                'license_ratio': matching_kpi.license_ratio,
                'digital_ratio': matching_kpi.digital_ratio,
                'talent_ltv_index': matching_kpi.talent_ltv_index,
            },
        )

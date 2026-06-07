import json
import os
from typing import Dict, List

from .company_operations_integration_service import CompanyOperationsIntegrationService
from ..models.midterm_strategy_model import (
    AnnualStrategicGoal,
    MidtermStrategyModel,
    StrategyGap,
    StrategyRecommendation,
    StrategyTheme,
    StrategicInitiative,
)

class MidtermStrategyService:
    def __init__(self):
        self.data_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), '../../../../data/samples')
        )
        self.strategy_file = os.path.join(self.data_path, 'midterm_strategy_model.json')
        self.integration_service = CompanyOperationsIntegrationService()

    def load_strategy_model(self) -> MidtermStrategyModel:
        if not os.path.exists(self.strategy_file):
            raise FileNotFoundError(f'Strategy data not found: {self.strategy_file}')

        with open(self.strategy_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        return MidtermStrategyModel(**data)

    def evaluate_kpi_gap(self, current_kpis: Dict[str, float], strategy_model: MidtermStrategyModel) -> List[StrategyGap]:
        gaps: List[StrategyGap] = []

        for theme in strategy_model.themes:
            for kpi_name, target_value in theme.target_kpis.items():
                current_value = float(current_kpis.get(kpi_name, 0.0))
                gap_value = round(target_value - current_value, 4)
                if gap_value >= 0.05:
                    severity = 'High'
                elif gap_value >= 0.02:
                    severity = 'Medium'
                else:
                    severity = 'Low'

                gaps.append(StrategyGap(
                    kpi_name=kpi_name,
                    current_value=current_value,
                    target_value=target_value,
                    gap=gap_value,
                    severity=severity,
                ))

        return gaps

    def recommend_initiatives(self, gaps: List[StrategyGap], strategy_model: MidtermStrategyModel) -> List[StrategyRecommendation]:
        recommendations: List[StrategyRecommendation] = []
        sorted_gaps = sorted(gaps, key=lambda gap: gap.gap, reverse=True)

        for gap in sorted_gaps:
            if gap.gap <= 0:
                continue

            related_themes = [theme for theme in strategy_model.themes if gap.kpi_name in theme.target_kpis]
            for theme in related_themes:
                candidates = [initiative for initiative in strategy_model.initiatives if initiative.theme_id == theme.id]
                if not candidates:
                    continue

                initiative = sorted(candidates, key=lambda i: i.investment_required)[0]
                recommendations.append(StrategyRecommendation(
                    theme_id=theme.id,
                    initiative_id=initiative.id,
                    reason=f'Current {gap.kpi_name} is below target by {gap.gap:.3f}',
                    expected_effect=initiative.expected_impact,
                ))

        return recommendations

    def simulate_year_with_strategy(self, year: int) -> Dict[str, object]:
        strategy_model = self.load_strategy_model()
        monthly_results = []
        aggregated_kpis: Dict[str, float] = {}
        kpi_counts: Dict[str, int] = {}

        for month in range(1, 13):
            month_result = self.integration_service.simulate_month_full(month)
            monthly_results.append(month_result)

            for kpi_name, value in month_result['pl']['kpis'].items():
                aggregated_kpis[kpi_name] = aggregated_kpis.get(kpi_name, 0.0) + float(value)
                kpi_counts[kpi_name] = kpi_counts.get(kpi_name, 0) + 1

        annual_kpis = {
            kpi_name: round(total / max(kpi_counts.get(kpi_name, 1), 1), 4)
            for kpi_name, total in aggregated_kpis.items()
        }

        gaps = self.evaluate_kpi_gap(annual_kpis, strategy_model)
        recommendations = self.recommend_initiatives(gaps, strategy_model)

        return {
            'year': year,
            'annual_kpis': annual_kpis,
            'gaps': [gap.model_dump() for gap in gaps],
            'recommendations': [rec.model_dump() for rec in recommendations],
            'monthly_results': monthly_results,
        }

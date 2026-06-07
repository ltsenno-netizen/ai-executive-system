from typing import Dict, List, Optional

from ..models.corporate_fundamentals_model import CorporateFundamentalsModel
from ..models.external_environment_model import MarketSegment
from ..services.external_environment_service import ExternalEnvironmentService


class MarketIntegrationService:
    def __init__(self):
        self.environment_service = ExternalEnvironmentService()

    def map_market_to_business_units(
        self,
        fundamentals: CorporateFundamentalsModel,
        environment_state: Dict[str, object],
    ) -> Dict[str, float]:
        unit_index: Dict[str, float] = {}
        segment_indices = environment_state.get('market_index_by_segment', {})

        for unit in fundamentals.business_units:
            indices: List[float] = []
            for segment_id in getattr(unit, 'linked_market_segments', []):
                if segment_id in segment_indices:
                    indices.append(float(segment_indices.get(segment_id, 1.0)))
            if indices:
                unit_index[unit.id] = sum(indices) / len(indices)
            else:
                unit_index[unit.id] = 1.0

        return unit_index

    def apply_market_factors_to_revenue(
        self,
        monthly,
        environment_state: Dict[str, object],
        fundamentals: CorporateFundamentalsModel,
    ) -> None:
        if not environment_state:
            return

        segment_indices = environment_state.get('market_index_by_segment', {})
        active_events = environment_state.get('active_events', [])
        segment_sensitivity: Dict[str, float] = {}

        for segment in self.environment_service.load_external_environment().segments:
            segment_sensitivity[segment.id] = float(segment.shock_sensitivity or 0.0)

        def get_category_index(unit) -> float:
            indices: List[float] = []
            for segment_id in getattr(unit, 'linked_market_segments', []):
                if segment_id in segment_indices:
                    indices.append(float(segment_indices.get(segment_id, 1.0)))
            return float(sum(indices) / len(indices)) if indices else 1.0

        def get_shock_multiplier(unit) -> float:
            multiplier = 1.0
            for event in active_events:
                if not isinstance(event, dict):
                    continue
                for segment_id, impact in event.get('impact_map', {}).items():
                    if segment_id in getattr(unit, 'linked_market_segments', []):
                        sensitivity = segment_sensitivity.get(segment_id, 0.0)
                        multiplier += float(impact) * (1.0 + sensitivity)
            return max(0.5, min(1.5, multiplier))

        category_map = {
            'talent': ['bu_ai_talent', 'bu_advertising'],
            'performance': ['bu_live_entertainment'],
            'license': ['bu_digital_ip'],
            'md': ['bu_md'],
            'digital': ['bu_digital_ip', 'bu_ai_solutions'],
        }

        def matches_category(category: str, unit) -> bool:
            if unit.id in category_map.get(category, []):
                return True
            if isinstance(unit.revenue_model, list):
                return any(model.lower() in category.lower() for model in unit.revenue_model)
            return unit.revenue_model.lower() in category.lower() or unit.name.lower() in category.lower()

        for unit in fundamentals.business_units:
            category_index = get_category_index(unit)
            shock_multiplier = get_shock_multiplier(unit)
            for category in monthly.revenue:
                if not matches_category(category, unit):
                    continue
                base_value = float(monthly.revenue.get(category, 0.0))
                adjusted = round(base_value * category_index * shock_multiplier, 3)
                monthly.revenue[category] = max(0.0, adjusted)

    def update_growth_forecasts(
        self,
        fundamentals: CorporateFundamentalsModel,
        environment_state: Dict[str, object],
    ) -> CorporateFundamentalsModel:
        segment_indices = environment_state.get('market_index_by_segment', {})
        for unit in fundamentals.business_units:
            index_values = [float(segment_indices.get(seg, 1.0)) for seg in getattr(unit, 'linked_market_segments', [])]
            if index_values:
                forecast = sum(index_values) / len(index_values)
                unit.kpis['growth_rate'] = round(min(1.0, max(0.0, forecast * 0.1)), 4)
        return fundamentals

import json
import os
from datetime import datetime
from typing import Dict, List, Optional

from ..models.external_environment_model import (
    Competitor,
    ExternalEnvironmentModel,
    ExternalEvent,
    ExternalShock,
    IndustryTrend,
    MarketSegment,
)


class ExternalEnvironmentService:
    def __init__(self):
        self.base_year = 2026
        self.data_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), '../../../../data/samples')
        )
        self.environment_file = os.path.join(self.data_path, 'external_environment_model.json')
        self.external_events_file = os.path.join(self.data_path, 'external_events.json')

    def load_external_environment(self) -> ExternalEnvironmentModel:
        if not os.path.exists(self.environment_file):
            raise FileNotFoundError(f'External environment data not found: {self.environment_file}')

        with open(self.environment_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        return ExternalEnvironmentModel(**data)

    def _get_segment(self, segment_id: str, model: ExternalEnvironmentModel) -> Optional[MarketSegment]:
        return next((segment for segment in model.segments if segment.id == segment_id), None)

    def _load_persisted_external_events(self) -> List[ExternalEvent]:
        if not os.path.exists(self.external_events_file):
            return []
        with open(self.external_events_file, 'r', encoding='utf-8') as f:
            raw = json.load(f)
        return [ExternalEvent(**item) for item in raw if isinstance(item, dict)]

    def _gather_external_events(
        self,
        model: ExternalEnvironmentModel,
        extra_events: Optional[List[ExternalEvent]] = None,
    ) -> List[ExternalEvent]:
        events: List[ExternalEvent] = []
        if model.external_events:
            events.extend(model.external_events)
        events.extend(self._load_persisted_external_events())

        if extra_events:
            for event in extra_events:
                if isinstance(event, ExternalEvent):
                    events.append(event)
                elif isinstance(event, dict):
                    try:
                        events.append(ExternalEvent(**event))
                    except Exception:
                        pass

        unique = {event.id: event for event in events}
        return list(unique.values())

    def _calculate_monthly_index(self, segment: MarketSegment, month: int, year: int) -> float:
        if segment.monthly_index and isinstance(segment.monthly_index, dict):
            key = f'{year:04d}-{month:02d}'
            if key in segment.monthly_index:
                return float(segment.monthly_index[key])

        seasonality = float((segment.seasonality or {}).get(month, 1.0))
        growth = float(segment.growth_rate or 0.0)
        indicator_multiplier = 1.0
        if segment.external_indicators:
            indicator_multiplier += sum(segment.external_indicators.values()) * 0.01
        return round((1.0 + growth) * seasonality * indicator_multiplier, 4)

    def _is_event_active(self, event: ExternalEvent, month: int, year: int) -> bool:
        try:
            event_date = datetime.fromisoformat(event.date)
        except ValueError:
            return False

        event_start_month = event_date.month
        event_start_year = event_date.year
        if year < event_start_year:
            return False

        months_since_start = (year - event_start_year) * 12 + (month - event_start_month)
        return 0 <= months_since_start < event.duration_months

    def calculate_market_size(
        self,
        segment_id: str,
        month: int,
        year: int,
        extra_events: Optional[List[ExternalEvent]] = None,
    ) -> float:
        model = self.load_external_environment()
        segment = self._get_segment(segment_id, model)
        if segment is None:
            raise ValueError(f'Segment not found: {segment_id}')

        base_size = float(segment.base_size or 0.0)
        year_offset = year - self.base_year
        base = base_size * ((1 + float(segment.growth_rate or 0.0)) ** year_offset)
        index = self._calculate_monthly_index(segment, month, year)
        trend_factor = 1.0 + sum(
            trend.impact_on_segments.get(segment_id, 0.0) for trend in model.trends
        )
        all_events = self._gather_external_events(model, extra_events=extra_events)
        event_factor = 1.0 + sum(
            event.impact_map.get(segment_id, 0.0)
            for event in all_events
            if self._is_event_active(event, month, year)
        )
        shock_factor = 1.0 + sum(
            shock.affected_segments.get(segment_id, 0.0)
            for shock in model.shocks
            if self._is_event_active(ExternalEvent(
                id=shock.id,
                date=f'{year}-01-01',
                type='legacy_shock',
                impact_map=shock.affected_segments,
                duration_months=shock.duration_months,
                source='legacy',
                notes=shock.description,
            ), month, year)
        )

        return round(max(0.0, base * index * trend_factor * shock_factor * event_factor), 3)

    def calculate_competitive_pressure(self, segment_id: str) -> float:
        model = self.load_external_environment()
        pressure = sum(
            competitor.strength_by_segment.get(segment_id, 0.0) * competitor.aggressiveness
            for competitor in model.competitors
        )
        return round(min(1.0, pressure), 3)

    def build_environment_state(
        self,
        month: int,
        year: int,
        extra_events: Optional[List[ExternalEvent]] = None,
    ) -> Dict[str, object]:
        model = self.load_external_environment()
        market_sizes = {
            segment.id: self.calculate_market_size(segment.id, month, year, extra_events=extra_events)
            for segment in model.segments
        }
        base_sizes = {segment.id: float(segment.base_size or 0.0) for segment in model.segments}
        trend_effects = {
            trend.id: trend.impact_on_segments for trend in model.trends
        }
        active_shocks = [shock.model_dump() for shock in model.shocks if self._is_event_active(
            ExternalEvent(
                id=shock.id,
                date=f'{year}-01-01',
                type='legacy_shock',
                impact_map=shock.affected_segments,
                duration_months=shock.duration_months,
                source='legacy',
                notes=shock.description,
            ), month, year
        )]
        all_events = self._gather_external_events(model, extra_events=extra_events or [])
        active_events = [event.model_dump() for event in all_events if self._is_event_active(event, month, year)]

        market_index_by_segment = {
            segment.id: self._calculate_monthly_index(segment, month, year)
            for segment in model.segments
        }

        competitive_pressure = {
            segment.id: self.calculate_competitive_pressure(segment.id)
            for segment in model.segments
        }

        return {
            'month': month,
            'year': year,
            'market_size_by_segment': market_sizes,
            'base_size_by_segment': base_sizes,
            'trend_effects': trend_effects,
            'active_shocks': active_shocks,
            'active_events': active_events,
            'market_index_by_segment': market_index_by_segment,
            'competitive_pressure_by_segment': competitive_pressure,
        }

    def calculate_company_opportunity(
        self,
        company_profile: Dict[str, float],
        environment_state: Dict[str, object],
    ) -> Dict[str, float]:
        market_sizes = environment_state.get('market_size_by_segment', {})
        competitive_pressure = environment_state.get('competitive_pressure_by_segment', {})
        opportunities: Dict[str, float] = {}

        for segment_id, size in market_sizes.items():
            share = float(company_profile.get(segment_id, 0.1))
            pressure = float(competitive_pressure.get(segment_id, 0.0))
            opportunities[segment_id] = round(size * share * max(0.0, 1.0 - pressure), 3)

        return opportunities

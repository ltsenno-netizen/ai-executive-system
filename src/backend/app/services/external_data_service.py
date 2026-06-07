import csv
import json
import os
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Optional

from ..models.external_environment_model import (
    ExternalEnvironmentModel,
    ExternalEvent,
    MarketSegment,
)


class SourceConnector(ABC):
    @abstractmethod
    def load(self, path: str) -> Dict[str, object]:
        pass


class FileConnector(SourceConnector):
    def load(self, path: str) -> Dict[str, object]:
        if not os.path.exists(path):
            raise FileNotFoundError(f'Source file not found: {path}')

        if path.lower().endswith('.json'):
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)

        if path.lower().endswith('.csv'):
            with open(path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                return {'rows': [row for row in reader]}

        raise ValueError('Unsupported connector file type: ' + path)


class ExternalDataService:
    def __init__(self):
        self.data_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), '../../../../data/samples')
        )
        self.environment_file = os.path.join(self.data_path, 'external_environment_model.json')
        self.indicators_file = os.path.join(self.data_path, 'market_indicators_sample.json')
        self.event_file = os.path.join(self.data_path, 'external_events.json')
        self.raw_indicators_file = os.path.join(self.data_path, 'raw_market_indicators.json')

    def _read_json(self, path: str) -> Dict[str, object]:
        if not os.path.exists(path):
            return {}
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _write_json(self, path: str, data: Dict[str, object]) -> None:
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def _load_environment_model(self) -> ExternalEnvironmentModel:
        raw = self._read_json(self.environment_file)
        return ExternalEnvironmentModel(**raw)

    def _save_environment_model(self, model: ExternalEnvironmentModel) -> None:
        self._write_json(self.environment_file, model.model_dump())

    def _load_events(self) -> List[ExternalEvent]:
        raw = self._read_json(self.event_file)
        if not raw:
            return []
        return [ExternalEvent(**item) for item in raw]

    def _save_events(self, events: List[ExternalEvent]) -> None:
        self._write_json(self.event_file, [event.model_dump() for event in events])

    def fetch_market_indicators(self, source_config: Dict[str, str]) -> Dict[str, Dict[str, float]]:
        connector = FileConnector()
        data = connector.load(source_config.get('path', self.indicators_file))
        indicators = data.get('segments', {}) if isinstance(data, dict) else {}

        raw_indicators = {
            'source': source_config,
            'loaded_at': datetime.utcnow().isoformat() + 'Z',
            'segments': indicators,
        }
        self._write_json(self.raw_indicators_file, raw_indicators)

        environment = self._load_environment_model()
        for segment in environment.segments:
            segment.external_indicators = indicators.get(segment.id, {})
        self._save_environment_model(environment)

        return indicators

    def apply_seasonality_and_growth(self, base_month: str, market_segment: MarketSegment) -> MarketSegment:
        if market_segment.monthly_index is None:
            market_segment.monthly_index = {}

        year, month = map(int, base_month.split('-'))
        for offset in range(0, 12):
            current_year = year + (month + offset - 1) // 12
            current_month = ((month + offset - 1) % 12) + 1
            key = f'{current_year:04d}-{current_month:02d}'
            season = float((market_segment.seasonality or {}).get(current_month, 1.0))
            growth = float(market_segment.growth_rate or 0.0)
            indicator_multiplier = 1.0
            if market_segment.external_indicators:
                indicator_multiplier += sum(market_segment.external_indicators.values()) * 0.01
            market_segment.monthly_index[key] = round((1.0 + growth) * season * indicator_multiplier, 4)

        return market_segment

    def ingest_external_event(self, event_payload: Dict[str, object]) -> ExternalEvent:
        event = ExternalEvent(**event_payload)
        events = self._load_events()
        events.append(event)
        self._save_events(events)
        return event

    def simulate_market_shock(self, month: int, shock_spec: Dict[str, object]) -> Dict[str, object]:
        event_payload = {
            'id': shock_spec.get('id', f'shock-{month}-{int(datetime.utcnow().timestamp())}'),
            'date': shock_spec.get('date', f'2026-{month:02d}-01'),
            'type': shock_spec.get('type', 'macro_shock'),
            'impact_map': shock_spec.get('impact_map', {}),
            'duration_months': int(shock_spec.get('duration_months', 1)),
            'source': shock_spec.get('source', 'simulated'),
            'notes': shock_spec.get('notes', 'Simulated market shock'),
        }
        event = self.ingest_external_event(event_payload)
        return {
            'event': event.model_dump(),
            'summary': {
                'affected_segments': event.impact_map,
                'duration_months': event.duration_months,
            },
        }

    def backfill_historical_indices(self, horizon_years: int = 3) -> Dict[str, Dict[str, float]]:
        environment = self._load_environment_model()
        year = datetime.utcnow().year
        for segment in environment.segments:
            if segment.monthly_index is None:
                segment.monthly_index = {}
            for past_year in range(year - horizon_years, year + 1):
                for month in range(1, 13):
                    key = f'{past_year:04d}-{month:02d}'
                    if key not in segment.monthly_index:
                        season = float((segment.seasonality or {}).get(month, 1.0))
                        growth = float(segment.growth_rate or 0.0)
                        segment.monthly_index[key] = round((1.0 + growth) ** (past_year - year + horizon_years) * season, 4)
        self._save_environment_model(environment)
        return {segment.id: segment.monthly_index for segment in environment.segments}

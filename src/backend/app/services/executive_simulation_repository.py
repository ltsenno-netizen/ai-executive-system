import json
import os
from typing import List, Optional

from ..models.executive_simulation_model import ExecutiveSimulationResult


class ExecutiveSimulationRepository:
    """Persistence layer for executive simulation history."""

    def __init__(self):
        self.storage_dir = os.path.join(os.path.dirname(__file__), '../../../data/executive_simulation')
        os.makedirs(self.storage_dir, exist_ok=True)
        self.history_file = os.path.join(self.storage_dir, 'history.json')

    def save(self, result: ExecutiveSimulationResult) -> None:
        history = self._load_history()
        history = [item for item in history if item.simulation_id != result.simulation_id]
        history.append(result)
        self._save_history(history)

    def get_latest(self) -> Optional[ExecutiveSimulationResult]:
        history = self._load_history()
        if not history:
            return None
        return sorted(history, key=lambda item: item.timestamp, reverse=True)[0]

    def get_by_id(self, simulation_id: str) -> Optional[ExecutiveSimulationResult]:
        history = self._load_history()
        for item in history:
            if item.simulation_id == simulation_id:
                return item
        return None

    def list_recent(self, limit: int = 20) -> List[ExecutiveSimulationResult]:
        history = sorted(self._load_history(), key=lambda item: item.timestamp, reverse=True)
        return history[:limit]

    def _load_history(self) -> List[ExecutiveSimulationResult]:
        if not os.path.exists(self.history_file):
            return []

        try:
            with open(self.history_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return [ExecutiveSimulationResult(**item) for item in data]
        except Exception:
            return []

    def _save_history(self, history: List[ExecutiveSimulationResult]) -> None:
        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump([item.model_dump() for item in history], f, indent=2, default=str)

import json
import os
from datetime import datetime
from typing import List, Optional

from ..models.enterprise_autopilot_model import AutopilotCycleHistory, AutopilotCycleResult


class EnterpriseAutopilotRepository:
    """Persistence layer for storing autopilot cycle history."""

    def __init__(self):
        self.storage_dir = os.path.join(os.path.dirname(__file__), '../../../data/enterprise_autopilot')
        os.makedirs(self.storage_dir, exist_ok=True)
        self.history_file = os.path.join(self.storage_dir, 'cycle_history.json')

    def save_cycle(self, cycle: AutopilotCycleResult) -> None:
        history = self._load_history()
        # Replace existing cycle if ids match
        history.cycles = [c for c in history.cycles if c.cycle_id != cycle.cycle_id] + [cycle]
        history.last_run_at = cycle.completed_at or datetime.utcnow()
        history.total_cycles = len(history.cycles)
        self._save_history(history)

    def get_latest(self) -> Optional[AutopilotCycleResult]:
        history = self._load_history()
        if not history.cycles:
            return None
        return sorted(history.cycles, key=lambda c: c.completed_at or datetime.min, reverse=True)[0]

    def list_recent(self, limit: int = 5) -> List[AutopilotCycleResult]:
        history = self._load_history()
        return sorted(history.cycles, key=lambda c: c.completed_at or datetime.min, reverse=True)[:limit]

    def _load_history(self) -> AutopilotCycleHistory:
        if not os.path.exists(self.history_file):
            return AutopilotCycleHistory()

        try:
            with open(self.history_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return AutopilotCycleHistory(**data)
        except Exception:
            return AutopilotCycleHistory()

    def _save_history(self, history: AutopilotCycleHistory) -> None:
        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump(history.model_dump(), f, indent=2, default=str)

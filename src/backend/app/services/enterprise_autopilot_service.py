import uuid
from datetime import datetime
from typing import List, Optional

from .enterprise_autopilot_engine import EnterpriseAutopilotEngine
from .enterprise_autopilot_repository import EnterpriseAutopilotRepository
from ..models.enterprise_autopilot_model import AutopilotCycleResult
from .corporate_memory_service import CorporateMemoryService
from ..models.corporate_memory_model import MemoryImportance, MemoryItemType


class EnterpriseAutopilotService:
    """Service layer for Enterprise Autopilot orchestration and history."""

    def __init__(self):
        self.engine = EnterpriseAutopilotEngine()
        self.repository = EnterpriseAutopilotRepository()
        self.memory_service = CorporateMemoryService()

    def run_cycle(self) -> AutopilotCycleResult:
        cycle_id = str(uuid.uuid4())
        cycle_result = self.engine.run_autopilot_cycle(cycle_id)
        self.repository.save_cycle(cycle_result)
        self._record_cycle_memory(cycle_result)
        return cycle_result

    def get_latest_cycle(self) -> Optional[AutopilotCycleResult]:
        return self.repository.get_latest()

    def get_cycle_history(self, limit: int = 5) -> List[AutopilotCycleResult]:
        return self.repository.list_recent(limit)

    def _record_cycle_memory(self, cycle_result: AutopilotCycleResult) -> None:
        try:
            self.memory_service.add_memory(
                item_type=MemoryItemType.SYSTEM_EVENT,
                title="Enterprise Autopilot cycle",
                description=(
                    f"Autopilot cycle {cycle_result.cycle_id} completed with status {cycle_result.overall_status}."
                ),
                context={
                    "cycle_id": cycle_result.cycle_id,
                    "overall_status": cycle_result.overall_status,
                    "summary": cycle_result.summary,
                },
                importance=MemoryImportance.HIGH,
                tags=["ENTERPRISE_AUTOPILOT", "CYCLE"],
            )
        except Exception:
            pass

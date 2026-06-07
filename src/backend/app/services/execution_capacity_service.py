import json
import os
from typing import Dict, List, Optional

from ..models.execution_model import ExecutionHistoryRecord, ExecutionRequirement, ExecutionState


class ExecutionCapacityService:
    def __init__(self, data_path: Optional[str] = None):
        self.data_path = os.path.abspath(
            data_path
            if data_path
            else os.path.join(os.path.dirname(__file__), '../../../../data/samples')
        )
        self.state_file = os.path.join(self.data_path, 'execution_state.json')

    def load_state(self) -> ExecutionState:
        if not os.path.exists(self.state_file):
            return ExecutionState(capacity=10.0, load=0.0, efficiency=1.0, history=[])

        with open(self.state_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        return ExecutionState(**data)

    def save_state(self, state: ExecutionState) -> None:
        os.makedirs(self.data_path, exist_ok=True)
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(state.model_dump(), f, indent=2, ensure_ascii=False)

    def calculate_capacity(
        self,
        organization_personnel: float,
        digital_investment: float,
        outsourcing_factor: float,
        base_capacity: float = 10.0,
    ) -> float:
        return round(
            base_capacity
            + (organization_personnel * 0.05)
            + (digital_investment * 0.1)
            + outsourcing_factor,
            3,
        )

    def calculate_load(self, requirements: List[ExecutionRequirement]) -> float:
        return round(sum(req.required_capacity for req in requirements), 3)

    def calculate_efficiency(self, history: List[ExecutionHistoryRecord]) -> float:
        if not history:
            return 1.0

        recent = history[-6:]
        delay_rate = sum(record.delays for record in recent) / max(1, sum(record.projects_completed for record in recent))
        kpi_success_rate = sum(record.kpi_success_rate for record in recent) / len(recent)
        efficiency = 1.0 - (delay_rate * 0.4) + (kpi_success_rate * 0.6)
        return round(max(0.0, min(1.0, efficiency)), 3)

    def calculate_execution_capacity_score(
        self,
        capacity: float,
        load: float,
        efficiency: float,
    ) -> float:
        return round((capacity - load) * efficiency, 3)

    def get_current_state(self) -> Dict[str, object]:
        state = self.load_state()
        return {
            'capacity': state.capacity,
            'load': state.load,
            'efficiency': state.efficiency,
            'execution_capacity_score': self.calculate_execution_capacity_score(
                state.capacity,
                state.load,
                state.efficiency,
            ),
            'history': [record.model_dump() for record in state.history],
        }

    def forecast_next_months(self, months: int = 3) -> List[Dict[str, object]]:
        state = self.load_state()
        forecast = []
        for month_offset in range(1, months + 1):
            forecast.append(
                {
                    'month_offset': month_offset,
                    'capacity': state.capacity,
                    'load': state.load,
                    'efficiency': state.efficiency,
                    'predicted_execution_capacity_score': self.calculate_execution_capacity_score(
                        state.capacity,
                        state.load,
                        state.efficiency,
                    ),
                }
            )
        return forecast

    def update_monthly_performance(
        self,
        month: int,
        projects_completed: int,
        delays: int,
        kpi_success_rate: float,
        capacity: Optional[float] = None,
        load: Optional[float] = None,
    ) -> Dict[str, object]:
        state = self.load_state()
        record = ExecutionHistoryRecord(
            month=month,
            projects_completed=projects_completed,
            delays=delays,
            kpi_success_rate=kpi_success_rate,
        )
        state.history.append(record)
        if capacity is not None:
            state.capacity = round(capacity, 3)
        if load is not None:
            state.load = round(load, 3)
        state.efficiency = self.calculate_efficiency(state.history)
        self.save_state(state)
        return self.get_current_state()

import json
import os
from typing import List, Dict
from ..models.annual_operations_model import AnnualOperationsModel, MonthlyOperationResult

class AnnualOperationsService:
    def __init__(self):
        self.data_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), '../../../../data/samples')
        )
        self.operations_file = os.path.join(self.data_path, 'annual_operations_model.json')

    def load_operations_model(self) -> AnnualOperationsModel:
        if not os.path.exists(self.operations_file):
            raise FileNotFoundError(f'Operations data not found: {self.operations_file}')

        with open(self.operations_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        return AnnualOperationsModel(**data)

    def simulate_month_operations(self, month: int) -> Dict[str, object]:
        model = self.load_operations_model()
        monthly = next((item for item in model.monthly_operations if item.month == month), None)
        if monthly is None:
            raise ValueError(f'Month {month} is not defined in operations model')

        generated_tasks = []
        generated_incidents = []

        for department, load in monthly.department_load.items():
            task_count = max(1, int(round(monthly.base_tasks.get(department, 1) * load)))
            for index in range(task_count):
                generated_tasks.append({
                    'id': f'{department}_task_{month}_{index + 1}',
                    'title': f'{department} task for month {month}',
                    'department': department,
                    'priority': 'High' if load >= 1.0 else 'Medium',
                    'estimated_hours': 8,
                })

        incident_count = max(0, int(round(monthly.incident_rate * sum(monthly.base_tasks.values()) * 0.5)))
        for index in range(incident_count):
            severity = 'High' if 'peak' in ' '.join(monthly.event_tags).lower() else 'Medium'
            generated_incidents.append({
                'id': f'ops_incident_{month}_{index + 1}',
                'title': f'Operational incident for month {month}',
                'severity': severity,
                'related_events': monthly.event_tags,
            })

        result = MonthlyOperationResult(
            month=month,
            department_load=monthly.department_load,
            generated_tasks=generated_tasks,
            generated_incidents=generated_incidents,
        )
        return result.model_dump()

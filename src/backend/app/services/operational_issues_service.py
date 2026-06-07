import json
import os
import uuid
from typing import Dict, List, Optional

from pydantic import BaseModel

from ..models.operational_issues_model import (
    ImprovementAction,
    IssueDefinition,
    IssueInstance,
    OperationalIssuesModel,
)
from .company_operations_integration_service import CompanyOperationsIntegrationService
from .organization_service import OrganizationService


class TaskInstance(BaseModel):
    id: str
    title: str
    description: str
    owner_department: str
    priority: str
    related_issue_id: str
    task_template_id: Optional[str] = None
    expected_effect: Dict[str, float]


class OperationalIssuesService:
    def __init__(self):
        self.data_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), '../../../../data/samples')
        )
        self.issues_file = os.path.join(self.data_path, 'operational_issues_model.json')
        self.integration_service = CompanyOperationsIntegrationService()
        self.organization_service = OrganizationService()

    def load_issues_model(self) -> OperationalIssuesModel:
        if not os.path.exists(self.issues_file):
            raise FileNotFoundError(f'Operational issues data not found: {self.issues_file}')

        with open(self.issues_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        return OperationalIssuesModel(**data)

    def _is_violation(self, metric_name: str, current_value: float, threshold: float) -> bool:
        if metric_name in [
            'duplicate_revenue_entries',
            'license_processing_days',
            'missing_kpi_count',
        ] or metric_name.endswith('_days') or metric_name.endswith('_entries') or 'missing' in metric_name:
            return current_value > threshold

        if metric_name in ['inventory_turnover', 'allocation_accuracy', 'performance_profit_margin']:
            return current_value < threshold

        if metric_name.endswith('_ratio') or metric_name.endswith('_margin') or metric_name.endswith('_turnover'):
            return current_value < threshold

        return current_value < threshold

    def detect_issues(
        self,
        monthly_state: Dict[str, object],
        company_kpis: Dict[str, float],
        month: int,
    ) -> List[IssueInstance]:
        model = self.load_issues_model()
        issues: List[IssueInstance] = []

        pl_state = monthly_state.get('pl', {})
        pl_kpis = pl_state.get('kpis', {}) if isinstance(pl_state, dict) else {}

        for issue_definition in model.issues:
            detected_values: Dict[str, float] = {}
            triggered = False

            for metric, threshold in issue_definition.detection_rules.items():
                current_value = None

                if metric in company_kpis:
                    current_value = float(company_kpis.get(metric, 0.0))
                elif metric in pl_kpis:
                    current_value = float(pl_kpis.get(metric, 0.0))
                elif isinstance(monthly_state.get('operations'), dict) and metric in monthly_state['operations']:
                    try:
                        current_value = float(monthly_state['operations'][metric])
                    except (TypeError, ValueError):
                        current_value = 0.0

                if current_value is None:
                    current_value = 0.0

                if self._is_violation(metric, current_value, threshold):
                    detected_values[metric] = current_value
                    triggered = True

            if triggered:
                issues.append(
                    IssueInstance(
                        id=f'{issue_definition.id}_{month}',
                        issue_id=issue_definition.id,
                        month=month,
                        detected_values=detected_values,
                        severity=issue_definition.severity,
                        status='Open',
                        recommended_actions=[],
                    )
                )

        org_state = self.organization_service.load_organization_state(month=month)
        return self.organization_service.apply_organization_to_issues(issues, org_state, model.issues)

    def generate_recommendations(
        self,
        issue_instances: List[IssueInstance],
        org_state: Optional[object] = None,
    ) -> List[ImprovementAction]:
        if not issue_instances:
            return []

        model = self.load_issues_model()
        recommendations: List[ImprovementAction] = []

        for issue_instance in issue_instances:
            for action in model.actions:
                if action.issue_id == issue_instance.issue_id:
                    recommendations.append(action)

        if org_state is not None:
            recommendations = self.organization_service.apply_organization_to_improvements(recommendations, org_state)

        return recommendations

    def convert_actions_to_tasks(self, actions: List[ImprovementAction]) -> List[TaskInstance]:
        tasks: List[TaskInstance] = []

        for action in actions:
            priority = 'Medium'
            if any(
                metric.endswith('_days') or metric.startswith('missing') or metric.endswith('_entries')
                for metric in action.expected_effect
            ):
                priority = 'High'

            task = TaskInstance(
                id=str(uuid.uuid4()),
                title=action.name,
                description=action.description,
                owner_department=action.owner_department,
                priority=priority,
                related_issue_id=action.issue_id,
                task_template_id=action.task_template_id,
                expected_effect=action.expected_effect,
            )
            tasks.append(task)

        return tasks

    def simulate_month_with_issues(self, month: int) -> Dict[str, object]:
        if month < 1 or month > 12:
            raise ValueError('month must be between 1 and 12')

        monthly_state = self.integration_service.simulate_month_full(month)
        company_kpis = monthly_state.get('pl', {}).get('kpis', {})
        issues = self.detect_issues(monthly_state, company_kpis, month)
        org_state = self.organization_service.load_organization_state(month=month)
        recommendations = self.generate_recommendations(issues, org_state=org_state)
        generated_tasks = self.convert_actions_to_tasks(recommendations)

        return {
            'month': month,
            'pl': monthly_state.get('pl', {}),
            'operations': monthly_state.get('operations', {}),
            'issues': [issue.model_dump() for issue in issues],
            'recommendations': [action.model_dump() for action in recommendations],
            'generated_tasks': [task.model_dump() for task in generated_tasks],
        }

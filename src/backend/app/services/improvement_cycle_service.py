import json
import os
import uuid
from typing import Dict, List, Optional

from .company_operations_integration_service import CompanyOperationsIntegrationService
from .operational_issues_service import OperationalIssuesService
from .organization_service import OrganizationService
from ..models.improvement_cycle_model import (
    ActionEffectiveness,
    ContinuousImprovementState,
    ImprovementHistory,
)
from ..models.operational_issues_model import ImprovementAction


class ImprovementCycleService:
    def __init__(self, data_path: Optional[str] = None):
        self.data_path = os.path.abspath(
            data_path or os.path.join(os.path.dirname(__file__), '../../../../data/samples')
        )
        self.state_file = os.path.join(self.data_path, 'improvement_cycle_state.json')
        self.operational_service = OperationalIssuesService()
        self.integration_service = CompanyOperationsIntegrationService()
        self.organization_service = OrganizationService()

    def load_cycle_state(self) -> ContinuousImprovementState:
        if not os.path.exists(self.state_file):
            raise FileNotFoundError(f'Improvement cycle state not found: {self.state_file}')

        with open(self.state_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        return ContinuousImprovementState(**data)

    def save_cycle_state(self, state: ContinuousImprovementState) -> None:
        with open(self.state_file, 'w', encoding='utf-8') as f:
            f.write(state.model_dump_json(indent=2, ensure_ascii=False))

    def _calculate_actual_effect(self, previous_kpis: Dict[str, float], current_kpis: Dict[str, float], expected_effect: Dict[str, float]) -> Dict[str, float]:
        actual_effect: Dict[str, float] = {}
        for metric, expected in expected_effect.items():
            prev_value = float(previous_kpis.get(metric, 0.0))
            curr_value = float(current_kpis.get(metric, 0.0))
            actual_effect[metric] = round(curr_value - prev_value, 3)
        return actual_effect

    def _calculate_effect_error(self, expected: Dict[str, float], actual: Dict[str, float]) -> Dict[str, float]:
        return {metric: round(expected.get(metric, 0.0) - actual.get(metric, 0.0), 3) for metric in expected}

    def evaluate_action_effectiveness(
        self,
        previous_month_state: Dict[str, object],
        current_month_state: Dict[str, object],
        executed_actions: List[ImprovementAction],
        current_priorities: Dict[str, float],
    ) -> List[ImprovementHistory]:
        previous_kpis = previous_month_state.get('pl', {}).get('kpis', {})
        current_kpis = current_month_state.get('pl', {}).get('kpis', {})
        histories: List[ImprovementHistory] = []

        for action in executed_actions:
            actual_effect = self._calculate_actual_effect(previous_kpis, current_kpis, action.expected_effect)
            effect_error = self._calculate_effect_error(action.expected_effect, actual_effect)
            priority_score = float(current_priorities.get(action.id, 1.0))

            histories.append(
                ImprovementHistory(
                    id=str(uuid.uuid4()),
                    month=previous_month_state.get('month', 0),
                    issue_id=action.issue_id,
                    action_id=action.id,
                    expected_effect=action.expected_effect,
                    actual_effect=actual_effect,
                    effect_error=effect_error,
                    priority_score=priority_score,
                )
            )

        return histories

    def _normalize_ratio(self, expected: float, actual: float) -> float:
        if expected == 0:
            return 0.0
        return actual / expected if expected != 0 else 0.0

    def update_action_priority(
        self,
        history_list: List[ImprovementHistory],
        priorities: Dict[str, float],
        weight: float = 0.1,
    ) -> Dict[str, float]:
        updated_priorities = priorities.copy()

        for history in history_list:
            expected = history.expected_effect
            actual = history.actual_effect
            metric_scores = []
            metric_errors = []

            for metric, expected_value in expected.items():
                actual_value = actual.get(metric, 0.0)
                metric_scores.append(self._normalize_ratio(expected_value, actual_value))
                metric_errors.append(abs(expected_value - actual_value) / (abs(expected_value) if expected_value != 0 else 1.0))

            effectiveness = sum(metric_scores) / len(metric_scores) if metric_scores else 0.0
            error = sum(metric_errors) / len(metric_errors) if metric_errors else 0.0
            current_priority = float(updated_priorities.get(history.action_id, 1.0))
            new_priority = current_priority + (effectiveness - error) * weight
            new_priority = max(0.1, min(new_priority, 5.0))
            updated_priorities[history.action_id] = round(new_priority, 3)

        return updated_priorities

    def select_actions_by_priority(
        self,
        issues: List[Dict[str, object]],
        priorities: Dict[str, float],
    ) -> List[ImprovementAction]:
        potential_actions = self.operational_service.load_issues_model().actions
        selected: List[ImprovementAction] = []

        issue_ids = {issue.get('issue_id') for issue in issues}
        scored_actions: List[tuple[float, ImprovementAction]] = []

        for action in potential_actions:
            if action.issue_id not in issue_ids:
                continue
            score = priorities.get(action.id, 1.0)
            if any(issue.get('severity') == 'High' and issue.get('issue_id') == action.issue_id for issue in issues):
                score += 0.5
            if action.task_template_id:
                score += 0.1
            scored_actions.append((score, action))

        scored_actions.sort(key=lambda item: item[0], reverse=True)
        selected = [action for _, action in scored_actions[:3]]
        return selected

    def _update_action_effectiveness_records(
        self,
        state: ContinuousImprovementState,
        history_list: List[ImprovementHistory],
        updated_priorities: Dict[str, float],
    ) -> List[ActionEffectiveness]:
        effectiveness_map: Dict[str, ActionEffectiveness] = {
            record.action_id: record for record in state.action_effectiveness
        }

        for history in history_list:
            record = effectiveness_map.get(history.action_id)
            if record is None:
                record = ActionEffectiveness(
                    action_id=history.action_id,
                    total_runs=0,
                    avg_effect={},
                    avg_error={},
                    updated_priority=updated_priorities.get(history.action_id, 1.0),
                )
                effectiveness_map[history.action_id] = record

            record.total_runs += 1
            for metric, actual_value in history.actual_effect.items():
                previous_avg = record.avg_effect.get(metric, 0.0)
                record.avg_effect[metric] = round((previous_avg * (record.total_runs - 1) + actual_value) / record.total_runs, 3)
            for metric, error_value in history.effect_error.items():
                previous_avg_error = record.avg_error.get(metric, 0.0)
                record.avg_error[metric] = round((previous_avg_error * (record.total_runs - 1) + abs(error_value)) / record.total_runs, 3)
            record.updated_priority = updated_priorities.get(history.action_id, record.updated_priority)

        return list(effectiveness_map.values())

    def simulate_month_cycle(self, month: int) -> Dict[str, object]:
        if month < 1 or month > 11:
            raise ValueError('month must be between 1 and 11 to run a full improvement cycle')

        state = self.load_cycle_state()
        first_state = self.integration_service.simulate_month_full(month)
        issues = self.operational_service.detect_issues(
            first_state,
            first_state.get('pl', {}).get('kpis', {}),
            month,
        )
        org_state = self.organization_service.load_organization_state(month=month)
        recommended_actions = self.operational_service.generate_recommendations(issues, org_state=org_state)
        selected_actions = self.select_actions_by_priority(
            [issue.model_dump() for issue in issues],
            state.updated_priorities,
        )
        generated_tasks = self.operational_service.convert_actions_to_tasks(selected_actions)
        second_state = self.integration_service.simulate_month_full(month + 1)

        histories = self.evaluate_action_effectiveness(
            first_state,
            second_state,
            selected_actions,
            state.updated_priorities,
        )
        updated_priorities = self.update_action_priority(histories, state.updated_priorities)
        updated_effectiveness = self._update_action_effectiveness_records(state, histories, updated_priorities)

        state.month = month + 1
        state.executed_actions.extend(histories)
        state.updated_priorities = updated_priorities
        state.action_effectiveness = updated_effectiveness
        self.save_cycle_state(state)

        return {
            'month': month,
            'pl': first_state.get('pl', {}),
            'operations': first_state.get('operations', {}),
            'issues': [issue.model_dump() for issue in issues],
            'actions_executed': [history.model_dump() for history in histories],
            'generated_tasks': [task.model_dump() for task in generated_tasks],
            'effectiveness': [record.model_dump() for record in updated_effectiveness],
            'updated_priorities': updated_priorities,
        }

import json
import os
from copy import deepcopy
from typing import Dict, List, Optional

from ..models.organization import OrganizationModel, OrganizationUnit as LegacyOrganizationUnit
from ..models.organization_model import OpenPosition, OrganizationState, OrganizationUnit
from ..models.operational_issues_model import ImprovementAction


class OrganizationService:
    """組織モデルの読み込みと組織状態からの実行力計測サービス"""

    def __init__(self):
        self.data_path = os.path.abspath(
            os.path.join(os.path.dirname(__file__), '../../../../data/samples')
        )
        self.organization_file = os.path.join(self.data_path, 'organization_horipro.json')
        self.organization_state_file = os.path.join(self.data_path, 'organization_state_sample.json')

    def load_organization_model(self) -> OrganizationModel:
        if not os.path.exists(self.organization_file):
            raise FileNotFoundError(f'Organization data not found: {self.organization_file}')

        with open(self.organization_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        return OrganizationModel(**data)

    def count_total_headcount(self, unit: LegacyOrganizationUnit) -> int:
        child_total = sum(self.count_total_headcount(child) for child in unit.children)
        if unit.children:
            if unit.headcount == child_total:
                return unit.headcount
            return unit.headcount + child_total
        return unit.headcount

    def get_total_company_headcount(self) -> int:
        model = self.load_organization_model()
        return self.count_total_headcount(model.structure)

    def load_organization_state(
        self,
        path: Optional[str] = None,
        month: Optional[int] = None,
    ) -> OrganizationState:
        source_file = path or self.organization_state_file
        if not os.path.exists(source_file):
            raise FileNotFoundError(f'Organization state data not found: {source_file}')

        with open(source_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        state = OrganizationState(**data)
        if month is None or month == state.month:
            return state

        return self.simulate_hiring_and_attrition(state, month)

    def compute_organization_costs(self, org_state: OrganizationState) -> float:
        return round(
            sum(unit.headcount * unit.monthly_cost_per_fte for unit in org_state.units),
            3,
        )

    def estimate_skill_gap(
        self,
        unit: OrganizationUnit,
        business_unit_requirements: Dict[str, float],
    ) -> float:
        if not business_unit_requirements:
            return 0.0

        gaps = []
        for skill, required in business_unit_requirements.items():
            actual = float(unit.skill_profile.get(skill, 0.0))
            gaps.append(max(0.0, required - actual))

        return round(sum(gaps) / max(len(gaps), 1), 3)

    def _default_required_skills(self) -> Dict[str, float]:
        return {
            'creative': 0.7,
            'digital': 0.7,
            'ops': 0.6,
        }

    def _find_relevant_units(
        self,
        org_state: OrganizationState,
        department_names: List[str],
    ) -> List[OrganizationUnit]:
        units: List[OrganizationUnit] = []
        for unit in org_state.units:
            if unit.name in department_names or unit.id in department_names or unit.role in department_names:
                units.append(unit)
                continue
            for name in department_names:
                if name.lower() in unit.name.lower() or name.lower() in unit.role.lower():
                    units.append(unit)
                    break
        return units

    def _find_owner_unit(
        self,
        org_state: OrganizationState,
        owner_department: str,
    ) -> Optional[OrganizationUnit]:
        for unit in org_state.units:
            if unit.name == owner_department or unit.id == owner_department or unit.role == owner_department:
                return unit
            if owner_department.lower() in unit.name.lower() or owner_department.lower() in unit.role.lower():
                return unit
        return None

    def apply_organization_to_issues(
        self,
        issues: List[object],
        org_state: OrganizationState,
        issue_definitions: List[object],
    ) -> List[object]:
        for issue in issues:
            definition = next(
                (item for item in issue_definitions if getattr(item, 'id', None) == issue.issue_id),
                None,
            )
            if definition is None:
                continue

            relevant_units = self._find_relevant_units(
                org_state,
                getattr(definition, 'related_departments', []),
            )
            avg_workload = sum(unit.workload_index for unit in relevant_units) / max(len(relevant_units), 1)
            workload_penalty = max(0.0, avg_workload - 1.0) * 0.5
            avg_skill = sum(
                sum(unit.skill_profile.values()) / max(len(unit.skill_profile), 1)
                for unit in relevant_units
            ) / max(len(relevant_units), 1)
            skill_gap = max(0.0, 0.7 - avg_skill)
            culture_penalty = 0.2 if any(
                'risk_averse' in trait or 'conservative' in trait
                for unit in relevant_units
                for trait in unit.culture_traits
            ) else 0.0

            impact_score = workload_penalty + skill_gap + culture_penalty
            if impact_score > 0.6:
                adjusted_severity = 'Critical'
            elif impact_score > 0.35:
                adjusted_severity = 'High'
            elif impact_score > 0.15:
                adjusted_severity = 'Medium'
            else:
                adjusted_severity = issue.severity

            severity_levels = ['Low', 'Medium', 'High', 'Critical']
            current_index = severity_levels.index(issue.severity) if issue.severity in severity_levels else 0
            adjusted_index = severity_levels.index(adjusted_severity) if adjusted_severity in severity_levels else current_index
            issue.severity = severity_levels[max(current_index, adjusted_index)]

        return issues

    def apply_organization_to_improvements(
        self,
        improvements: List[ImprovementAction],
        org_state: OrganizationState,
    ) -> List[ImprovementAction]:
        for action in improvements:
            owner_unit = self._find_owner_unit(org_state, action.owner_department)
            skill_factor = 0.7
            headcount_factor = 0.7
            automation_boost = 1.0
            workload_penalty = 0.2

            if owner_unit is not None:
                skill_factor = max(
                    0.3,
                    1.0 - self.estimate_skill_gap(owner_unit, self._default_required_skills()),
                )
                headcount_factor = min(2.0, max(0.5, owner_unit.headcount / max(4.0, 1.0)))
                automation_boost = 1.0 + owner_unit.automation_index * 0.5
                workload_penalty = max(0.0, owner_unit.workload_index - 1.0) * 0.5

            effectiveness = max(0.6, min(1.3, skill_factor * (1.0 - workload_penalty) * automation_boost))
            for metric, value in action.expected_effect.items():
                action.expected_effect[metric] = round(value * effectiveness, 3)

            estimated_months = max(1.0, 4.0 / max(0.1, headcount_factor * skill_factor * automation_boost))
            action.description = f"{action.description} (推定実行期間: {estimated_months:.1f}か月)"

        return improvements

    def simulate_hiring_and_attrition(
        self,
        org_state: OrganizationState,
        month: int,
        hiring_actions: Optional[List[Dict[str, object]]] = None,
    ) -> OrganizationState:
        state = deepcopy(org_state)
        if month < state.month:
            state.month = month
            return state

        for unit in state.units:
            lost = int(round(unit.headcount * unit.attrition_rate))
            unit.headcount = max(1, unit.headcount - lost)

        if hiring_actions:
            for action in hiring_actions:
                state.open_positions.append(OpenPosition(**action))

        remaining_positions: List[OpenPosition] = []
        for open_position in state.open_positions:
            if isinstance(open_position, dict):
                open_position = OpenPosition(**open_position)

            unit = next((u for u in state.units if u.id == open_position.unit_id), None)
            if unit is None:
                remaining_positions.append(open_position)
                continue
            if month - open_position.posted_month >= unit.time_to_hire_months:
                unit.headcount += 1
            else:
                remaining_positions.append(open_position)

        state.open_positions = remaining_positions
        state.month = month
        return state

    def estimate_execution_capacity(
        self,
        org_state: OrganizationState,
        business_unit_id: str,
    ) -> float:
        candidates = [
            unit for unit in org_state.units
            if business_unit_id in unit.dependency_links
            or business_unit_id in unit.id
            or business_unit_id in unit.role.lower()
            or business_unit_id in unit.name.lower()
        ]

        if not candidates:
            baseline = sum(unit.headcount * unit.fte_capacity for unit in org_state.units)
            return round(min(1.0, baseline / 40.0), 3)

        capacity = 0.0
        for unit in candidates:
            unit_capacity = (
                unit.headcount
                * unit.fte_capacity
                * max(0.1, 1.0 - max(0.0, unit.workload_index - 1.0) * 0.25)
                * (1.0 + unit.automation_index * 0.2)
            )
            capacity += unit_capacity

        return round(min(1.0, capacity / 20.0), 3)

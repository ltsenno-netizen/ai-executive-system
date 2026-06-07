import os
import sys
from copy import deepcopy

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'backend')))

from app.services.organization_service import OrganizationService
from app.services.executive_dashboard_service import ExecutiveDashboardService
from app.models.operational_issues_model import IssueInstance, ImprovementAction


def test_load_organization_state():
    service = OrganizationService()
    state = service.load_organization_state()

    assert state.month == 7
    assert len(state.units) >= 4
    assert state.open_positions


def test_compute_organization_costs():
    service = OrganizationService()
    state = service.load_organization_state()
    cost = service.compute_organization_costs(state)

    assert cost > 0
    assert isinstance(cost, float)


def test_apply_organization_to_issues_increases_severity_for_heavy_load():
    service = OrganizationService()
    state = service.load_organization_state()
    issue = IssueInstance(
        id='test_issue_1',
        issue_id='weak_performance_profit_margin',
        month=7,
        detected_values={'performance_profit_margin': 0.08},
        severity='Medium',
        status='Open',
        recommended_actions=[],
    )
    from app.models.operational_issues_model import IssueDefinition

    issue_def = IssueDefinition(
        id='weak_performance_profit_margin',
        name='公演採算管理の弱さ',
        description='Test',
        detection_rules={'performance_profit_margin': 0.10},
        severity='Medium',
        related_departments=['公演事業本部'],
    )
    adjusted = service.apply_organization_to_issues([issue], state, [issue_def])

    assert adjusted[0].severity in {'Medium', 'High', 'Critical'}
    assert adjusted[0].severity != 'Low'


def test_apply_organization_to_improvements_scales_effect():
    service = OrganizationService()
    state = service.load_organization_state()
    action = ImprovementAction(
        id='test_action_1',
        issue_id='weak_performance_profit_margin',
        name='Test Task',
        description='Test improvement',
        owner_department='公演事業本部',
        expected_effect={'performance_profit_margin': 0.03},
    )
    updated = service.apply_organization_to_improvements([action], state)

    assert updated[0].expected_effect['performance_profit_margin'] != 0.03


def test_simulate_hiring_and_attrition_changes_headcount():
    service = OrganizationService()
    state = service.load_organization_state()
    state_with_action = deepcopy(state)
    state_with_action.open_positions.append({
        'unit_id': 'digital',
        'role': 'data_engineer',
        'posted_month': 5,
    })

    next_state = service.simulate_hiring_and_attrition(state_with_action, 8)
    digital_unit = next((u for u in next_state.units if u.id == 'digital'), None)

    assert digital_unit is not None
    assert digital_unit.headcount >= 12


def test_dashboard_includes_organization_summary():
    service = ExecutiveDashboardService()
    dashboard = service.build_dashboard(7)

    assert dashboard.organization_summary is not None
    assert len(dashboard.organization_summary.units) >= 1
    assert all(hasattr(unit, 'monthly_personnel_cost') for unit in dashboard.organization_summary.units)

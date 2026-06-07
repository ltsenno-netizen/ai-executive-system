import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'backend')))

from app.services.operational_issues_service import OperationalIssuesService


def test_detect_issues_thresholds():
    service = OperationalIssuesService()
    monthly_state = {
        'pl': {
            'kpis': {
                'performance_profit_margin': 0.08,
                'license_processing_days': 35,
                'inventory_turnover': 0.8,
                'allocation_accuracy': 0.75,
                'duplicate_revenue_entries': 2,
                'missing_kpi_count': 4,
            }
        },
        'operations': {},
    }
    issues = service.detect_issues(monthly_state, monthly_state['pl']['kpis'], 7)

    assert any(issue.issue_id == 'weak_performance_profit_margin' for issue in issues)
    assert any(issue.issue_id == 'license_processing_delay' for issue in issues)
    assert any(issue.issue_id == 'md_inventory_risk' for issue in issues)
    assert any(issue.issue_id == 'insufficient_data_infrastructure' for issue in issues)
    assert any(issue.issue_id == 'allocation_accuracy_ambiguity' for issue in issues)


def test_generate_recommendations_and_tasks():
    service = OperationalIssuesService()
    monthly_state = {
        'pl': {
            'kpis': {
                'performance_profit_margin': 0.08,
                'license_processing_days': 35,
                'inventory_turnover': 0.8,
                'allocation_accuracy': 0.75,
                'duplicate_revenue_entries': 2,
                'missing_kpi_count': 4,
            }
        },
        'operations': {},
    }
    issues = service.detect_issues(monthly_state, monthly_state['pl']['kpis'], 7)
    recommendations = service.generate_recommendations(issues)
    tasks = service.convert_actions_to_tasks(recommendations)

    assert len(recommendations) >= 1
    assert all(action.issue_id in {issue.issue_id for issue in issues} for action in recommendations)
    assert len(tasks) == len(recommendations)
    assert all(task.owner_department for task in tasks)
    assert all(task.related_issue_id for task in tasks)


def test_simulate_month_with_issues():
    service = OperationalIssuesService()
    result = service.simulate_month_with_issues(7)

    assert result['month'] == 7
    assert 'pl' in result
    assert 'operations' in result
    assert 'issues' in result
    assert 'recommendations' in result
    assert 'generated_tasks' in result
    assert isinstance(result['issues'], list)
    assert isinstance(result['generated_tasks'], list)

import csv
import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'backend')))

from app.services.company_operations_integration_service import CompanyOperationsIntegrationService
from app.services.external_environment_service import ExternalEnvironmentService
from app.services.financial_service import FinancialService


OUTPUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'samples', 'scenario_outputs'))

SCENARIOS = [
    {
        'id': 'scenario_base',
        'name': 'Base Case',
        'events': [],
        'investment_requests': [],
        'revenue_multiplier': 1.0,
    },
    {
        'id': 'scenario_downside',
        'name': 'Downside',
        'events': [
            {
                'id': 'shock_stage_market_drop',
                'date': '2026-01-01',
                'type': 'market_shock',
                'impact_map': {'stage_market': -0.30},
                'duration_months': 2,
                'source': 'scenario',
                'notes': 'Stage market drop 30%',
            }
        ],
        'investment_requests': [],
        'revenue_multiplier': 0.80,
    },
    {
        'id': 'scenario_upside',
        'name': 'Upside',
        'events': [
            {
                'id': 'shock_ai_solutions_rise',
                'date': '2026-01-01',
                'type': 'market_opportunity',
                'impact_map': {'ai_solutions': 0.30, 'digital_distribution_market': 0.20},
                'duration_months': 12,
                'source': 'scenario',
                'notes': 'AI demand +30%, digital ad recovery +20%',
            }
        ],
        'investment_requests': [],
        'revenue_multiplier': 1.0,
    },
    {
        'id': 'scenario_simultaneous',
        'name': 'Simultaneous Shocks + Large Investment',
        'events': [
            {
                'id': 'shock_stage_market_drop',
                'date': '2026-01-01',
                'type': 'market_shock',
                'impact_map': {'stage_market': -0.30},
                'duration_months': 2,
                'source': 'scenario',
                'notes': 'Stage market shock with large investment',
            }
        ],
        'investment_requests': [
            {
                'id': 'req-large-investment-202601',
                'business_unit_id': 'bu_ai_solutions',
                'requested_amount': 3.0,
                'expected_return_rate': 0.18,
                'payback_period_months': 24,
                'strategic_priority': 4,
                'requested_by': 'head_of_ai',
                'requested_month': 1,
            }
        ],
        'revenue_multiplier': 0.82,
    },
]


def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def save_json(path: str, data: Dict) -> None:
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def save_csv(path: str, rows: List[Dict[str, object]], fieldnames: List[str]) -> None:
    with open(path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def run_scenario(scenario: Dict[str, object]) -> Dict[str, object]:
    env_service = ExternalEnvironmentService()
    integration_service = CompanyOperationsIntegrationService()
    financial_service = FinancialService()

    scenario_results = []
    monthly_profits = []
    monthly_cash_balances = []
    monthly_cash_changes = []
    monthly_flows = []

    for year in [2026, 2027]:
        for month in range(1, 13):
            environment_state = env_service.build_environment_state(month, year, extra_events=scenario['events'])
            monthly_result = integration_service.simulate_month_full(month, year=year, environment_state=environment_state)
            pl = monthly_result['pl']
            revenue = float(sum(pl.get('revenue', {}).values()) if isinstance(pl.get('revenue', {}), dict) else pl.get('revenue', 0.0))
            adjusted_revenue = round(revenue * scenario['revenue_multiplier'], 3)
            pl['revenue'] = adjusted_revenue
            pl['profit'] = round(pl.get('profit', 0.0) * scenario['revenue_multiplier'], 3)
            pl['profit_margin'] = round((pl['profit'] / adjusted_revenue) if adjusted_revenue else 0.0, 3)

            finance = financial_service.calculate_monthly_free_cash_flow(pl, financial_service.load_financials())
            request_decisions = []
            if scenario['investment_requests']:
                for request_payload in scenario['investment_requests']:
                    from app.models.financial_model import InvestmentRequest
                    request = InvestmentRequest(**request_payload)
                    decision = financial_service.evaluate_investment_request(request, finance)
                    finance = financial_service.apply_investment_decision(decision, finance)
                    request_decisions.append(decision.model_dump())

            finance.cash_reserves = round(max(0.0, finance.cash_reserves + finance.free_cash_flow), 3)

            scenario_results.append({
                'scenario_id': scenario['id'],
                'month': month,
                'year': year,
                'revenue': adjusted_revenue,
                'profit': float(pl.get('profit', 0.0)),
                'profit_margin': float(pl.get('profit_margin', 0.0)),
                'cash_reserves': float(finance.cash_reserves),
                'free_cash_flow': float(finance.free_cash_flow),
                'investment_requests': request_decisions,
                'active_events': environment_state.get('active_events', []),
            })
            monthly_profits.append(float(pl.get('profit', 0.0)))
            monthly_cash_balances.append(float(finance.cash_reserves))
            monthly_cash_changes.append(float(finance.free_cash_flow))
            monthly_flows.append(float(pl.get('profit', 0.0)))

    return {
        'scenario_id': scenario['id'],
        'name': scenario['name'],
        'monthly': scenario_results,
        'summary': {
            'p50_profit': _quantile(monthly_profits, 0.5),
            'p10_profit': _quantile(monthly_profits, 0.1),
            'p90_profit': _quantile(monthly_profits, 0.9),
            'p50_cash': _quantile(monthly_cash_balances, 0.5),
            'p10_cash': _quantile(monthly_cash_balances, 0.1),
            'p90_cash': _quantile(monthly_cash_balances, 0.9),
            'final_cash': monthly_cash_balances[-1] if monthly_cash_balances else 0.0,
            'min_cash': min(monthly_cash_balances) if monthly_cash_balances else 0.0,
            'max_cash': max(monthly_cash_balances) if monthly_cash_balances else 0.0,
        },
    }


def _quantile(values: List[float], quantile: float) -> float:
    if not values:
        return 0.0
    sorted_values = sorted(values)
    index = min(len(values) - 1, max(0, int(round((len(values) - 1) * quantile))))
    return round(sorted_values[index], 3)


def main() -> None:
    ensure_dir(OUTPUT_DIR)
    comparison_rows = []
    generated = []

    for scenario in SCENARIOS:
        result = run_scenario(scenario)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        json_path = os.path.join(OUTPUT_DIR, f"{scenario['id']}_summary_{timestamp}.json")
        csv_path = os.path.join(OUTPUT_DIR, f"{scenario['id']}_monthly_{timestamp}.csv")
        save_json(json_path, result)

        fieldnames = [
            'scenario_id',
            'name',
            'year',
            'month',
            'revenue',
            'profit',
            'profit_margin',
            'cash_reserves',
            'free_cash_flow',
            'active_event_count',
        ]
        csv_rows = []
        for entry in result['monthly']:
            csv_rows.append({
                'scenario_id': entry['scenario_id'],
                'name': scenario['name'],
                'year': entry['year'],
                'month': entry['month'],
                'revenue': entry['revenue'],
                'profit': entry['profit'],
                'profit_margin': entry['profit_margin'],
                'cash_reserves': entry['cash_reserves'],
                'free_cash_flow': entry['free_cash_flow'],
                'active_event_count': len(entry['active_events']),
            })
        save_csv(csv_path, csv_rows, fieldnames)

        comparison_rows.append({
            'scenario_id': result['scenario_id'],
            'name': result['name'],
            'final_cash': result['summary']['final_cash'],
            'min_cash': result['summary']['min_cash'],
            'p50_cash': result['summary']['p50_cash'],
            'p10_cash': result['summary']['p10_cash'],
            'p90_cash': result['summary']['p90_cash'],
            'p50_profit': result['summary']['p50_profit'],
            'p10_profit': result['summary']['p10_profit'],
            'p90_profit': result['summary']['p90_profit'],
        })
        generated.append({'json': json_path, 'csv': csv_path})
        print(f'Generated {json_path} and {csv_path}')

    comparison_path = os.path.join(OUTPUT_DIR, f'comparison_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv')
    save_csv(comparison_path, comparison_rows, list(comparison_rows[0].keys()) if comparison_rows else [])
    print(f'Comparison saved to {comparison_path}')
    print('Generated output files:')
    for item in generated:
        print('  -', item)


if __name__ == '__main__':
    main()

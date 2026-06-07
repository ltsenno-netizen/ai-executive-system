import argparse
import csv
import json
import os
import sys
from datetime import datetime
from itertools import product
from typing import Dict, List, Optional

ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
sys.path.append(os.path.join(ROOT_DIR, 'src', 'backend'))

from app.models.financial_model import FinancialFundamentals, InvestmentRequest
from app.services.company_operations_integration_service import CompanyOperationsIntegrationService
from app.services.external_environment_service import ExternalEnvironmentService
from app.services.financial_service import FinancialService

OUTPUT_DIR = os.path.join(ROOT_DIR, 'sensitivity_outputs')
DEFAULT_YEAR = 2026


def build_parameter_grid(
    max_pct_values: List[float],
    min_cash_values: List[float],
    shock_strength_values: List[float],
    shock_duration_values: List[int],
) -> List[Dict[str, object]]:
    return [
        {
            'max_pct': max_pct,
            'min_cash': min_cash,
            'shock_strength': shock_strength,
            'shock_duration': shock_duration,
        }
        for max_pct, min_cash, shock_strength, shock_duration in product(
            max_pct_values,
            min_cash_values,
            shock_strength_values,
            shock_duration_values,
        )
    ]


def format_scenario_id(params: Dict[str, object]) -> str:
    return (
        f"maxpct-{params['max_pct']:.2f}"
        f"_mincash-{params['min_cash']:.1f}"
        f"_strength-{int(abs(params['shock_strength']) * 100)}"
        f"_duration-{params['shock_duration']}"
    )


def build_market_shock_event(
    shock_strength: float,
    shock_duration_months: int,
    start_month: int = 3,
    year: int = DEFAULT_YEAR,
) -> Dict[str, object]:
    environment_service = ExternalEnvironmentService()
    segments = environment_service.load_external_environment().segments
    impact_map = {segment.id: shock_strength for segment in segments}

    return {
        'id': f'sensitivity_shock_{int(abs(shock_strength) * 100)}_{shock_duration_months}',
        'date': f'{year}-{start_month:02d}-01',
        'type': 'market',
        'impact_map': impact_map,
        'duration_months': shock_duration_months,
        'source': 'sensitivity_batch',
        'notes': f'Market shock {shock_strength:.0%} for {shock_duration_months} months',
    }


def simulate_policy_scenario(
    params: Dict[str, object],
    output_dir: str = OUTPUT_DIR,
    months: int = 24,
    shock_start_month: int = 3,
) -> Dict[str, object]:
    os.makedirs(output_dir, exist_ok=True)
    integration_service = CompanyOperationsIntegrationService()
    finance_service = FinancialService()

    scenario_id = format_scenario_id(params)
    event_template = build_market_shock_event(
        shock_strength=params['shock_strength'],
        shock_duration_months=params['shock_duration'],
        start_month=shock_start_month,
        year=DEFAULT_YEAR,
    )

    monthly_rows: List[Dict[str, object]] = []
    approvals = 0
    rejections = 0
    deferrals = 0
    tranche_delays = 0
    cash_balances: List[float] = []
    free_cash_flows: List[float] = []

    for step in range(months):
        year = DEFAULT_YEAR + (step // 12)
        month = (step % 12) + 1
        event = dict(event_template)
        event['date'] = f'{year}-{shock_start_month:02d}-01'

        environment_state = integration_service.environment_service.build_environment_state(
            month,
            year,
            extra_events=[event],
        )

        result = integration_service.simulate_month_full(
            month,
            year=year,
            environment_state=environment_state,
        )

        cash_balance = float(result.get('pl', {}).get('cash_balance', 0.0))
        free_cash_flow = float(result.get('financials', {}).get('free_cash_flow', 0.0))
        cash_balances.append(cash_balance)
        free_cash_flows.append(free_cash_flow)

        monthly_rows.append(
            {
                'year': year,
                'month': month,
                'final_cash': cash_balance,
                'free_cash_flow': free_cash_flow,
                'revenue': float(sum(result.get('pl', {}).get('revenue', {}).values())),
                'profit': float(result.get('pl', {}).get('profit', 0.0)),
                'min_cash_threshold': params['min_cash'],
                'max_investment_pct_of_cash': params['max_pct'],
                'shock_strength': params['shock_strength'],
                'shock_duration': params['shock_duration'],
            }
        )

        sample_financials = finance_service.load_financials()
        sample_financials.cash_reserves = cash_balance
        sample_financials.minimum_cash_threshold = float(params['min_cash'])
        sample_financials.investment_policy['max_investment_pct_of_cash'] = float(params['max_pct'])

        synthetic_request = InvestmentRequest(
            id=f'synth-{step + 1}',
            business_unit_id='bu_sensitivity',
            requested_amount=max(1.0, round(cash_balance * 0.15, 3)),
            expected_return_rate=0.18,
            payback_period_months=24,
            strategic_priority=3,
            requested_month=month,
            tranche_count=3,
            tranche_interval_months=1,
        )

        decision = finance_service.evaluate_investment_request(synthetic_request, sample_financials)
        if decision.decision == 'Approved' or decision.decision == 'Partial':
            approvals += 1
        elif decision.decision == 'Rejected':
            rejections += 1
        elif decision.decision == 'Deferred':
            deferrals += 1

        if decision.tranche_schedule and any(item.get('status') == 'deferred' for item in decision.tranche_schedule):
            tranche_delays += 1

    summary = {
        'params': {
            'max_pct': float(params['max_pct']),
            'min_cash_threshold': float(params['min_cash']),
            'shock_strength': float(params['shock_strength']),
            'shock_duration': int(params['shock_duration']),
        },
        'results': {
            'final_cash': round(cash_balances[-1] if cash_balances else 0.0, 3),
            'min_cash': round(min(cash_balances) if cash_balances else 0.0, 3),
            'avg_fcf': round(sum(free_cash_flows) / len(free_cash_flows), 3) if free_cash_flows else 0.0,
            'approvals': approvals,
            'rejections': rejections,
            'tranche_delays': tranche_delays,
            'deferred': deferrals,
        },
    }

    csv_path = os.path.join(output_dir, f'scenario_{scenario_id}_monthly.csv')
    json_path = os.path.join(output_dir, f'scenario_{scenario_id}_summary.json')

    with open(csv_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(monthly_rows[0].keys()))
        writer.writeheader()
        writer.writerows(monthly_rows)

    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    return {'csv_path': csv_path, 'json_path': json_path, 'summary': summary}


def run_batch(
    max_pct_values: List[float],
    min_cash_values: List[float],
    shock_strength_values: List[float],
    shock_duration_values: List[int],
    output_dir: str = OUTPUT_DIR,
    months: int = 24,
    small_set: bool = False,
) -> List[Dict[str, object]]:
    if small_set:
        max_pct_values = max_pct_values[:2]
        min_cash_values = min_cash_values[:2]
        shock_strength_values = shock_strength_values[:1]
        shock_duration_values = shock_duration_values[:1]

    params_grid = build_parameter_grid(
        max_pct_values,
        min_cash_values,
        shock_strength_values,
        shock_duration_values,
    )

    results = []
    for params in params_grid:
        print(f"Running scenario: {format_scenario_id(params)}")
        results.append(simulate_policy_scenario(params, output_dir=output_dir, months=months))
    return results


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Run sensitivity analysis batch for 24-month simulations.')
    parser.add_argument('--output-dir', default=OUTPUT_DIR, help='Directory to write sensitivity outputs.')
    parser.add_argument('--small-set', action='store_true', help='Run a smaller subset of scenarios for testing.')
    return parser.parse_args()


def main() -> None:
    args = parse_arguments()
    max_pct_values = [0.10, 0.15, 0.20, 0.25, 0.30, 0.35]
    min_cash_values = [2.0, 3.0, 4.0, 5.0]
    shock_strength_values = [-0.10, -0.20, -0.30, -0.40]
    shock_duration_values = [1, 2, 3, 4, 5, 6]

    run_batch(
        max_pct_values,
        min_cash_values,
        shock_strength_values,
        shock_duration_values,
        output_dir=args.output_dir,
        months=24,
        small_set=args.small_set,
    )


if __name__ == '__main__':
    main()

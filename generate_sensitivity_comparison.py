import csv
import glob
import json
import os
from datetime import datetime

ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
OUTPUT_DIR = os.path.join(ROOT_DIR, 'sensitivity_outputs')


def load_summary_files(output_dir: str = OUTPUT_DIR):
    pattern = os.path.join(output_dir, 'scenario_*_summary.json')
    for path in glob.glob(pattern):
        with open(path, 'r', encoding='utf-8') as f:
            yield json.load(f)


def generate_comparison_csv(output_dir: str = OUTPUT_DIR) -> str:
    summaries = list(load_summary_files(output_dir=output_dir))
    if not summaries:
        raise FileNotFoundError(f'No summary files found in {output_dir}')

    timestamp = datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
    filename = f'comparison_sensitivity_{timestamp}.csv'
    csv_path = os.path.join(output_dir, filename)

    fieldnames = [
        'max_pct',
        'min_cash_threshold',
        'shock_strength',
        'shock_duration',
        'final_cash',
        'min_cash',
        'avg_fcf',
        'approvals',
        'rejections',
        'tranche_delays',
        'deferred',
    ]

    with open(csv_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for summary in summaries:
            row = {
                'max_pct': summary['params']['max_pct'],
                'min_cash_threshold': summary['params']['min_cash_threshold'],
                'shock_strength': summary['params']['shock_strength'],
                'shock_duration': summary['params']['shock_duration'],
                'final_cash': summary['results']['final_cash'],
                'min_cash': summary['results']['min_cash'],
                'avg_fcf': summary['results']['avg_fcf'],
                'approvals': summary['results'].get('approvals', 0),
                'rejections': summary['results'].get('rejections', 0),
                'tranche_delays': summary['results'].get('tranche_delays', 0),
                'deferred': summary['results'].get('deferred', 0),
            }
            writer.writerow(row)

    return csv_path


def main() -> None:
    output_path = generate_comparison_csv()
    print(f'Comparison CSV generated: {output_path}')


if __name__ == '__main__':
    main()

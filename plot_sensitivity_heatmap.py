import csv
import os
import sys
from collections import defaultdict
from datetime import datetime
from typing import Dict, List, Optional

ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
OUTPUT_DIR = os.path.join(ROOT_DIR, 'sensitivity_outputs')

try:
    import matplotlib.pyplot as plt
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False


def load_comparison_rows(output_dir: str = OUTPUT_DIR) -> List[Dict[str, object]]:
    path = next(
        (
            os.path.join(output_dir, name)
            for name in os.listdir(output_dir)
            if name.startswith('comparison_sensitivity_') and name.endswith('.csv')
        ),
        None,
    )
    if path is None:
        raise FileNotFoundError('No comparison CSV found in sensitivity_outputs/')

    rows = []
    with open(path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append({
                'max_pct': float(row['max_pct']),
                'min_cash_threshold': float(row['min_cash_threshold']),
                'shock_strength': float(row['shock_strength']),
                'shock_duration': int(row['shock_duration']),
                'final_cash': float(row['final_cash']),
                'min_cash': float(row['min_cash']),
            })
    return rows, path


def build_heatmap_data(rows: List[Dict[str, object]], value_key: str = 'min_cash') -> Dict[str, object]:
    grid = defaultdict(lambda: defaultdict(list))
    for row in rows:
        grid[row['min_cash_threshold']][row['max_pct']].append(row[value_key])

    x_values = sorted({row['max_pct'] for row in rows})
    y_values = sorted({row['min_cash_threshold'] for row in rows})
    z_values = []
    for y in y_values:
        z_row = []
        for x in x_values:
            values = grid[y][x]
            z_row.append(sum(values) / len(values) if values else 0.0)
        z_values.append(z_row)

    return {
        'x': x_values,
        'y': y_values,
        'z': z_values,
        'value_key': value_key,
    }


def save_heatmap_image(data: Dict[str, object], output_dir: str = OUTPUT_DIR) -> str:
    if not HAS_MATPLOTLIB:
        raise ImportError('matplotlib is required to generate heatmap images. Install it with pip install matplotlib')

    x = data['x']
    y = data['y']
    z = data['z']
    value_key = data['value_key']

    fig, ax = plt.subplots(figsize=(8, 6))
    heatmap = ax.imshow(z, cmap='viridis', aspect='auto', origin='lower')
    ax.set_xticks(range(len(x)))
    ax.set_xticklabels([f'{value:.2f}' for value in x], rotation=45)
    ax.set_yticks(range(len(y)))
    ax.set_yticklabels([f'{value:.1f}' for value in y])
    ax.set_xlabel('max_investment_pct_of_cash')
    ax.set_ylabel('minimum_cash_threshold')
    ax.set_title(f'Sensitivity heatmap ({value_key})')
    fig.colorbar(heatmap, ax=ax, label=value_key)

    timestamp = datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
    filename = f'sensitivity_heatmap_{value_key}_{timestamp}.png'
    output_path = os.path.join(output_dir, filename)
    fig.tight_layout()
    fig.savefig(output_path)
    plt.close(fig)

    return output_path


def main(value_key: Optional[str] = 'min_cash') -> None:
    rows, csv_path = load_comparison_rows()
    print(f'Loaded comparison CSV: {csv_path}')
    heatmap_data = build_heatmap_data(rows, value_key=value_key)
    if not HAS_MATPLOTLIB:
        print('matplotlib not installed. Heatmap data prepared, but image generation is skipped.')
        print('Install matplotlib and rerun to generate PNG output.')
        return
    output_path = save_heatmap_image(heatmap_data)
    print(f'Heatmap image generated: {output_path}')


if __name__ == '__main__':
    main()

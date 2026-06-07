import os
import sys
import tempfile
import unittest

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from run_sensitivity_batch import (
    build_parameter_grid,
    run_batch,
)
from generate_sensitivity_comparison import generate_comparison_csv


class SensitivityBatchTest(unittest.TestCase):
    def test_build_parameter_grid(self):
        grid = build_parameter_grid([0.1, 0.15], [2.0, 3.0], [-0.1], [1])
        self.assertEqual(len(grid), 4)
        params = grid[0]
        self.assertIn('max_pct', params)
        self.assertIn('min_cash', params)
        self.assertIn('shock_strength', params)
        self.assertIn('shock_duration', params)

    def test_run_small_batch_generates_files(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            results = run_batch(
                max_pct_values=[0.1, 0.15],
                min_cash_values=[2.0, 3.0],
                shock_strength_values=[-0.1],
                shock_duration_values=[1],
                output_dir=temp_dir,
                months=2,
                small_set=False,
            )

            self.assertEqual(len(results), 4)
            for result in results:
                self.assertTrue(os.path.exists(result['csv_path']))
                self.assertTrue(os.path.exists(result['json_path']))
                self.assertEqual(result['summary']['params']['shock_duration'], 1)
                self.assertIn('final_cash', result['summary']['results'])

    def test_comparison_csv_generation(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            run_batch(
                max_pct_values=[0.1, 0.15],
                min_cash_values=[2.0, 3.0],
                shock_strength_values=[-0.1],
                shock_duration_values=[1],
                output_dir=temp_dir,
                months=2,
                small_set=False,
            )
            csv_path = generate_comparison_csv(output_dir=temp_dir)
            self.assertTrue(os.path.exists(csv_path))
            with open(csv_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            self.assertGreaterEqual(len(lines), 2)
            self.assertIn('max_pct', lines[0])


if __name__ == '__main__':
    unittest.main()

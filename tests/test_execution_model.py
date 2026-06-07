import os
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'backend')))

from fastapi.testclient import TestClient
from app.main import app
from app.models.execution_model import ExecutionRequirement
from app.services.execution_capacity_service import ExecutionCapacityService
from app.routes import execution as execution_route


class ExecutionCapacityModelTest(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.service = ExecutionCapacityService(data_path=self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_calculate_capacity_load_efficiency(self):
        capacity = self.service.calculate_capacity(20.0, 15.0, 1.5)
        self.assertAlmostEqual(capacity, 10.0 + 20.0 * 0.05 + 15.0 * 0.1 + 1.5, places=3)

        requirements = [
            ExecutionRequirement(investment_request_id='req-1', required_capacity=1.0, duration_months=2),
            ExecutionRequirement(investment_request_id='req-2', required_capacity=2.5, duration_months=3),
        ]
        load = self.service.calculate_load(requirements)
        self.assertEqual(load, 3.5)

        state = self.service.load_state()
        efficiency = self.service.calculate_efficiency(state.history)
        self.assertGreaterEqual(efficiency, 0.0)
        self.assertLessEqual(efficiency, 1.0)

    def test_update_monthly_performance(self):
        result = self.service.update_monthly_performance(
            month=202604,
            projects_completed=4,
            delays=1,
            kpi_success_rate=0.8,
            capacity=12.0,
            load=5.0,
        )
        self.assertEqual(result['capacity'], 12.0)
        self.assertEqual(result['load'], 5.0)
        self.assertIn('execution_capacity_score', result)
        self.assertEqual(len(result['history']), 1)

    def test_execution_api_routes(self):
        execution_route.service = ExecutionCapacityService(data_path=self.temp_dir.name)
        client = TestClient(app)

        response = client.get('/api/execution/state')
        self.assertEqual(response.status_code, 200)
        self.assertIn('execution_capacity_score', response.json())

        update_response = client.post(
            '/api/execution/update',
            json={
                'month': 202604,
                'projects_completed': 2,
                'delays': 0,
                'kpi_success_rate': 0.9,
                'capacity': 11.0,
                'load': 3.0,
            },
        )
        self.assertEqual(update_response.status_code, 200)
        self.assertEqual(update_response.json()['capacity'], 11.0)

        forecast_response = client.get('/api/execution/forecast')
        self.assertEqual(forecast_response.status_code, 200)
        self.assertEqual(len(forecast_response.json()), 3)


if __name__ == '__main__':
    unittest.main()

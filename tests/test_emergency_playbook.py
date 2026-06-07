import os
import sys
import json
import unittest
from copy import deepcopy
from unittest.mock import patch

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'backend')))

from fastapi.testclient import TestClient
from app.main import app
from app.models.financial_model import FinancialFundamentals
from app.services.financial_service import FinancialService

client = TestClient(app)


class EmergencyPlaybookTest(unittest.TestCase):
    def setUp(self):
        self.service = FinancialService()
        self.financials = deepcopy(self.service.load_financials())

    def test_generate_emergency_playbook_triggered(self):
        self.financials.cash_reserves = 1.5
        playbook = self.service.generate_emergency_playbook(self.financials)

        self.assertEqual(playbook['trigger'], 'cash_below_threshold')
        self.assertEqual(playbook['status'], 'critical')
        self.assertIn('suspend_tranches', [item['id'] for item in playbook['actions']])

    def test_build_emergency_alert_templates(self):
        self.financials.cash_reserves = 1.5
        playbook = self.service.generate_emergency_playbook(self.financials)
        templates = self.service.build_emergency_alert_templates(playbook)

        self.assertIn('Emergency Triggered', templates['slack'])
        self.assertIn('Current: 1.5', templates['email_body'])
        self.assertIn('POST /api/financials/execute-playbook', templates['email_body'])

    @patch('app.services.notification_service.send_slack_alert')
    @patch('app.services.notification_service.send_email_alert')
    def test_dispatch_emergency_alerts(self, mock_email, mock_slack):
        self.financials.cash_reserves = 1.5
        playbook = self.service.generate_emergency_playbook(self.financials)
        self.service.dispatch_emergency_alerts(playbook)

        mock_slack.assert_called_once()
        mock_email.assert_called_once()

    def test_execute_playbook_endpoint(self):
        response = client.post('/api/financials/execute-playbook', json={'actions': ['suspend_tranches', 'reduce_production_cost']})
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body['status'], 'executed')
        self.assertEqual(body['executed_actions'], ['suspend_tranches', 'reduce_production_cost'])
        self.assertIn('timestamp', body)

    def test_execute_playbook_logs_execution(self):
        log_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'samples', 'executed_playbook_log.json'))
        if os.path.exists(log_path):
            os.remove(log_path)

        try:
            response = client.post('/api/financials/execute-playbook', json={'actions': ['suspend_tranches', 'reduce_production_cost']})
            self.assertEqual(response.status_code, 200)
            self.assertTrue(os.path.exists(log_path))

            with open(log_path, 'r', encoding='utf-8') as f:
                entries = json.load(f)

            self.assertIsInstance(entries, list)
            self.assertEqual(entries[-1]['executed_actions'], ['suspend_tranches', 'reduce_production_cost'])
        finally:
            if os.path.exists(log_path):
                os.remove(log_path)

    def test_dashboard_includes_emergency_playbook(self):
        self.financials.cash_reserves = 1.5
        result = self.service.generate_emergency_playbook(self.financials)

        self.assertEqual(result['trigger'], 'cash_below_threshold')
        self.assertIsInstance(result['actions'], list)


if __name__ == '__main__':
    unittest.main()

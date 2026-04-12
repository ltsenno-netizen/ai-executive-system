import os
import sys
import unittest
from copy import deepcopy

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src', 'backend')))

from fastapi.testclient import TestClient
from app.main import app
from app.models.financial_model import FinancialFundamentals, InvestmentDecisionRecord, InvestmentRequest
from app.services.financial_service import FinancialService

client = TestClient(app)


class TestFinancialService(unittest.TestCase):
    def setUp(self):
        self.service = FinancialService()

    def test_load_financials(self):
        financials = self.service.load_financials()

        self.assertEqual(financials.cash_reserves, 15.0)
        self.assertEqual(financials.investment_policy['max_investment_pct_of_cash'], 0.25)

    def test_calculate_monthly_free_cash_flow(self):
        financials = self.service.load_financials()
        pl_monthly = {'revenue': 6.0}

        updated = self.service.calculate_monthly_free_cash_flow(
            pl_monthly, deepcopy(financials), working_capital_change=0.1
        )

        self.assertEqual(
            updated.free_cash_flow,
            round((6.0 - financials.monthly_operating_expenses) * 0.75 - financials.monthly_debt_service - 0.1, 3),
        )

    def test_evaluate_investment_request_rejects_low_liquidity(self):
        financials = self.service.load_financials()
        request = InvestmentRequest(
            id='req-low-cash',
            business_unit_id='bu_test',
            requested_amount=14.0,
            expected_return_rate=0.1,
            payback_period_months=24,
            strategic_priority=5,
            requested_by='tester',
            requested_month=7,
        )
        decision = self.service.evaluate_investment_request(request, financials)

        self.assertEqual(decision.decision, 'Rejected')
        self.assertIn('流動性閾値', decision.reason)

    def test_apply_investment_decision_updates_cash_and_capex(self):
        financials = self.service.load_financials()
        before_cash = financials.cash_reserves
        before_capex = financials.committed_capex
        decision = InvestmentDecisionRecord(
            id='dec1',
            investment_request_id='req-1',
            decision='Approved',
            approved_amount=1.0,
            reason='Test',
            impact_on_cash=-1.0,
            applied_month=7,
        )

        updated = self.service.apply_investment_decision(
            decision, deepcopy(financials), business_unit_id='bu_test'
        )

        self.assertEqual(updated.cash_reserves, round(before_cash - 1.0, 3))
        self.assertEqual(updated.committed_capex, round(before_capex + 1.0, 3))

    def test_emergency_liquidity_measures_when_low(self):
        financials = self.service.load_financials()
        financials.cash_reserves = 1.0

        measures = self.service.emergency_liquidity_measures(financials)

        self.assertTrue(any('投資' in measure for measure in measures))
        self.assertTrue(any('与信' in measure for measure in measures))

    def test_financials_endpoint_returns_data(self):
        response = client.get('/api/financials')
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertIn('cash_reserves', body)
        self.assertIn('monthly_operating_expenses', body)

    def test_partial_candidate_calculated_when_request_exceeds_policy(self):
        financials = FinancialFundamentals(
            cash_reserves=10.0,
            short_term_debt=1.0,
            long_term_debt=2.0,
            interest_rate_short=0.05,
            interest_rate_long=0.06,
            monthly_revenue=0.0,
            monthly_operating_expenses=1.0,
            capex_plan={},
            committed_capex=0.0,
            available_credit_line=1.0,
            liquidity_buffer_months=1.0,
            minimum_cash_threshold=2.0,
            monthly_debt_service=0.1,
            free_cash_flow=0.0,
            investment_policy={
                'max_investment_pct_of_cash': 0.25,
                'tranche_buffer': 1.0,
            },
            financial_health_indicators={
                'debt_to_equity': 1.0,
                'current_ratio': 1.0,
            },
        )
        request = InvestmentRequest(
            id='request-partial',
            business_unit_id='bu_test',
            requested_amount=7.0,
            expected_return_rate=0.20,
            payback_period_months=24,
            strategic_priority=3,
            requested_by='tester',
            requested_month=5,
        )
        decision = self.service.evaluate_investment_request(request, financials)

        self.assertEqual(decision.decision, 'Partial')
        self.assertEqual(decision.partial_candidate, 2.5)
        self.assertEqual(decision.approved_amount, 2.5)
        self.assertIsNone(decision.tranche_schedule)

    def test_tranche_schedule_is_generated_for_request_with_tranche(self):
        financials = FinancialFundamentals(
            cash_reserves=10.0,
            short_term_debt=1.0,
            long_term_debt=2.0,
            interest_rate_short=0.05,
            interest_rate_long=0.06,
            monthly_revenue=0.0,
            monthly_operating_expenses=1.0,
            capex_plan={},
            committed_capex=0.0,
            available_credit_line=1.0,
            liquidity_buffer_months=1.0,
            minimum_cash_threshold=2.0,
            monthly_debt_service=0.1,
            free_cash_flow=0.0,
            investment_policy={
                'max_investment_pct_of_cash': 0.75,
                'tranche_buffer': 1.0,
            },
            financial_health_indicators={
                'debt_to_equity': 1.0,
                'current_ratio': 1.0,
            },
        )
        request = InvestmentRequest(
            id='request-tranche',
            business_unit_id='bu_test',
            requested_amount=8.0,
            expected_return_rate=0.20,
            payback_period_months=24,
            strategic_priority=3,
            requested_by='tester',
            requested_month=4,
            tranche_count=3,
            tranche_interval_months=2,
        )
        decision = self.service.evaluate_investment_request(request, financials)

        self.assertEqual(decision.decision, 'Partial')
        self.assertIsNotNone(decision.tranche_schedule)
        self.assertEqual(len(decision.tranche_schedule), 3)
        self.assertEqual(decision.tranche_schedule[0]['scheduled_month'], 4)
        self.assertEqual(decision.tranche_schedule[1]['scheduled_month'], 6)
        self.assertEqual(decision.tranche_schedule[2]['scheduled_month'], 8)
        self.assertEqual(decision.tranche_schedule[0]['status'], 'pending')

    def test_apply_investment_decision_supports_tranche_index(self):
        financials = FinancialFundamentals(
            cash_reserves=10.0,
            short_term_debt=1.0,
            long_term_debt=2.0,
            interest_rate_short=0.05,
            interest_rate_long=0.06,
            monthly_revenue=0.0,
            monthly_operating_expenses=1.0,
            capex_plan={},
            committed_capex=0.0,
            available_credit_line=1.0,
            liquidity_buffer_months=1.0,
            minimum_cash_threshold=2.0,
            monthly_debt_service=0.1,
            free_cash_flow=0.0,
            investment_policy={
                'max_investment_pct_of_cash': 0.25,
                'tranche_buffer': 1.0,
            },
            financial_health_indicators={
                'debt_to_equity': 1.0,
                'current_ratio': 1.0,
            },
        )
        decision = InvestmentDecisionRecord(
            id='dec-tranche',
            investment_request_id='request-tranche',
            decision='Approved',
            approved_amount=1.0,
            partial_candidate=None,
            tranche_schedule=None,
            reason='Tranche execution',
            impact_on_cash=-1.0,
            applied_month=4,
            tranche_index=1,
        )

        updated = self.service.apply_investment_decision(decision, financials)

        self.assertEqual(updated.cash_reserves, 9.0)
        self.assertEqual(updated.committed_capex, 1.0)


if __name__ == '__main__':
    unittest.main()

import os
import sys
import unittest

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from expert_system.inference_engine import ExpertInferenceEngine

class TestExpertRules(unittest.TestCase):
    def setUp(self):
        self.engine = ExpertInferenceEngine()

    def test_underage_applicant(self):
        data = {'age': 16, 'income': 50000, 'credit_score': 750, 'previous_default': 0}
        res = self.engine.evaluate(data)
        self.assertTrue(res['has_critical_fail'])
        self.assertEqual(res['status'], 'NOT_ELIGIBLE')

    def test_low_income_risk(self):
        data = {'age': 30, 'income': 15000, 'credit_score': 700, 'previous_default': 0}
        res = self.engine.evaluate(data)
        self.assertTrue(any('20,000' in f for f in res['risk_factors']))

    def test_previous_default_critical(self):
        data = {'age': 35, 'income': 60000, 'credit_score': 720, 'previous_default': 1}
        res = self.engine.evaluate(data)
        self.assertTrue(res['has_critical_fail'])

    def test_prime_applicant_eligible(self):
        data = {
            'age': 30,
            'income': 90000,
            'credit_score': 800,
            'loan_amount': 200000,
            'existing_emi': 5000,
            'debt': 10000,
            'monthly_expenses': 25000,
            'savings': 400000,
            'dependents': 1,
            'previous_default': 0,
            'employment_status': 'Salaried',
            'debt_to_income': 0.05,
            'emi_ratio': 0.05,
            'disposable_income': 60000,
            'loan_to_income': 0.18,
            'savings_ratio': 0.37,
            'financial_health_score': 95
        }
        res = self.engine.evaluate(data)
        self.assertEqual(res['status'], 'ELIGIBLE')
        self.assertGreaterEqual(res['rule_score'], 75)

if __name__ == '__main__':
    unittest.main()

import os
import sys
import unittest

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from app import app

class TestAPIEndpoints(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()

    def test_api_models_endpoint(self):
        res = self.client.get('/api/models')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn('models', data)

    def test_api_rules_endpoint(self):
        res = self.client.get('/api/rules')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn('rules', data)
        self.assertGreaterEqual(len(data['rules']), 15)

    def test_api_datasets_endpoint(self):
        res = self.client.get('/api/datasets')
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn('datasets', data)
        self.assertEqual(len(data['datasets']), 5)

    def test_api_calculator_endpoint(self):
        res = self.client.post('/api/calculator', json={
            'loan_amount': 500000,
            'interest_rate': 10.5,
            'loan_term': 36
        })
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn('monthly_emi', data)
        self.assertGreater(data['monthly_emi'], 0)

    def test_api_predict_endpoint(self):
        res = self.client.post('/api/predict', json={
            'applicant_name': 'Test Applicant',
            'age': 32,
            'income': 75000,
            'credit_score': 760,
            'loan_amount': 300000,
            'employment_status': 'Salaried',
            'previous_default': 0
        })
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertIn('decision', data)
        self.assertIn('final_score', data)
        self.assertIn('models', data)

if __name__ == '__main__':
    unittest.main()

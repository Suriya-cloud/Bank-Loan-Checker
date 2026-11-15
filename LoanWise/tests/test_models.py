import os
import sys
import unittest

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from ml.predict import MLPredictor
from ml.evaluate_models import load_model_metrics

class TestMLModels(unittest.TestCase):
    def test_model_metrics_exist(self):
        metrics = load_model_metrics()
        self.assertIsNotNone(metrics)
        self.assertIn('logistic_regression', metrics)
        self.assertIn('random_forest', metrics)
        self.assertIn('decision_tree', metrics)
        self.assertIn('xgboost', metrics)

    def test_ml_predictor_inference(self):
        predictor = MLPredictor()
        sample_input = {
            'age': 30,
            'income': 60000,
            'credit_score': 720,
            'loan_amount': 250000,
            'employment_status': 'Salaried'
        }
        predictions, processed = predictor.predict_all(sample_input)
        self.assertEqual(len(predictions), 4)
        for model_name, info in predictions.items():
            self.assertIn('probability', info)
            self.assertGreaterEqual(info['probability'], 0.0)
            self.assertLessEqual(info['probability'], 100.0)

if __name__ == '__main__':
    unittest.main()

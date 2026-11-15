import os
import sys

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import joblib
import numpy as np

from ml.preprocess import preprocess_single_input

MODELS_DIR = os.path.join(os.path.dirname(__file__), '..', 'models')

class MLPredictor:
    def __init__(self):
        self.models = {}
        self._load_models()

    def _load_models(self):
        model_files = {
            'logistic_regression': 'logistic_regression.pkl',
            'random_forest': 'random_forest.pkl',
            'decision_tree': 'decision_tree.pkl',
            'xgboost': 'xgboost_model.pkl'
        }
        for name, filename in model_files.items():
            path = os.path.join(MODELS_DIR, filename)
            if os.path.exists(path):
                try:
                    self.models[name] = joblib.load(path)
                except Exception as e:
                    print(f"Warning: Failed to load model {name} from {path}: {e}")
            else:
                print(f"Warning: Model file {filename} not found.")

    def predict_all(self, raw_input_dict):
        """
        Preprocesses raw user input and runs all available ML models.
        Returns a dictionary of predictions (approval probability 0-100%) for each model.
        """
        X_processed, processed_features = preprocess_single_input(raw_input_dict)
        
        predictions = {}
        probabilities = {}
        
        for name in ['logistic_regression', 'random_forest', 'decision_tree', 'xgboost']:
            if name in self.models and self.models[name] is not None:
                try:
                    model = self.models[name]
                    prob = float(model.predict_proba(X_processed)[0][1])
                    prob_pct = round(prob * 100.0, 2)
                    probabilities[name] = prob_pct
                    predictions[name] = {
                        'status': 'AVAILABLE',
                        'probability': prob_pct,
                        'risk_class': 'Low Risk' if prob_pct >= 75 else ('Medium Risk' if prob_pct >= 50 else 'High Risk')
                    }
                except Exception as e:
                    predictions[name] = {'status': 'ERROR', 'error': str(e), 'probability': 0.0}
            else:
                predictions[name] = {'status': 'UNAVAILABLE', 'probability': 0.0}

        return predictions, processed_features

import os
import sys

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import numpy as np
from ml.evaluate_models import load_model_metrics

class EnsembleDecisionEngine:
    def __init__(self, ml_weight=0.50, rule_weight=0.30, financial_weight=0.20):
        self.ml_weight = ml_weight
        self.rule_weight = rule_weight
        self.financial_weight = financial_weight

    def calculate_ml_ensemble_score(self, model_predictions):
        """
        Combines individual ML model probabilities using test-performance F1 dynamic weighting.
        """
        metrics = load_model_metrics()
        
        # Default static weights fallback
        default_weights = {
            'logistic_regression': 0.20,
            'random_forest': 0.30,
            'decision_tree': 0.15,
            'xgboost': 0.35
        }
        
        weights = {}
        if metrics:
            total_f1 = sum(metrics[m]['f1'] for m in metrics if m in model_predictions and model_predictions[m].get('status') == 'AVAILABLE')
            if total_f1 > 0:
                for m in model_predictions:
                    if model_predictions[m].get('status') == 'AVAILABLE' and m in metrics:
                        weights[m] = metrics[m]['f1'] / total_f1
        
        if not weights:
            weights = default_weights

        weighted_score = 0.0
        weight_sum = 0.0
        valid_probs = []

        for name, info in model_predictions.items():
            if info.get('status') == 'AVAILABLE':
                prob = info.get('probability', 50.0)
                w = weights.get(name, 0.25)
                weighted_score += prob * w
                weight_sum += w
                valid_probs.append(prob)

        if weight_sum > 0:
            final_ml_prob = round(weighted_score / weight_sum, 2)
        else:
            final_ml_prob = 50.0

        # Consensus & Disagreement analysis
        if len(valid_probs) > 1:
            std_dev = float(np.std(valid_probs))
            prob_range = float(np.ptp(valid_probs))
            has_disagreement = prob_range > 20.0
            
            if std_dev < 5.0:
                confidence = "HIGH"
            elif std_dev < 12.0:
                confidence = "MEDIUM"
            else:
                confidence = "LOW"
        else:
            std_dev = 0.0
            prob_range = 0.0
            has_disagreement = False
            confidence = "MEDIUM"

        return {
            'ml_score': final_ml_prob,
            'weights_used': weights,
            'confidence': confidence,
            'std_dev': round(std_dev, 2),
            'disagreement_range': round(prob_range, 2),
            'has_disagreement': has_disagreement
        }

    def generate_final_decision(self, ml_res, rule_res, processed_features):
        """
        Combines ML Score, Rule Score, and Financial Health Score into Final Decision.
        Applies critical rule overrides.
        """
        ml_score = ml_res['ml_score']
        rule_score = rule_res['rule_score']
        financial_score = processed_features.get('financial_health_score', 65.0)

        # Weighted final score calculation
        final_score = round(
            self.ml_weight * ml_score +
            self.rule_weight * rule_score +
            self.financial_weight * financial_score,
            2
        )

        has_critical = rule_res.get('has_critical_fail', False)

        # Decision threshold logic
        if has_critical or final_score < 50.0:
            decision = "NOT_ELIGIBLE"
            risk_level = "HIGH"
        elif final_score >= 75.0:
            decision = "ELIGIBLE"
            risk_level = "LOW"
        else:
            decision = "CONDITIONALLY_ELIGIBLE"
            risk_level = "MEDIUM"

        return {
            'decision': decision,
            'risk_level': risk_level,
            'final_score': final_score,
            'ml_score': ml_score,
            'rule_score': rule_score,
            'financial_score': financial_score,
            'confidence': ml_res['confidence'],
            'has_disagreement': ml_res['has_disagreement'],
            'disagreement_range': ml_res['disagreement_range'],
            'weights_config': {
                'ml': self.ml_weight,
                'rule': self.rule_weight,
                'financial': self.financial_weight
            }
        }

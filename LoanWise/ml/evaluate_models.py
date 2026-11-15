import os
import json

MODELS_DIR = os.path.join(os.path.dirname(__file__), '..', 'models')
METRICS_FILE = os.path.join(MODELS_DIR, 'model_metrics.json')

def load_model_metrics():
    """
    Loads saved evaluation metrics for all 4 ML models.
    """
    if not os.path.exists(METRICS_FILE):
        return None
    try:
        with open(METRICS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading model metrics: {e}")
        return None

def get_best_model(metrics=None):
    """
    Identifies the best performing model based on F1 Score.
    """
    if metrics is None:
        metrics = load_model_metrics()
    if not metrics:
        return "Unknown", 0.0

    best_name = None
    best_f1 = -1.0
    for key, data in metrics.items():
        if data.get('f1', 0) > best_f1:
            best_f1 = data['f1']
            best_name = data.get('model_name', key)

    return best_name, best_f1

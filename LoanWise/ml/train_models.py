import os
import sys

# Ensure root package directory is in sys.path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import json
import joblib
import pandas as pd
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.tree import DecisionTreeClassifier, export_text
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix

try:
    from xgboost import XGBClassifier
    HAS_XGB = True
except ImportError:
    HAS_XGB = False

from ml.preprocess import generate_unified_dataset, fit_and_save_transformers, NUMERICAL_FEATURES, CATEGORICAL_FEATURES

MODELS_DIR = os.path.join(os.path.dirname(__file__), '..', 'models')
os.makedirs(MODELS_DIR, exist_ok=True)

def train_and_evaluate_all():
    print("==================================================")
    print("      LOANWISE ML MODEL TRAINING PIPELINE         ")
    print("==================================================")
    
    # 1. Load/generate dataset & fit preprocessing transformers
    df = generate_unified_dataset()
    scaler, encoder = fit_and_save_transformers(df)
    
    # Transform features
    X_num = scaler.transform(df[NUMERICAL_FEATURES])
    X_cat = encoder.transform(df[CATEGORICAL_FEATURES])
    X = np.hstack([X_num, X_cat])
    y = df['target'].values
    
    feature_names = NUMERICAL_FEATURES + list(encoder.get_feature_names_out(CATEGORICAL_FEATURES))

    # 2. 80/20 Stratified Train-Test Split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )

    print(f"Dataset Split: {len(X_train)} Training samples, {len(X_test)} Testing samples.")

    # Dictionary to hold models and metrics
    trained_models = {}
    metrics_summary = {}

    # --- MODEL 1: LOGISTIC REGRESSION ---
    print("\nTraining Model 1: Logistic Regression...")
    lr = LogisticRegression(max_iter=1000, random_state=42)
    lr.fit(X_train, y_train)
    y_pred_lr = lr.predict(X_test)
    y_prob_lr = lr.predict_proba(X_test)[:, 1]
    
    metrics_summary['logistic_regression'] = {
        'model_name': 'Logistic Regression',
        'purpose': 'Loan Approval Probability Estimation',
        'accuracy': round(float(accuracy_score(y_test, y_pred_lr)), 4),
        'precision': round(float(precision_score(y_test, y_pred_lr, zero_division=0)), 4),
        'recall': round(float(recall_score(y_test, y_pred_lr, zero_division=0)), 4),
        'f1': round(float(f1_score(y_test, y_pred_lr, zero_division=0)), 4),
        'roc_auc': round(float(roc_auc_score(y_test, y_prob_lr)), 4),
        'confusion_matrix': confusion_matrix(y_test, y_pred_lr).tolist()
    }
    trained_models['logistic_regression'] = lr
    joblib.dump(lr, os.path.join(MODELS_DIR, 'logistic_regression.pkl'))
    print("✓ Logistic Regression trained & saved.")

    # --- MODEL 2: RANDOM FOREST ---
    print("\nTraining Model 2: Random Forest...")
    rf = RandomForestClassifier(n_estimators=100, max_depth=8, random_state=42)
    rf.fit(X_train, y_train)
    y_pred_rf = rf.predict(X_test)
    y_prob_rf = rf.predict_proba(X_test)[:, 1]
    
    rf_importances = dict(zip(feature_names, [round(float(v), 4) for v in rf.feature_importances_]))

    metrics_summary['random_forest'] = {
        'model_name': 'Random Forest',
        'purpose': 'Credit & Default Risk Classification',
        'accuracy': round(float(accuracy_score(y_test, y_pred_rf)), 4),
        'precision': round(float(precision_score(y_test, y_pred_rf, zero_division=0)), 4),
        'recall': round(float(recall_score(y_test, y_pred_rf, zero_division=0)), 4),
        'f1': round(float(f1_score(y_test, y_pred_rf, zero_division=0)), 4),
        'roc_auc': round(float(roc_auc_score(y_test, y_prob_rf)), 4),
        'confusion_matrix': confusion_matrix(y_test, y_pred_rf).tolist(),
        'feature_importance': rf_importances
    }
    trained_models['random_forest'] = rf
    joblib.dump(rf, os.path.join(MODELS_DIR, 'random_forest.pkl'))
    print("✓ Random Forest trained & saved.")

    # --- MODEL 3: DECISION TREE ---
    print("\nTraining Model 3: Decision Tree...")
    dt = DecisionTreeClassifier(max_depth=5, random_state=42)
    dt.fit(X_train, y_train)
    y_pred_dt = dt.predict(X_test)
    y_prob_dt = dt.predict_proba(X_test)[:, 1]
    
    tree_rules_text = export_text(dt, feature_names=feature_names, max_depth=3)

    metrics_summary['decision_tree'] = {
        'model_name': 'Decision Tree',
        'purpose': 'Explainable Rule Classification',
        'accuracy': round(float(accuracy_score(y_test, y_pred_dt)), 4),
        'precision': round(float(precision_score(y_test, y_pred_dt, zero_division=0)), 4),
        'recall': round(float(recall_score(y_test, y_pred_dt, zero_division=0)), 4),
        'f1': round(float(f1_score(y_test, y_pred_dt, zero_division=0)), 4),
        'roc_auc': round(float(roc_auc_score(y_test, y_prob_dt)), 4),
        'confusion_matrix': confusion_matrix(y_test, y_pred_dt).tolist(),
        'decision_rules': tree_rules_text
    }
    trained_models['decision_tree'] = dt
    joblib.dump(dt, os.path.join(MODELS_DIR, 'decision_tree.pkl'))
    print("✓ Decision Tree trained & saved.")

    # --- MODEL 4: XGBOOST / GRADIENT BOOSTING ---
    print("\nTraining Model 4: XGBoost / Gradient Boosting...")
    if HAS_XGB:
        xgb = XGBClassifier(n_estimators=100, max_depth=5, learning_rate=0.1, random_state=42, eval_metric='logloss')
        xgb.fit(X_train, y_train)
        model_type_name = "XGBoost Classifier"
    else:
        xgb = GradientBoostingClassifier(n_estimators=100, max_depth=5, learning_rate=0.1, random_state=42)
        xgb.fit(X_train, y_train)
        model_type_name = "Gradient Boosting Classifier (Fallback)"
        
    y_pred_xgb = xgb.predict(X_test)
    y_prob_xgb = xgb.predict_proba(X_test)[:, 1]

    xgb_importances = dict(zip(feature_names, [round(float(v), 4) for v in xgb.feature_importances_]))

    metrics_summary['xgboost'] = {
        'model_name': model_type_name,
        'purpose': 'High-Performance Risk & Approval Boosting',
        'accuracy': round(float(accuracy_score(y_test, y_pred_xgb)), 4),
        'precision': round(float(precision_score(y_test, y_pred_xgb, zero_division=0)), 4),
        'recall': round(float(recall_score(y_test, y_pred_xgb, zero_division=0)), 4),
        'f1': round(float(f1_score(y_test, y_pred_xgb, zero_division=0)), 4),
        'roc_auc': round(float(roc_auc_score(y_test, y_prob_xgb)), 4),
        'confusion_matrix': confusion_matrix(y_test, y_pred_xgb).tolist(),
        'feature_importance': xgb_importances
    }
    trained_models['xgboost'] = xgb
    joblib.dump(xgb, os.path.join(MODELS_DIR, 'xgboost_model.pkl'))
    print(f"✓ {model_type_name} trained & saved.")

    # Save metrics JSON
    with open(os.path.join(MODELS_DIR, 'model_metrics.json'), 'w', encoding='utf-8') as f:
        json.dump(metrics_summary, f, indent=2)

    print("\n==================================================")
    print(" MODEL PERFORMANCE EVALUATION COMPARISON SUMMARY ")
    print("==================================================")
    print(f"{'Model':<24} | {'Accuracy':<8} | {'Precision':<9} | {'Recall':<8} | {'F1 Score':<8} | {'ROC-AUC':<8}")
    print("-" * 75)
    for k, v in metrics_summary.items():
        print(f"{v['model_name']:<24} | {v['accuracy']*100:6.1f}%  | {v['precision']*100:7.1f}%  | {v['recall']*100:6.1f}%  | {v['f1']*100:6.1f}%  | {v['roc_auc']*100:6.1f}%")
    print("==================================================")
    print("All models successfully trained, evaluated, and saved!")
    return metrics_summary

if __name__ == '__main__':
    train_and_evaluate_all()

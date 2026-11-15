import os
import sys

# Ensure root directory is in sys.path
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import json
import pandas as pd
import numpy as np
from flask import Flask, render_template, request, jsonify, redirect, url_for
try:
    from flask_cors import CORS
    HAS_CORS = True
except ImportError:
    HAS_CORS = False

from config import Config
from database.database import init_db, save_assessment, get_all_assessments, get_assessment_by_id, delete_assessment, get_dashboard_summary
from expert_system.rules import load_knowledge_base
from expert_system.inference_engine import ExpertInferenceEngine
from ml.preprocess import preprocess_single_input
from ml.predict import MLPredictor
from ml.evaluate_models import load_model_metrics, get_best_model
from ml.ensemble import EnsembleDecisionEngine

app = Flask(__name__)
app.config.from_object(Config)
if HAS_CORS:
    CORS(app)

# Initialize Database
init_db()

# Instantiate core engines
inference_engine = ExpertInferenceEngine()
ml_predictor = MLPredictor()
ensemble_engine = EnsembleDecisionEngine(
    ml_weight=Config.ML_SCORE_WEIGHT,
    rule_weight=Config.EXPERT_RULE_WEIGHT,
    financial_weight=Config.FINANCIAL_HEALTH_WEIGHT
)

# Helper: Generate personalized recommendations
def generate_recommendations(data, decision, risk_level):
    recs = []
    cs = data.get('credit_score', 700)
    dti = data.get('debt_to_income', 0.2)
    disp = data.get('disposable_income', 20000)
    prev_def = data.get('previous_default', 0)
    loan_amt = data.get('loan_amount', 200000)
    income = data.get('income', 50000)

    if cs < 720:
        recs.append("Work on improving your credit score by making all payments on time and maintaining low credit utilization.")
    if dti > 0.35:
        recs.append(f"Your Debt-to-Income ratio ({dti*100:.1f}%) is high. Pay off existing credit card or EMI loans to reduce debt burden.")
    if disp < 15000:
        recs.append("Increase your net disposable income by cutting monthly discretionary expenses.")
    if loan_amt > (income * 12 * 0.4):
        recs.append("Consider requesting a lower loan amount or extending the loan tenure to reduce monthly EMI payments.")
    if prev_def == 1:
        recs.append("Establish a 12-month clean payment record to overcome past default history.")
    if not recs:
        recs.append("Maintain your current healthy financial habits and keep debt low.")
        recs.append("Consider building an emergency savings reserve equivalent to 6 months of living expenses.")

    return recs

# -------------------------------------------------------------------
# FRONTEND TEMPLATE ROUTES
# -------------------------------------------------------------------
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/assessment')
def assessment():
    return render_template('assessment.html')

@app.route('/analyzing')
def analyzing():
    return render_template('analyzing.html')

@app.route('/result', methods=['GET', 'POST'])
def result():
    post_result_json = None
    if request.method == 'POST':
        try:
            data = request.form.to_dict() if request.form else (request.json or {})
            if data:
                raw_input = {
                    'applicant_name': str(data.get('applicant_name', 'Anonymous Applicant')),
                    'age': int(data.get('age', 30)),
                    'gender': str(data.get('gender', 'Male')),
                    'marital_status': str(data.get('marital_status', 'Single')),
                    'dependents': int(data.get('dependents', 0)),
                    'education': str(data.get('education', 'Graduate')),
                    'employment_status': str(data.get('employment_status', 'Salaried')),
                    'income': float(data.get('income', 50000)),
                    'monthly_expenses': float(data.get('monthly_expenses', 20000)),
                    'savings': float(data.get('savings', 100000)),
                    'existing_emi': float(data.get('existing_emi', 5000)),
                    'debt': float(data.get('debt', 50000)),
                    'credit_score': int(data.get('credit_score', 700)),
                    'previous_default': int(data.get('previous_default', 0)),
                    'requested_loan_amount': float(data.get('loan_amount', 200000)),
                    'loan_amount': float(data.get('loan_amount', 200000)),
                    'loan_term': int(data.get('loan_term', 36)),
                    'loan_purpose': str(data.get('loan_purpose', 'Personal'))
                }

                ml_predictions, processed_features = ml_predictor.predict_all(raw_input)
                rule_analysis = inference_engine.evaluate(processed_features)
                ml_ensemble_res = ensemble_engine.calculate_ml_ensemble_score(ml_predictions)
                final_decision_res = ensemble_engine.generate_final_decision(
                    ml_ensemble_res, rule_analysis, processed_features
                )

                financial_metrics = {
                    'dti': processed_features.get('debt_to_income', 0.1),
                    'emi_ratio': processed_features.get('emi_ratio', 0.1),
                    'disposable_income': processed_features.get('disposable_income', 25000),
                    'loan_to_income': processed_features.get('loan_to_income', 0.33),
                    'savings_ratio': processed_features.get('savings_ratio', 0.2),
                    'financial_health_score': processed_features.get('financial_health_score', 75.0)
                }

                recommendations = generate_recommendations(
                    processed_features,
                    final_decision_res['decision'],
                    final_decision_res['risk_level']
                )

                model_scores = {
                    'logistic_regression': ml_predictions.get('logistic_regression', {}).get('probability', 0.0),
                    'random_forest': ml_predictions.get('random_forest', {}).get('probability', 0.0),
                    'decision_tree': ml_predictions.get('decision_tree', {}).get('probability', 0.0),
                    'xgboost': ml_predictions.get('xgboost', {}).get('probability', 0.0)
                }

                result_object = {
                    "decision": final_decision_res['decision'],
                    "risk_level": final_decision_res['risk_level'],
                    "final_score": final_decision_res['final_score'],
                    "ml_score": final_decision_res['ml_score'],
                    "rule_score": final_decision_res['rule_score'],
                    "financial_score": final_decision_res['financial_score'],
                    "confidence": final_decision_res['confidence'],
                    "has_disagreement": final_decision_res['has_disagreement'],
                    "disagreement_range": final_decision_res['disagreement_range'],
                    "models": model_scores,
                    "models_detail": ml_predictions,
                    "triggered_rules": rule_analysis['triggered_rules'],
                    "positive_factors": rule_analysis['positive_factors'],
                    "risk_factors": rule_analysis['risk_factors'],
                    "critical_flags": rule_analysis.get('critical_flags', []),
                    "financial_metrics": financial_metrics,
                    "recommendations": recommendations,
                    "applicant_info": raw_input,
                    "disclaimer": "LoanWise is an educational AI prototype. Results are generated using machine-learning models and expert rules and do not represent an actual bank's lending decision or guarantee of approval."
                }

                assessment_id = save_assessment(raw_input, result_object)
                result_object['assessment_id'] = assessment_id
                post_result_json = json.dumps(result_object)
        except Exception as e:
            print(f"Error processing POST /result: {e}")

    return render_template('result.html', post_result=post_result_json)

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/models')
def models():
    return render_template('models.html')

@app.route('/datasets')
def datasets():
    return render_template('datasets.html')

@app.route('/rules')
def rules():
    return render_template('rules.html')

@app.route('/history')
def history():
    return render_template('history.html')

@app.route('/about')
def about():
    return render_template('about.html')

# -------------------------------------------------------------------
# REST API ENDPOINTS
# -------------------------------------------------------------------

@app.route('/api/predict', methods=['POST'])
def api_predict():
    """
    Complete Hybrid Assessment Pipeline:
    User Input -> Validation -> Preprocessing & Feature Engineering -> 4 ML Models ->
    Expert Rules -> Financial Risk Score -> Ensemble Decision -> DB Storage -> Structured JSON
    """
    try:
        data = request.json if request.is_json else request.form.to_dict()
        if not data:
            return jsonify({'error': 'No input data provided'}), 400

        # Type conversion & normalization
        raw_input = {
            'applicant_name': str(data.get('applicant_name', 'Anonymous Applicant')),
            'age': int(data.get('age', 30)),
            'gender': str(data.get('gender', 'Male')),
            'marital_status': str(data.get('marital_status', 'Single')),
            'dependents': int(data.get('dependents', 0)),
            'education': str(data.get('education', 'Graduate')),
            'employment_status': str(data.get('employment_status', 'Salaried')),
            'income': float(data.get('income', 50000)),
            'monthly_expenses': float(data.get('monthly_expenses', 20000)),
            'savings': float(data.get('savings', 100000)),
            'existing_emi': float(data.get('existing_emi', 5000)),
            'debt': float(data.get('debt', 50000)),
            'credit_score': int(data.get('credit_score', 700)),
            'previous_default': int(data.get('previous_default', 0)),
            'requested_loan_amount': float(data.get('loan_amount', 200000)),
            'loan_amount': float(data.get('loan_amount', 200000)),
            'loan_term': int(data.get('loan_term', 36)),
            'loan_purpose': str(data.get('loan_purpose', 'Personal'))
        }

        # 1. ML Model Predictions
        ml_predictions, processed_features = ml_predictor.predict_all(raw_input)

        # 2. Expert Rules Analysis
        rule_analysis = inference_engine.evaluate(processed_features)

        # 3. ML Ensemble Calculation
        ml_ensemble_res = ensemble_engine.calculate_ml_ensemble_score(ml_predictions)

        # 4. Final Ensemble Decision Engine
        final_decision_res = ensemble_engine.generate_final_decision(
            ml_ensemble_res, rule_analysis, processed_features
        )

        # 5. Financial Health Ratios
        financial_metrics = {
            'dti': processed_features.get('debt_to_income', 0.1),
            'emi_ratio': processed_features.get('emi_ratio', 0.1),
            'disposable_income': processed_features.get('disposable_income', 25000),
            'loan_to_income': processed_features.get('loan_to_income', 0.33),
            'savings_ratio': processed_features.get('savings_ratio', 0.2),
            'financial_health_score': processed_features.get('financial_health_score', 75.0)
        }

        # 6. Actionable Recommendations
        recommendations = generate_recommendations(
            processed_features,
            final_decision_res['decision'],
            final_decision_res['risk_level']
        )

        # Format model score map
        model_scores = {
            'logistic_regression': ml_predictions.get('logistic_regression', {}).get('probability', 0.0),
            'random_forest': ml_predictions.get('random_forest', {}).get('probability', 0.0),
            'decision_tree': ml_predictions.get('decision_tree', {}).get('probability', 0.0),
            'xgboost': ml_predictions.get('xgboost', {}).get('probability', 0.0)
        }

        # Construct final structured response (Section 48 compliant)
        result_object = {
            "decision": final_decision_res['decision'],
            "risk_level": final_decision_res['risk_level'],
            "final_score": final_decision_res['final_score'],
            "ml_score": final_decision_res['ml_score'],
            "rule_score": final_decision_res['rule_score'],
            "financial_score": final_decision_res['financial_score'],
            "confidence": final_decision_res['confidence'],
            "has_disagreement": final_decision_res['has_disagreement'],
            "disagreement_range": final_decision_res['disagreement_range'],

            "models": model_scores,
            "models_detail": ml_predictions,

            "triggered_rules": rule_analysis['triggered_rules'],
            "positive_factors": rule_analysis['positive_factors'],
            "risk_factors": rule_analysis['risk_factors'],
            "critical_flags": rule_analysis.get('critical_flags', []),

            "financial_metrics": financial_metrics,
            "recommendations": recommendations,
            "applicant_info": raw_input,
            "disclaimer": "LoanWise is an educational AI prototype. Results are generated using machine-learning models and expert rules and do not represent an actual bank's lending decision or guarantee of approval."
        }

        # Save to SQLite Database
        assessment_id = save_assessment(raw_input, result_object)
        result_object['assessment_id'] = assessment_id

        return jsonify(result_object), 200

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Failed to process assessment', 'details': str(e)}), 500

@app.route('/api/expert-analysis', methods=['POST'])
def api_expert_analysis():
    """Runs expert rules independently."""
    try:
        data = request.json or {}
        _, processed_features = preprocess_single_input(data)
        analysis = inference_engine.evaluate(processed_features)
        return jsonify(analysis), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/ml-predict', methods=['POST'])
def api_ml_predict():
    """Runs ML models independently."""
    try:
        data = request.json or {}
        predictions, _ = ml_predictor.predict_all(data)
        return jsonify(predictions), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/models', methods=['GET'])
def api_models():
    """Returns evaluation metrics, ROC-AUC, F1, and comparison stats."""
    metrics = load_model_metrics()
    best_name, best_f1 = get_best_model(metrics)
    return jsonify({
        'models': metrics or {},
        'best_model': best_name,
        'best_f1': best_f1
    }), 200

@app.route('/api/datasets', methods=['GET'])
def api_datasets():
    """Returns actual dataset statistics from CSV files in data/raw/."""
    dataset_files = {
        'Loan Approval Dataset': 'loan_approval.csv',
        'Credit Risk Dataset': 'credit_risk.csv',
        'Loan Default Dataset': 'loan_default.csv',
        'Customer Financial Dataset': 'customer_financial.csv',
        'Personal Loan Dataset': 'personal_loan.csv'
    }
    
    stats = []
    for name, filename in dataset_files.items():
        filepath = os.path.join(Config.RAW_DATA_DIR, filename)
        if os.path.exists(filepath):
            df = pd.read_csv(filepath)
            missing = df.isnull().sum().to_dict()
            missing_filtered = {k: v for k, v in missing.items() if v > 0}
            
            num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            cat_cols = df.select_dtypes(exclude=[np.number]).columns.tolist()
            
            sample_records = df.head(5).to_dict(orient='records')

            stats.append({
                'name': name,
                'filename': filename,
                'rows': len(df),
                'columns': len(df.columns),
                'column_names': list(df.columns),
                'target': df.columns[-1],
                'missing_values': missing_filtered,
                'numerical_features': num_cols,
                'categorical_features': cat_cols,
                'sample': sample_records
            })
        else:
            stats.append({
                'name': name,
                'filename': filename,
                'rows': 0,
                'columns': 0,
                'error': 'File not found'
            })
    return jsonify({'datasets': stats}), 200

@app.route('/api/rules', methods=['GET'])
def api_rules():
    """Returns all rules from knowledge base JSON."""
    rules_list = load_knowledge_base()
    return jsonify({'rules': rules_list}), 200

@app.route('/api/history', methods=['GET'])
def api_history():
    """Returns all historical assessments from SQLite database."""
    records = get_all_assessments()
    return jsonify({'history': records}), 200

@app.route('/api/history/<int:assessment_id>', methods=['GET'])
def api_history_detail(assessment_id):
    """Returns detailed assessment record by ID."""
    record = get_assessment_by_id(assessment_id)
    if record:
        return jsonify(record), 200
    return jsonify({'error': 'Record not found'}), 404

@app.route('/api/history/<int:assessment_id>', methods=['DELETE'])
def api_history_delete(assessment_id):
    """Deletes assessment record from SQLite database."""
    success = delete_assessment(assessment_id)
    if success:
        return jsonify({'message': 'Assessment deleted successfully'}), 200
    return jsonify({'error': 'Failed to delete assessment'}), 400

@app.route('/api/calculator', methods=['POST'])
def api_calculator():
    """Financial Loan EMI Calculator."""
    try:
        data = request.json or {}

        raw_amount = data.get('loan_amount')
        raw_rate = data.get('interest_rate')
        raw_term = data.get('loan_term')

        P = float(raw_amount) if raw_amount is not None and str(raw_amount).strip() != '' else 500000.0
        annual_rate = float(raw_rate) if raw_rate is not None and str(raw_rate).strip() != '' else 10.5
        tenure_months = int(raw_term) if raw_term is not None and str(raw_term).strip() != '' else 36

        if P <= 0:
            return jsonify({'error': 'Loan amount must be greater than zero.'}), 400
        if annual_rate < 0:
            return jsonify({'error': 'Interest rate cannot be negative.'}), 400
        if tenure_months <= 0:
            return jsonify({'error': 'Loan term must be at least 1 month.'}), 400

        r = (annual_rate / 100.0) / 12.0

        if r > 0:
            emi = (P * r * ((1 + r) ** tenure_months)) / (((1 + r) ** tenure_months) - 1)
        else:
            emi = P / tenure_months

        total_payment = emi * tenure_months
        total_interest = total_payment - P

        return jsonify({
            'monthly_emi': round(emi, 2),
            'total_interest': round(max(total_interest, 0.0), 2),
            'total_payment': round(total_payment, 2),
            'principal': P,
            'rate': annual_rate,
            'term_months': tenure_months
        }), 200
    except (ValueError, TypeError) as e:
        return jsonify({'error': f'Invalid input values: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/dashboard-stats', methods=['GET'])
def api_dashboard_stats():
    """Returns summary analytics for dashboard."""
    stats = get_dashboard_summary()
    return jsonify(stats), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', getattr(Config, 'PORT', 5000)))
    print("==================================================")
    print(f"  LOANWISE HYBRID AI SERVER STARTING ON PORT {port} ")
    print("==================================================")
    app.run(host='127.0.0.1', port=port, debug=True)

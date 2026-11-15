import json
import os

KNOWLEDGE_BASE_PATH = os.path.join(os.path.dirname(__file__), 'knowledge_base.json')

def load_knowledge_base():
    """Loads knowledge base JSON file containing all rule definitions."""
    if not os.path.exists(KNOWLEDGE_BASE_PATH):
        raise FileNotFoundError(f"Knowledge base file not found at {KNOWLEDGE_BASE_PATH}")
    with open(KNOWLEDGE_BASE_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data.get('rules', [])

def evaluate_rule_condition(condition_str, data):
    """
    Safely evaluates a rule condition string against the applicant's financial profile.
    """
    # Expose profile fields to local context safely
    context = {
        'age': data.get('age', 30),
        'income': data.get('income', 50000),
        'credit_score': data.get('credit_score', 700),
        'loan_amount': data.get('loan_amount', 200000),
        'existing_emi': data.get('existing_emi', 5000),
        'debt': data.get('debt', 50000),
        'monthly_expenses': data.get('monthly_expenses', 20000),
        'savings': data.get('savings', 100000),
        'dependents': data.get('dependents', 0),
        'previous_default': data.get('previous_default', 0),
        'employment_status': data.get('employment_status', 'Salaried'),
        'debt_to_income': data.get('debt_to_income', 0.1),
        'emi_ratio': data.get('emi_ratio', 0.1),
        'disposable_income': data.get('disposable_income', 25000),
        'loan_to_income': data.get('loan_to_income', 0.33),
        'savings_ratio': data.get('savings_ratio', 0.2),
        'financial_health_score': data.get('financial_health_score', 75)
    }
    
    try:
        # Evaluate condition safely within context
        return bool(eval(condition_str, {"__builtins__": None}, context))
    except Exception as e:
        print(f"Error evaluating rule condition '{condition_str}': {e}")
        return False

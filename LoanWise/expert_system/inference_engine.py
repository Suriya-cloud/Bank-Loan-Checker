import os
import sys

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import numpy as np
from expert_system.rules import load_knowledge_base, evaluate_rule_condition

class ExpertInferenceEngine:
    def __init__(self):
        self.rules = load_knowledge_base()

    def calculate_rule_score(self, data):
        """
        Calculates an educational rule score (0-100) using domain expert component weightings:
        - Credit Score: 30 pts
        - Monthly Income: 20 pts
        - Employment Stability: 15 pts
        - Debt-to-Income (DTI): 15 pts
        - Previous Default: 10 pts
        - Savings Ratio: 5 pts
        - Age / Dependents: 5 pts
        """
        score = 0.0

        # 1. Credit Score (30 pts max)
        cs = data.get('credit_score', 700)
        if cs >= 750:
            score += 30
        elif cs >= 700:
            score += 24
        elif cs >= 650:
            score += 18
        elif cs >= 600:
            score += 10
        else:
            score += 0

        # 2. Monthly Income (20 pts max)
        income = data.get('income', 50000)
        if income >= 75000:
            score += 20
        elif income >= 50000:
            score += 16
        elif income >= 30000:
            score += 12
        elif income >= 20000:
            score += 8
        else:
            score += 0

        # 3. Employment (15 pts max)
        emp = data.get('employment_status', 'Salaried')
        if emp == 'Salaried':
            score += 15
        elif emp in ['Self-Employed', 'Business Owner']:
            score += 10
        else:
            score += 0

        # 4. Debt-to-Income DTI (15 pts max)
        dti = data.get('debt_to_income', 0.2)
        if dti < 0.20:
            score += 15
        elif dti < 0.35:
            score += 11
        elif dti < 0.45:
            score += 5
        else:
            score += 0

        # 5. Previous Default (10 pts max)
        prev_def = data.get('previous_default', 0)
        if prev_def == 0:
            score += 10
        else:
            score += 0

        # 6. Savings (5 pts max)
        savings = data.get('savings', 50000)
        annual_inc = income * 12
        savings_ratio = savings / max(annual_inc, 1)
        if savings_ratio >= 0.3:
            score += 5
        elif savings_ratio >= 0.15:
            score += 3
        else:
            score += 1

        # 7. Age (5 pts max)
        age = data.get('age', 30)
        if 23 <= age <= 60:
            score += 5
        elif age >= 18:
            score += 3
        else:
            score += 0

        return round(float(np.clip(score, 0, 100)), 2)

    def evaluate(self, data):
        """
        Runs the full expert rule inference engine against the input profile.
        Returns triggered rules, risk factors, positive factors, rule score, and critical flags.
        """
        triggered_rules = []
        positive_factors = []
        risk_factors = []
        critical_flags = []
        
        has_critical_fail = False

        for rule in self.rules:
            is_triggered = evaluate_rule_condition(rule['condition'], data)
            
            rule_entry = {
                "id": rule['id'],
                "name": rule['name'],
                "condition": rule['condition'],
                "severity": rule['severity'],
                "result": rule['result'],
                "explanation": rule['explanation'],
                "category": rule['category'],
                "triggered": is_triggered
            }
            
            if is_triggered:
                triggered_rules.append(rule_entry)
                
                if rule['severity'] == 'critical':
                    has_critical_fail = True
                    critical_flags.append(rule['explanation'])
                    risk_factors.append(f"CRITICAL: {rule['explanation']}")
                elif rule['severity'] == 'high':
                    risk_factors.append(rule['explanation'])
                elif rule['severity'] == 'medium':
                    risk_factors.append(rule['explanation'])
                elif rule['severity'] == 'positive':
                    positive_factors.append(rule['explanation'])

        rule_score = self.calculate_rule_score(data)
        
        # Rule-based decision recommendation
        if has_critical_fail or rule_score < 50:
            recommendation = "NOT_ELIGIBLE"
        elif rule_score >= 75 and len(critical_flags) == 0:
            recommendation = "ELIGIBLE"
        else:
            recommendation = "CONDITIONALLY_ELIGIBLE"

        return {
            "status": recommendation,
            "rule_score": rule_score,
            "has_critical_fail": has_critical_fail,
            "critical_flags": critical_flags,
            "triggered_rules": triggered_rules,
            "positive_factors": list(set(positive_factors)),
            "risk_factors": list(set(risk_factors))
        }

if __name__ == '__main__':
    engine = ExpertInferenceEngine()
    test_data = {
        'age': 30,
        'income': 80000,
        'credit_score': 780,
        'loan_amount': 200000,
        'existing_emi': 10000,
        'debt': 20000,
        'monthly_expenses': 25000,
        'savings': 200000,
        'dependents': 1,
        'previous_default': 0,
        'employment_status': 'Salaried',
        'debt_to_income': 0.125,
        'emi_ratio': 0.125,
        'disposable_income': 45000,
        'loan_to_income': 0.208,
        'savings_ratio': 0.208,
        'financial_health_score': 88
    }
    res = engine.evaluate(test_data)
    print("Inference Engine Test Result:", res['status'], "Score:", res['rule_score'])

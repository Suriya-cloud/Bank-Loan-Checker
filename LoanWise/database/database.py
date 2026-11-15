import os
import sqlite3
import json

from database.schema import CREATE_ASSESSMENTS_TABLE, CREATE_MODEL_METRICS_TABLE, CREATE_RULE_RESULTS_TABLE

DB_DIR = os.path.dirname(__file__)
DB_PATH = os.path.join(DB_DIR, 'loanwise.db')

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(CREATE_ASSESSMENTS_TABLE)
    cursor.execute(CREATE_MODEL_METRICS_TABLE)
    cursor.execute(CREATE_RULE_RESULTS_TABLE)
    conn.commit()
    conn.close()
    print("Database initialized at:", DB_PATH)

def save_assessment(raw_input, result):
    conn = get_db_connection()
    cursor = conn.cursor()

    applicant_name = raw_input.get('applicant_name', 'Anonymous Applicant')
    age = raw_input.get('age', 30)
    income = raw_input.get('income', 50000)
    credit_score = raw_input.get('credit_score', 700)
    loan_amount = raw_input.get('loan_amount', 200000)
    loan_term = raw_input.get('loan_term', 36)
    employment_status = raw_input.get('employment_status', 'Salaried')

    fin = result.get('financial_metrics', {})
    dti = fin.get('dti', 0.1)
    emi_ratio = fin.get('emi_ratio', 0.1)
    disposable_income = fin.get('disposable_income', 25000)

    final_score = result.get('final_score', 0)
    ml_score = result.get('ml_score', 0)
    rule_score = result.get('rule_score', 0)
    financial_score = result.get('financial_score', 0)
    risk_level = result.get('risk_level', 'UNKNOWN')
    decision = result.get('decision', 'UNKNOWN')
    confidence = result.get('confidence', 'MEDIUM')

    cursor.execute("""
        INSERT INTO assessments (
            applicant_name, age, income, credit_score, loan_amount, loan_term,
            employment_status, dti, emi_ratio, disposable_income,
            final_score, ml_score, rule_score, financial_score,
            risk_level, decision, confidence, raw_input_json, full_result_json
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        applicant_name, age, income, credit_score, loan_amount, loan_term,
        employment_status, dti, emi_ratio, disposable_income,
        final_score, ml_score, rule_score, financial_score,
        risk_level, decision, confidence,
        json.dumps(raw_input), json.dumps(result)
    ))

    assessment_id = cursor.lastrowid

    # Save rule results
    for rule in result.get('triggered_rules', []):
        cursor.execute("""
            INSERT INTO rule_results (assessment_id, rule_id, rule_name, triggered, severity)
            VALUES (?, ?, ?, ?, ?)
        """, (
            assessment_id,
            rule.get('id', 'R000'),
            rule.get('name', 'Rule'),
            1 if rule.get('triggered', True) else 0,
            rule.get('severity', 'medium')
        ))

    conn.commit()
    conn.close()
    return assessment_id

def get_all_assessments():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, created_at, applicant_name, age, income, credit_score, loan_amount,
               final_score, ml_score, rule_score, financial_score, risk_level, decision, confidence
        FROM assessments
        ORDER BY created_at DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_assessment_by_id(assessment_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM assessments WHERE id = ?", (assessment_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        data = dict(row)
        data['raw_input'] = json.loads(data['raw_input_json']) if data.get('raw_input_json') else {}
        data['full_result'] = json.loads(data['full_result_json']) if data.get('full_result_json') else {}
        return data
    return None

def delete_assessment(assessment_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM assessments WHERE id = ?", (assessment_id,))
    cursor.execute("DELETE FROM rule_results WHERE assessment_id = ?", (assessment_id,))
    conn.commit()
    conn.close()
    return True

def get_dashboard_summary():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) as total FROM assessments")
    total = cursor.fetchone()['total']
    
    cursor.execute("SELECT COUNT(*) as cnt FROM assessments WHERE decision = 'ELIGIBLE'")
    eligible = cursor.fetchone()['cnt']
    
    cursor.execute("SELECT COUNT(*) as cnt FROM assessments WHERE decision = 'CONDITIONALLY_ELIGIBLE'")
    conditional = cursor.fetchone()['cnt']
    
    cursor.execute("SELECT COUNT(*) as cnt FROM assessments WHERE decision = 'NOT_ELIGIBLE'")
    not_eligible = cursor.fetchone()['cnt']

    cursor.execute("SELECT COUNT(*) as cnt FROM assessments WHERE risk_level = 'HIGH'")
    high_risk = cursor.fetchone()['cnt']

    cursor.execute("SELECT AVG(final_score) as avg_score, AVG(credit_score) as avg_cs FROM assessments")
    avg_row = cursor.fetchone()
    avg_score = round(avg_row['avg_score'], 1) if avg_row['avg_score'] else 0.0
    avg_credit = round(avg_row['avg_cs'], 1) if avg_row['avg_cs'] else 0.0

    conn.close()
    return {
        'total_assessments': total,
        'eligible': eligible,
        'conditionally_eligible': conditional,
        'not_eligible': not_eligible,
        'high_risk': high_risk,
        'average_score': avg_score,
        'average_credit_score': avg_credit
    }

if __name__ == '__main__':
    init_db()

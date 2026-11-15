CREATE_ASSESSMENTS_TABLE = """
CREATE TABLE IF NOT EXISTS assessments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    applicant_name TEXT DEFAULT 'Anonymous Applicant',
    age INTEGER,
    income REAL,
    credit_score INTEGER,
    loan_amount REAL,
    loan_term INTEGER,
    employment_status TEXT,
    dti REAL,
    emi_ratio REAL,
    disposable_income REAL,
    final_score REAL,
    ml_score REAL,
    rule_score REAL,
    financial_score REAL,
    risk_level TEXT,
    decision TEXT,
    confidence TEXT,
    raw_input_json TEXT,
    full_result_json TEXT
);
"""

CREATE_MODEL_METRICS_TABLE = """
CREATE TABLE IF NOT EXISTS model_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    model_name TEXT,
    purpose TEXT,
    accuracy REAL,
    precision REAL,
    recall REAL,
    f1 REAL,
    roc_auc REAL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

CREATE_RULE_RESULTS_TABLE = """
CREATE TABLE IF NOT EXISTS rule_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    assessment_id INTEGER,
    rule_id TEXT,
    rule_name TEXT,
    triggered INTEGER,
    severity TEXT,
    FOREIGN KEY(assessment_id) REFERENCES assessments(id) ON DELETE CASCADE
);
"""

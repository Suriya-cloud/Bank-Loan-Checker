# LoanWise — Hybrid AI Loan Eligibility & Credit Risk Expert System

LoanWise is an educational full-stack **Hybrid AI Loan Eligibility and Credit Risk Expert System**. It combines statistical Machine Learning classifiers with deterministic Expert System rules and financial health analysis into an ensemble decision engine with transparent Explainable AI (XAI) outputs.

---

## 🌟 Key Features

* **Hybrid AI Decision Engine**: Blends ML probabilities (50%), Expert Rule scores (30%), and Financial Health ratios (20%).
* **4 Machine Learning Classifiers**: Trains Logistic Regression, Random Forest, Decision Tree, and Gradient Boosting / XGBoost.
* **15+ Domain Expert Rules**: Enforces legal age limits, debt-to-income (DTI) bounds, negative disposable income overrides, and credit thresholds.
* **Model Consensus & Disagreement Detection**: Measures prediction variance across models and assigns consensus confidence levels (*High*, *Medium*, *Low*).
* **5 Standardized Datasets**: Analyzes data from Loan Approval, Credit Risk, Loan Default, Customer Financial, and Personal Loan datasets.
* **Explainable AI (XAI)**: Displays why a decision was made, triggered rules, model disagreement alerts, and feature importances.
* **Interactive Web Dashboard & Simulator**: Includes a 5-step assessment wizard, pre-filled demo profiles, real-time rule simulator, loan EMI calculator, analytics dashboard, and SQLite audit history log.

---

## 🏗️ System Architecture

```text
User Input / Assessment Wizard
             ↓
Data Preprocessing & Derived Ratios (DTI, EMI Ratio, Disposable Income, Financial Health)
             ↓
 ┌─────────────────────────────────────────┐
 │            ML MODEL LAYER               │
 │                                         │
 │ Logistic Regression   (Probability)     │
 │ Random Forest         (Risk & Features) │
 │ Decision Tree         (Rule Path)       │
 │ XGBoost / GradBoost   (High-Perf)       │
 └────────────────────┬────────────────────┘
                      ↓
              Model Predictions
                      ↓
 ┌─────────────────────────────────────────┐
 │          EXPERT RULE ENGINE             │
 │          (15 Domain Rules)              │
 └────────────────────┬────────────────────┘
                      ↓
            Rule-Based Assessment
                      ↓
 ┌─────────────────────────────────────────┐
 │        ENSEMBLE DECISION ENGINE         │
 │     50% ML + 30% Rules + 20% Financial  │
 └────────────────────┬────────────────────┘
                      ↓
           FINAL ELIGIBILITY & RISK
                      ↓
    EXPLAINABLE AI REPORT & DB HISTORICAL LOG
```

---

## 📁 Project Structure

```text
LoanWise/
├── app.py                      # Main Flask application & REST API server
├── config.py                   # Configuration settings & ensemble weights
├── generate_data.py            # Raw dataset generation script
├── requirements.txt            # Python dependencies
├── README.md                   # System documentation
│
├── data/
│   ├── raw/                    # 5 raw CSV datasets
│   └── processed/              # Processed master dataset
│
├── models/                     # Saved joblib models, scaler, encoder & metrics
│   ├── logistic_regression.pkl
│   ├── random_forest.pkl
│   ├── decision_tree.pkl
│   ├── xgboost_model.pkl
│   ├── scaler.pkl
│   ├── feature_encoder.pkl
│   └── model_metrics.json
│
├── ml/                         # Machine learning pipeline modules
│   ├── preprocess.py           # Feature engineering & scaling
│   ├── train_models.py        # Model training & evaluation pipeline
│   ├── evaluate_models.py     # Metrics loader
│   ├── predict.py             # Inference predictor
│   └── ensemble.py            # Ensemble decision engine
│
├── expert_system/              # Rule engine
│   ├── rules.py               # Condition evaluator
│   ├── inference_engine.py    # Rule engine evaluator & score calculator
│   └── knowledge_base.json    # 15 domain expert rules
│
├── database/                   # SQLite database persistence
│   ├── database.py            # Connection & DB queries
│   └── schema.py              # DDL table schemas
│
├── templates/                  # Jinja2 HTML templates
│   ├── base.html
│   ├── index.html
│   ├── assessment.html
│   ├── analyzing.html
│   ├── result.html
│   ├── dashboard.html
│   ├── models.html
│   ├── datasets.html
│   ├── rules.html
│   ├── history.html
│   └── about.html
│
├── static/                     # CSS & JS assets
│   ├── css/style.css
│   └── js/
│       ├── main.js
│       ├── assessment.js
│       ├── result.js
│       └── dashboard.js
│
└── tests/                      # Automated test suite
    ├── test_rules.py
    ├── test_models.py
    └── test_api.py
```

---

## 🚀 Quick Start & Installation

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Generate Data & Train Models

```bash
python generate_data.py
python ml/train_models.py
```

### 3. Run Application Server

```bash
python app.py
```

Open your browser at: `http://127.0.0.1:5000`

---

## 🧪 Running Automated Tests

Run the full pytest suite:

```bash
pytest tests/
```

---

## 📡 REST API Documentation

* `POST /api/predict`: Runs full hybrid assessment pipeline and saves record to DB.
* `POST /api/expert-analysis`: Executes expert rules only.
* `POST /api/ml-predict`: Runs all 4 ML models.
* `GET /api/models`: Returns evaluation metrics (Accuracy, Precision, Recall, F1, ROC-AUC).
* `GET /api/datasets`: Returns dataset statistics for all 5 CSV files.
* `GET /api/rules`: Returns knowledge base JSON rules.
* `GET /api/history`: Returns historical assessment log from SQLite database.
* `POST /api/calculator`: Financial loan EMI calculator endpoint.

---

## ⚖️ Responsible AI & Disclaimer

LoanWise is an **educational AI prototype**. Results are generated using simplified machine-learning models and expert rules and do not represent an actual bank's lending decision, credit score, or guarantee of approval. LoanWise strictly excludes protected attributes (race, gender, religion, caste) from all decision pipelines.

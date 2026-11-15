import os
import pandas as pd
import numpy as np

# Set random seed for reproducibility
np.random.seed(42)

DATA_DIR = os.path.join(os.path.dirname(__file__), 'data', 'raw')
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(os.path.join(os.path.dirname(__file__), 'data', 'processed'), exist_ok=True)
os.makedirs(os.path.join(os.path.dirname(__file__), 'models'), exist_ok=True)

# 1. Loan Approval Dataset (614 rows)
n_approval = 614
loan_approval_df = pd.DataFrame({
    'Loan_ID': [f'LP00{1000+i}' for i in range(n_approval)],
    'Gender': np.random.choice(['Male', 'Female'], size=n_approval, p=[0.8, 0.2]),
    'Married': np.random.choice(['Yes', 'No'], size=n_approval, p=[0.65, 0.35]),
    'Dependents': np.random.choice(['0', '1', '2', '3+'], size=n_approval, p=[0.58, 0.17, 0.17, 0.08]),
    'Education': np.random.choice(['Graduate', 'Not Graduate'], size=n_approval, p=[0.78, 0.22]),
    'Self_Employed': np.random.choice(['No', 'Yes'], size=n_approval, p=[0.85, 0.15]),
    'ApplicantIncome': np.random.randint(15000, 150000, size=n_approval),
    'CoapplicantIncome': np.random.choice([0, 15000, 25000, 40000], size=n_approval, p=[0.4, 0.3, 0.2, 0.1]),
    'LoanAmount': np.random.randint(50000, 800000, size=n_approval),
    'Loan_Amount_Term': np.random.choice([120, 180, 240, 360, 480], size=n_approval, p=[0.05, 0.1, 0.1, 0.7, 0.05]),
    'Credit_History': np.random.choice([1.0, 0.0], size=n_approval, p=[0.84, 0.16]),
    'Property_Area': np.random.choice(['Urban', 'Semiurban', 'Rural'], size=n_approval, p=[0.33, 0.38, 0.29]),
})

# Calculate realistic status based on income and credit history
status_score = (
    (loan_approval_df['Credit_History'] == 1.0) * 0.5 +
    (loan_approval_df['ApplicantIncome'] > 40000) * 0.25 +
    (loan_approval_df['Education'] == 'Graduate') * 0.15 +
    (loan_approval_df['LoanAmount'] / (loan_approval_df['ApplicantIncome'] * 12 + 1) < 0.4) * 0.1
)
loan_approval_df['Loan_Status'] = np.where(status_score + np.random.normal(0, 0.1, n_approval) > 0.5, 'Y', 'N')
loan_approval_df.to_csv(os.path.join(DATA_DIR, 'loan_approval.csv'), index=False)
print("Saved loan_approval.csv")

# 2. Credit Risk Dataset (800 rows)
n_risk = 800
age = np.random.randint(18, 70, size=n_risk)
income = np.random.randint(18000, 180000, size=n_risk)
credit_score = np.random.randint(300, 850, size=n_risk)
debt = np.random.randint(0, 50000, size=n_risk)
loan_amt = np.random.randint(30000, 600000, size=n_risk)

risk_metric = (credit_score - 300) / 550.0 * 0.45 + (income / 180000.0) * 0.35 - (debt / 50000.0) * 0.20
risk_probs = risk_metric + np.random.normal(0, 0.08, n_risk)

risk_cat = []
for score in risk_probs:
    if score > 0.55:
        risk_cat.append('Low')
    elif score > 0.35:
        risk_cat.append('Medium')
    else:
        risk_cat.append('High')

credit_risk_df = pd.DataFrame({
    'Age': age,
    'Income': income,
    'Employment': np.random.choice(['Employed', 'Self-Employed', 'Unemployed', 'Retired'], size=n_risk, p=[0.7, 0.15, 0.05, 0.1]),
    'CreditScore': credit_score,
    'Debt': debt,
    'LoanAmount': loan_amt,
    'LoanDuration': np.random.choice([12, 24, 36, 60, 120, 240, 360], size=n_risk),
    'PaymentHistory': np.random.choice(['Excellent', 'Good', 'Fair', 'Poor'], size=n_risk, p=[0.4, 0.3, 0.2, 0.1]),
    'ExistingLoans': np.random.randint(0, 5, size=n_risk),
    'DefaultHistory': np.random.choice(['No', 'Yes'], size=n_risk, p=[0.85, 0.15]),
    'Risk': risk_cat
})
credit_risk_df.to_csv(os.path.join(DATA_DIR, 'credit_risk.csv'), index=False)
print("Saved credit_risk.csv")

# 3. Loan Default Dataset (1000 rows)
n_default = 1000
def_age = np.random.randint(21, 65, size=n_default)
def_inc = np.random.randint(20000, 160000, size=n_default)
def_score = np.random.randint(300, 850, size=n_default)
def_prev = np.random.choice([0, 1], size=n_default, p=[0.88, 0.12])
def_dti = np.random.uniform(0.05, 0.65, size=n_default)

default_prob = 1 / (1 + np.exp(-(-0.005 * (def_score - 650) - 0.00002 * (def_inc - 50000) + 4.0 * def_dti + 2.5 * def_prev - 1.5)))
default_label = (np.random.uniform(0, 1, n_default) < default_prob).astype(int)

loan_default_df = pd.DataFrame({
    'Age': def_age,
    'Income': def_inc,
    'LoanAmount': np.random.randint(50000, 750000, size=n_default),
    'InterestRate': np.round(np.random.uniform(5.5, 18.5, size=n_default), 2),
    'LoanTerm': np.random.choice([12, 36, 60, 180, 360], size=n_default),
    'EmploymentLength': np.random.randint(0, 30, size=n_default),
    'DebtToIncomeRatio': np.round(def_dti, 3),
    'CreditScore': def_score,
    'PreviousDefault': def_prev,
    'NumberOfAccounts': np.random.randint(1, 10, size=n_default),
    'Default': default_label
})
loan_default_df.to_csv(os.path.join(DATA_DIR, 'loan_default.csv'), index=False)
print("Saved loan_default.csv")

# 4. Customer Financial Dataset (750 rows)
n_cust = 750
cust_inc = np.random.randint(22000, 200000, size=n_cust)
cust_exp = np.round(cust_inc * np.random.uniform(0.3, 0.7, size=n_cust), 2)
cust_emi = np.round(cust_inc * np.random.uniform(0.0, 0.35, size=n_cust), 2)

customer_financial_df = pd.DataFrame({
    'CustomerID': [f'CUST-{10000+i}' for i in range(n_cust)],
    'Age': np.random.randint(20, 68, size=n_cust),
    'MonthlyIncome': cust_inc,
    'MonthlyExpenses': cust_exp,
    'Savings': np.random.randint(10000, 1000000, size=n_cust),
    'ExistingEMI': cust_emi,
    'CreditScore': np.random.randint(300, 850, size=n_cust),
    'EmploymentStatus': np.random.choice(['Salaried', 'Self-Employed', 'Business Owner', 'Unemployed'], size=n_cust, p=[0.65, 0.20, 0.10, 0.05]),
    'Dependents': np.random.randint(0, 5, size=n_cust),
    'Debt': np.random.randint(0, 600000, size=n_cust)
})
customer_financial_df.to_csv(os.path.join(DATA_DIR, 'customer_financial.csv'), index=False)
print("Saved customer_financial.csv")

# 5. Personal Loan Dataset (900 rows)
n_pl = 900
pl_inc = np.random.randint(20000, 200000, size=n_pl)
pl_cc = np.random.choice([0, 1], size=n_pl, p=[0.75, 0.25])
pl_cd = np.random.choice([0, 1], size=n_pl, p=[0.92, 0.08])

pl_prob = 1 / (1 + np.exp(-(-3.0 + 0.00003 * pl_inc + 2.0 * pl_cd + 1.2 * pl_cc)))
pl_target = (np.random.uniform(0, 1, n_pl) < pl_prob).astype(int)

personal_loan_df = pd.DataFrame({
    'Age': np.random.randint(23, 65, size=n_pl),
    'Experience': np.random.randint(1, 40, size=n_pl),
    'Income': pl_inc,
    'Family': np.random.randint(1, 5, size=n_pl),
    'Education': np.random.choice([1, 2, 3], size=n_pl, p=[0.4, 0.4, 0.2]),
    'Mortgage': np.random.choice([0, 50000, 120000, 250000], size=n_pl, p=[0.6, 0.2, 0.1, 0.1]),
    'SecuritiesAccount': np.random.choice([0, 1], size=n_pl, p=[0.9, 0.1]),
    'CDAccount': pl_cd,
    'Online': np.random.choice([0, 1], size=n_pl, p=[0.6, 0.4]),
    'CreditCard': pl_cc,
    'PersonalLoan': pl_target
})
personal_loan_df.to_csv(os.path.join(DATA_DIR, 'personal_loan.csv'), index=False)
print("Saved personal_loan.csv")
print("All 5 datasets successfully generated!")

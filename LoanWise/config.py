import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'loanwise-hybrid-ai-secret-key-2026')
    DEBUG = True
    PORT = int(os.environ.get('PORT', 5000))
    
    # Ensemble Decision Engine Weighting Configurations
    ML_SCORE_WEIGHT = 0.50
    EXPERT_RULE_WEIGHT = 0.30
    FINANCIAL_HEALTH_WEIGHT = 0.20
    
    # Paths
    DATABASE_PATH = os.path.join(BASE_DIR, 'database', 'loanwise.db')
    MODELS_DIR = os.path.join(BASE_DIR, 'models')
    RAW_DATA_DIR = os.path.join(BASE_DIR, 'data', 'raw')
    KNOWLEDGE_BASE_PATH = os.path.join(BASE_DIR, 'expert_system', 'knowledge_base.json')

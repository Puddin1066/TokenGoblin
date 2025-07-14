import os
from typing import List
from dotenv import load_dotenv

load_dotenv()

# Bot Configuration
TOKEN = os.getenv("TOKEN")
ADMIN_ID_LIST = [int(x.strip()) for x in os.getenv("ADMIN_ID_LIST", "").split(",") if x.strip()]
SUPPORT_LINK = os.getenv("SUPPORT_LINK", "https://t.me/your_username")

# Agentic Features
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
AGENTIC_MODE = os.getenv("AGENTIC_MODE", "false").lower() == "true"

# Database Configuration
DB_NAME = os.getenv("DB_NAME", "database.db")
DB_ENCRYPTION = os.getenv("DB_ENCRYPTION", "false").lower() == "true"
DB_PASS = os.getenv("DB_PASS", "")

# Payment Processing
WEB3_PROVIDER_URL = os.getenv("WEB3_PROVIDER_URL")
KRYPTO_EXPRESS_API_KEY = os.getenv("KRYPTO_EXPRESS_API_KEY")
KRYPTO_EXPRESS_API_URL = os.getenv("KRYPTO_EXPRESS_API_URL", "https://kryptoexpress.pro/api")
KRYPTO_EXPRESS_API_SECRET = os.getenv("KRYPTO_EXPRESS_API_SECRET")

# Task Queue
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "")
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", f"redis://{REDIS_HOST}:6379")

# Monitoring
PROMETHEUS_ENDPOINT = os.getenv("PROMETHEUS_ENDPOINT", "localhost:9090")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

# Agentic Configuration
MIN_INVENTORY_THRESHOLD = int(os.getenv("MIN_INVENTORY_THRESHOLD", "1000"))
MAX_PURCHASE_BUDGET = float(os.getenv("MAX_PURCHASE_BUDGET", "500"))
OPPORTUNITY_CHECK_INTERVAL = int(os.getenv("OPPORTUNITY_CHECK_INTERVAL", "3600"))
PRICING_UPDATE_INTERVAL = int(os.getenv("PRICING_UPDATE_INTERVAL", "1800"))

# Lead Scoring Weights
LEAD_SCORING_WEIGHTS = {
    'browse_frequency': float(os.getenv("BROWSE_FREQUENCY_WEIGHT", "0.3")),
    'cart_abandonment': float(os.getenv("CART_ABANDONMENT_WEIGHT", "0.25")),
    'session_duration': float(os.getenv("SESSION_DURATION_WEIGHT", "0.2")),
    'previous_purchases': float(os.getenv("PREVIOUS_PURCHASES_WEIGHT", "0.15")),
    'engagement_level': float(os.getenv("ENGAGEMENT_LEVEL_WEIGHT", "0.1"))
}

# Pricing Configuration
PRICING_CONFIG = {
    'min_markup': float(os.getenv("MIN_MARKUP", "0.1")),
    'max_markup': float(os.getenv("MAX_MARKUP", "0.5")),
    'competitor_weight': float(os.getenv("COMPETITOR_WEIGHT", "0.4")),
    'demand_weight': float(os.getenv("DEMAND_WEIGHT", "0.3")),
    'cost_weight': float(os.getenv("COST_WEIGHT", "0.3"))
}

# Inventory Configuration
INVENTORY_CONFIG = {
    'min_inventory_threshold': MIN_INVENTORY_THRESHOLD,
    'max_purchase_budget': MAX_PURCHASE_BUDGET,
    'restock_lead_time': int(os.getenv("RESTOCK_LEAD_TIME", "3600")),
    'demand_prediction_days': int(os.getenv("DEMAND_PREDICTION_DAYS", "7"))
}

# Webhook Configuration
WEBHOOK_PATH = os.getenv("WEBHOOK_PATH", "/")
WEBAPP_HOST = os.getenv("WEBAPP_HOST", "0.0.0.0")
WEBAPP_PORT = int(os.getenv("WEBAPP_PORT", "5000"))
WEBHOOK_SECRET_TOKEN = os.getenv("WEBHOOK_SECRET_TOKEN", "your_secret_token")

# NGROK Configuration
NGROK_TOKEN = os.getenv("NGROK_TOKEN")
PAGE_ENTRIES = int(os.getenv("PAGE_ENTRIES", "8"))
BOT_LANGUAGE = os.getenv("BOT_LANGUAGE", "en")
MULTIBOT = os.getenv("MULTIBOT", "false").lower() == "true"
CURRENCY = os.getenv("CURRENCY", "USD")
RUNTIME_ENVIRONMENT = os.getenv("RUNTIME_ENVIRONMENT", "prod")

# ETHPlorer Configuration
ETHPLORER_API_KEY = os.getenv("ETHPLORER_API_KEY")

# Claude Models Configuration
CLAUDE_MODELS = {
    'claude-3-sonnet': {
        'model_id': 'anthropic/claude-3-sonnet',
        'name': 'Claude 3 Sonnet',
        'default_price': 0.015,
        'context_length': 200000
    },
    'claude-3-opus': {
        'model_id': 'anthropic/claude-3-opus',
        'name': 'Claude 3 Opus',
        'default_price': 0.015,
        'context_length': 200000
    },
    'claude-3-haiku': {
        'model_id': 'anthropic/claude-3-haiku',
        'name': 'Claude 3 Haiku',
        'default_price': 0.00025,
        'context_length': 200000
    }
}

# Rate Limiting
RATE_LIMIT_PER_USER = int(os.getenv("RATE_LIMIT_PER_USER", "100"))
RATE_LIMIT_PER_IP = int(os.getenv("RATE_LIMIT_PER_IP", "1000"))

# Caching Configuration
CACHE_TTL = int(os.getenv("CACHE_TTL", "3600"))
CACHE_PREFIX = os.getenv("CACHE_PREFIX", "ai_bot:")

# Validation
if not TOKEN:
    raise ValueError("TOKEN environment variable is required")

if AGENTIC_MODE and not OPENROUTER_API_KEY:
    raise ValueError("OPENROUTER_API_KEY is required when AGENTIC_MODE is enabled")

if AGENTIC_MODE and not ANTHROPIC_API_KEY:
    raise ValueError("ANTHROPIC_API_KEY is required when AGENTIC_MODE is enabled")

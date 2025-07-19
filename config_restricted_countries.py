import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# === CORE BOT CONFIGURATION ===
BOT_TOKEN = os.getenv("BOT_TOKEN")
MULTIBOT = os.getenv("MULTIBOT", "False") == "True"
RUNTIME_ENVIRONMENT = os.getenv("RUNTIME_ENVIRONMENT", "dev")

# === ADMIN CONFIGURATION ===
ADMIN_ID_LIST = list(map(int, os.getenv("ADMIN_ID_LIST", "").split(","))) if os.getenv("ADMIN_ID_LIST") else []
SUPPORT_LINK = os.getenv("SUPPORT_LINK", "https://t.me/support")

# === DATABASE CONFIGURATION ===
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///bot_restricted.db")
DB_ENCRYPTION = os.getenv("DB_ENCRYPTION", "False") == "True"
DB_ENCRYPTION_KEY = os.getenv("DB_ENCRYPTION_KEY")

# === REDIS CONFIGURATION ===
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")

# === WEBHOOK CONFIGURATION ===
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
WEBHOOK_SECRET_TOKEN = os.getenv("WEBHOOK_SECRET_TOKEN")
WEBHOOK_PATH = os.getenv("WEBHOOK_PATH", "/webhook")
WEB_SERVER_HOST = os.getenv("WEB_SERVER_HOST", "localhost")
WEB_SERVER_PORT = int(os.getenv("WEB_SERVER_PORT", 8080))

# === AI API CONFIGURATION ===
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Preferred AI model for restricted regions
DEFAULT_AI_MODEL = os.getenv("DEFAULT_AI_MODEL", "anthropic/claude-3-haiku")

# === CRYPTOCURRENCY PAYMENT CONFIGURATION ===

# Master wallet seed for deterministic address generation
MASTER_WALLET_SEED = os.getenv("MASTER_WALLET_SEED", "change_this_in_production")

# Supported cryptocurrencies for restricted regions
SUPPORTED_CRYPTOCURRENCIES = {
    'USDT_TRC20': {
        'enabled': os.getenv("USDT_TRC20_ENABLED", "True") == "True",
        'contract_address': 'TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t',
        'min_amount': float(os.getenv("USDT_TRC20_MIN_AMOUNT", "1.0")),
        'preferred_regions': ['zh-hans', 'ru']
    },
    'BTC': {
        'enabled': os.getenv("BTC_ENABLED", "True") == "True",
        'min_amount': float(os.getenv("BTC_MIN_AMOUNT", "0.0001")),
        'preferred_regions': ['fa', 'ar']
    }
}

# External API keys for blockchain monitoring
TRONGRID_API_KEY = os.getenv("TRONGRID_API_KEY")  # Optional - uses free tier if not set
BLOCKCYPHER_API_TOKEN = os.getenv("BLOCKCYPHER_API_TOKEN")  # Optional - uses free tier if not set

# === REGIONAL TARGETING CONFIGURATION ===

# Region-specific pricing multipliers
REGIONAL_PRICING_MULTIPLIERS = {
    'ru': float(os.getenv("PRICING_MULTIPLIER_RU", "2.5")),     # Russia
    'zh-hans': float(os.getenv("PRICING_MULTIPLIER_CN", "3.0")), # China
    'fa': float(os.getenv("PRICING_MULTIPLIER_IR", "2.8")),     # Iran
    'ar': float(os.getenv("PRICING_MULTIPLIER_AR", "2.2")),     # Middle East
    'default': float(os.getenv("PRICING_MULTIPLIER_DEFAULT", "2.0"))
}

# Minimum confidence threshold for region detection
REGION_DETECTION_THRESHOLD = float(os.getenv("REGION_DETECTION_THRESHOLD", "0.3"))

# === AGENTIC MARKETING CONFIGURATION ===

# Marketing campaign intervals (in hours)
MARKETING_INTERVALS = {
    'cart_abandonment': int(os.getenv("CART_ABANDONMENT_INTERVAL", "2")),
    'prospect_nurture': int(os.getenv("PROSPECT_NURTURE_INTERVAL", "24")),
    'retention': int(os.getenv("RETENTION_INTERVAL", "72")),
    'viral_referral': int(os.getenv("VIRAL_REFERRAL_INTERVAL", "168"))
}

# Lead scoring weights for behavioral analysis
LEAD_SCORING_WEIGHTS = {
    'browse_frequency': float(os.getenv("WEIGHT_BROWSE_FREQUENCY", "0.30")),
    'cart_abandonment': float(os.getenv("WEIGHT_CART_ABANDONMENT", "0.25")),
    'session_duration': float(os.getenv("WEIGHT_SESSION_DURATION", "0.20")),
    'previous_purchases': float(os.getenv("WEIGHT_PREVIOUS_PURCHASES", "0.15")),
    'engagement_level': float(os.getenv("WEIGHT_ENGAGEMENT_LEVEL", "0.10"))
}

# Lead scoring threshold for marketing actions
LEAD_SCORE_THRESHOLD = float(os.getenv("LEAD_SCORE_THRESHOLD", "0.7"))

# === TOKEN PRICING CONFIGURATION ===

# Base token pricing (before regional multipliers)
BASE_TOKEN_PACKAGES = {
    'starter': {
        'tokens': 1000,
        'base_price_usd': float(os.getenv("STARTER_BASE_PRICE", "10.0")),
        'markup_percentage': float(os.getenv("STARTER_MARKUP", "0.25"))
    },
    'standard': {
        'tokens': 5000,
        'base_price_usd': float(os.getenv("STANDARD_BASE_PRICE", "45.0")),
        'markup_percentage': float(os.getenv("STANDARD_MARKUP", "0.20"))
    },
    'premium': {
        'tokens': 15000,
        'base_price_usd': float(os.getenv("PREMIUM_BASE_PRICE", "120.0")),
        'markup_percentage': float(os.getenv("PREMIUM_MARKUP", "0.18"))
    },
    'enterprise': {
        'tokens': 50000,
        'base_price_usd': float(os.getenv("ENTERPRISE_BASE_PRICE", "350.0")),
        'markup_percentage': float(os.getenv("ENTERPRISE_MARKUP", "0.15"))
    }
}

# Dynamic pricing adjustments
DYNAMIC_PRICING_ENABLED = os.getenv("DYNAMIC_PRICING_ENABLED", "True") == "True"
DISCOUNT_RANGES = {
    'new_user': (10, 25),      # 10-25% discount for new users
    'loyal_customer': (5, 15), # 5-15% discount for returning customers
    'bulk_purchase': (15, 30), # 15-30% discount for large purchases
    'regional_special': (20, 40) # 20-40% discount for restricted regions
}

# === PAYMENT MONITORING CONFIGURATION ===

# Payment confirmation requirements
PAYMENT_CONFIRMATION_BLOCKS = {
    'BTC': int(os.getenv("BTC_CONFIRMATION_BLOCKS", "1")),
    'USDT_TRC20': int(os.getenv("USDT_CONFIRMATION_BLOCKS", "1"))
}

# Payment monitoring intervals (in seconds)
PAYMENT_MONITORING_INTERVALS = {
    'USDT_TRC20': int(os.getenv("USDT_MONITORING_INTERVAL", "60")),
    'BTC': int(os.getenv("BTC_MONITORING_INTERVAL", "90"))
}

# Payment expiration time (in hours)
PAYMENT_EXPIRATION_HOURS = int(os.getenv("PAYMENT_EXPIRATION_HOURS", "24"))

# Amount tolerance for payment validation (percentage)
PAYMENT_AMOUNT_TOLERANCE = float(os.getenv("PAYMENT_AMOUNT_TOLERANCE", "0.01"))  # 1%

# === SECURITY CONFIGURATION ===

# Rate limiting for restricted regions
RATE_LIMIT_REQUESTS = int(os.getenv("RATE_LIMIT_REQUESTS", "30"))
RATE_LIMIT_WINDOW = int(os.getenv("RATE_LIMIT_WINDOW", "60"))  # seconds

# Anti-fraud measures
FRAUD_DETECTION_ENABLED = os.getenv("FRAUD_DETECTION_ENABLED", "True") == "True"
MAX_PAYMENTS_PER_USER_PER_DAY = int(os.getenv("MAX_PAYMENTS_PER_USER_PER_DAY", "5"))
MAX_AMOUNT_PER_USER_PER_DAY = float(os.getenv("MAX_AMOUNT_PER_USER_PER_DAY", "1000.0"))

# IP and behavior analysis
SUSPICIOUS_BEHAVIOR_THRESHOLD = float(os.getenv("SUSPICIOUS_BEHAVIOR_THRESHOLD", "0.8"))

# === PRIVACY CONFIGURATION ===

# Data retention periods (in days)
USER_DATA_RETENTION_DAYS = int(os.getenv("USER_DATA_RETENTION_DAYS", "365"))
TRANSACTION_LOG_RETENTION_DAYS = int(os.getenv("TRANSACTION_LOG_RETENTION_DAYS", "2555"))  # 7 years
MARKETING_DATA_RETENTION_DAYS = int(os.getenv("MARKETING_DATA_RETENTION_DAYS", "90"))

# Privacy features for restricted regions
ANONYMOUS_MODE_ENABLED = os.getenv("ANONYMOUS_MODE_ENABLED", "True") == "True"
LOG_USER_IPS = os.getenv("LOG_USER_IPS", "False") == "True"
STORE_MESSAGE_CONTENT = os.getenv("STORE_MESSAGE_CONTENT", "False") == "True"

# === ANALYTICS CONFIGURATION ===

# Analytics tracking
ANALYTICS_ENABLED = os.getenv("ANALYTICS_ENABLED", "True") == "True"
ANALYTICS_RETENTION_DAYS = int(os.getenv("ANALYTICS_RETENTION_DAYS", "90"))

# Metrics tracking
TRACK_USER_BEHAVIOR = os.getenv("TRACK_USER_BEHAVIOR", "True") == "True"
TRACK_CONVERSION_FUNNEL = os.getenv("TRACK_CONVERSION_FUNNEL", "True") == "True"
TRACK_REGIONAL_PERFORMANCE = os.getenv("TRACK_REGIONAL_PERFORMANCE", "True") == "True"

# === NOTIFICATION CONFIGURATION ===

# Admin notifications
NOTIFY_ADMINS_NEW_PAYMENT = os.getenv("NOTIFY_ADMINS_NEW_PAYMENT", "True") == "True"
NOTIFY_ADMINS_HIGH_VALUE_USER = os.getenv("NOTIFY_ADMINS_HIGH_VALUE_USER", "True") == "True"
NOTIFY_ADMINS_SUSPICIOUS_ACTIVITY = os.getenv("NOTIFY_ADMINS_SUSPICIOUS_ACTIVITY", "True") == "True"

# Notification thresholds
HIGH_VALUE_PAYMENT_THRESHOLD = float(os.getenv("HIGH_VALUE_PAYMENT_THRESHOLD", "500.0"))
DAILY_REVENUE_NOTIFICATION_THRESHOLD = float(os.getenv("DAILY_REVENUE_THRESHOLD", "1000.0"))

# === DEVELOPMENT AND TESTING ===

# Development mode settings
DEBUG_MODE = os.getenv("DEBUG_MODE", "False") == "True"
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
ENABLE_TEST_PAYMENTS = os.getenv("ENABLE_TEST_PAYMENTS", "False") == "True"

# Test payment amounts (for development)
TEST_PAYMENT_AMOUNTS = {
    'USDT_TRC20': float(os.getenv("TEST_USDT_AMOUNT", "0.1")),
    'BTC': float(os.getenv("TEST_BTC_AMOUNT", "0.00001"))
}

# === LOCALIZATION CONFIGURATION ===

# Supported languages for restricted regions
SUPPORTED_LANGUAGES = ['en', 'ru', 'zh-hans', 'fa', 'ar']
DEFAULT_LANGUAGE = os.getenv("DEFAULT_LANGUAGE", "en")

# Auto-translate messages
AUTO_TRANSLATE_ENABLED = os.getenv("AUTO_TRANSLATE_ENABLED", "True") == "True"
TRANSLATION_API_KEY = os.getenv("TRANSLATION_API_KEY")  # Optional - for advanced translation

# === VIRAL MARKETING CONFIGURATION ===

# Referral program settings
REFERRAL_PROGRAM_ENABLED = os.getenv("REFERRAL_PROGRAM_ENABLED", "True") == "True"
REFERRER_COMMISSION_PERCENTAGE = float(os.getenv("REFERRER_COMMISSION_PERCENTAGE", "15.0"))
REFEREE_DISCOUNT_PERCENTAGE = float(os.getenv("REFEREE_DISCOUNT_PERCENTAGE", "10.0"))

# Viral coefficient targets
TARGET_VIRAL_COEFFICIENT = float(os.getenv("TARGET_VIRAL_COEFFICIENT", "1.2"))
VIRAL_CAMPAIGN_FREQUENCY_DAYS = int(os.getenv("VIRAL_CAMPAIGN_FREQUENCY_DAYS", "7"))

# === COMPLIANCE CONFIGURATION ===

# Legal and compliance settings
TERMS_OF_SERVICE_URL = os.getenv("TERMS_OF_SERVICE_URL", "https://example.com/terms")
PRIVACY_POLICY_URL = os.getenv("PRIVACY_POLICY_URL", "https://example.com/privacy")
AML_COMPLIANCE_ENABLED = os.getenv("AML_COMPLIANCE_ENABLED", "True") == "True"

# KYC requirements
KYC_THRESHOLD_USD = float(os.getenv("KYC_THRESHOLD_USD", "1000.0"))
KYC_REQUIRED_COUNTRIES = os.getenv("KYC_REQUIRED_COUNTRIES", "").split(",") if os.getenv("KYC_REQUIRED_COUNTRIES") else []

# === API RATE LIMITS ===

# External API rate limits (requests per minute)
COINGECKO_RATE_LIMIT = int(os.getenv("COINGECKO_RATE_LIMIT", "30"))
TRONGRID_RATE_LIMIT = int(os.getenv("TRONGRID_RATE_LIMIT", "100"))
BLOCKCYPHER_RATE_LIMIT = int(os.getenv("BLOCKCYPHER_RATE_LIMIT", "180"))  # Free tier: 3 req/sec

# === FEATURE FLAGS ===

# Feature toggles
FEATURE_GEO_TARGETING = os.getenv("FEATURE_GEO_TARGETING", "True") == "True"
FEATURE_AGENTIC_MARKETING = os.getenv("FEATURE_AGENTIC_MARKETING", "True") == "True"
FEATURE_DYNAMIC_PRICING = os.getenv("FEATURE_DYNAMIC_PRICING", "True") == "True"
FEATURE_BEHAVIORAL_ANALYSIS = os.getenv("FEATURE_BEHAVIORAL_ANALYSIS", "True") == "True"
FEATURE_AUTO_UPSELLING = os.getenv("FEATURE_AUTO_UPSELLING", "True") == "True"

# Advanced features
FEATURE_AI_CUSTOMER_SUPPORT = os.getenv("FEATURE_AI_CUSTOMER_SUPPORT", "False") == "True"
FEATURE_PREDICTIVE_ANALYTICS = os.getenv("FEATURE_PREDICTIVE_ANALYTICS", "False") == "True"
FEATURE_CUSTOM_MODELS = os.getenv("FEATURE_CUSTOM_MODELS", "False") == "True"

# === VALIDATION ===

def validate_config():
    """Validate critical configuration settings"""
    errors = []
    
    if not BOT_TOKEN:
        errors.append("BOT_TOKEN is required")
    
    if not OPENROUTER_API_KEY and not ANTHROPIC_API_KEY:
        errors.append("At least one AI API key is required (OPENROUTER_API_KEY or ANTHROPIC_API_KEY)")
    
    if MASTER_WALLET_SEED == "change_this_in_production" and RUNTIME_ENVIRONMENT == "production":
        errors.append("MASTER_WALLET_SEED must be changed in production")
    
    if not ADMIN_ID_LIST:
        errors.append("ADMIN_ID_LIST must contain at least one admin ID")
    
    if WEBHOOK_URL and not WEBHOOK_SECRET_TOKEN:
        errors.append("WEBHOOK_SECRET_TOKEN is required when using webhooks")
    
    if errors:
        raise ValueError(f"Configuration errors: {'; '.join(errors)}")

# Validate configuration on import
if RUNTIME_ENVIRONMENT == "production":
    validate_config()

# === EXPORT ALL SETTINGS ===
__all__ = [
    # Core settings
    'BOT_TOKEN', 'MULTIBOT', 'RUNTIME_ENVIRONMENT', 'ADMIN_ID_LIST',
    
    # Database and Redis
    'DATABASE_URL', 'REDIS_URL', 'DB_ENCRYPTION',
    
    # AI APIs
    'OPENROUTER_API_KEY', 'ANTHROPIC_API_KEY', 'DEFAULT_AI_MODEL',
    
    # Cryptocurrency
    'SUPPORTED_CRYPTOCURRENCIES', 'MASTER_WALLET_SEED',
    
    # Regional targeting
    'REGIONAL_PRICING_MULTIPLIERS', 'REGION_DETECTION_THRESHOLD',
    
    # Marketing
    'MARKETING_INTERVALS', 'LEAD_SCORING_WEIGHTS', 'LEAD_SCORE_THRESHOLD',
    
    # Pricing
    'BASE_TOKEN_PACKAGES', 'DYNAMIC_PRICING_ENABLED',
    
    # Security
    'FRAUD_DETECTION_ENABLED', 'RATE_LIMIT_REQUESTS',
    
    # Feature flags
    'FEATURE_GEO_TARGETING', 'FEATURE_AGENTIC_MARKETING', 'FEATURE_DYNAMIC_PRICING'
]
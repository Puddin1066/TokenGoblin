"""
Configuration management for Automated Telegram Marketing System
"""
import os
from typing import List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class TelegramConfig(BaseSettings):
    """Telegram API configuration"""
    api_id: int = Field(..., env='TELEGRAM_API_ID')
    api_hash: str = Field(..., env='TELEGRAM_API_HASH')
    bot_token: str = Field(..., env='TELEGRAM_BOT_TOKEN')
    phone_number: str = Field(..., env='TELEGRAM_PHONE_NUMBER')
    bot_username: str = Field(..., env='BOT_USERNAME')
    webhook_host: str = Field(..., env='WEBHOOK_HOST')
    webhook_path: str = Field('/webhook', env='WEBHOOK_PATH')
    webhook_secret: str = Field(..., env='WEBHOOK_SECRET_TOKEN')

class AIConfig(BaseSettings):
    """AI service configuration"""
    openai_api_key: str = Field(..., env='OPENAI_API_KEY')
    openai_model: str = Field('gpt-4', env='OPENAI_MODEL')
    openai_max_tokens: int = Field(1000, env='OPENAI_MAX_TOKENS')
    anthropic_api_key: Optional[str] = Field(None, env='ANTHROPIC_API_KEY')
    use_local_ai: bool = Field(False, env='USE_LOCAL_AI')
    local_ai_model_path: str = Field('./models/sales_agent', env='LOCAL_AI_MODEL_PATH')

class OpenRouterConfig(BaseSettings):
    """OpenRouter API configuration"""
    api_key: str = Field(..., env='OPENROUTER_API_KEY')
    api_url: str = Field('https://openrouter.ai/api/v1', env='OPENROUTER_API_URL')
    profit_margin: float = Field(300.0, env='OPENROUTER_PROFIT_MARGIN')

class DatabaseConfig(BaseSettings):
    """Database configuration"""
    url: str = Field(..., env='DATABASE_URL')
    sqlite_url: str = Field('sqlite:///./data/marketing.db', env='SQLITE_DATABASE_URL')
    type: str = Field('postgresql', env='DATABASE_TYPE')
    pool_size: int = Field(20, env='DATABASE_POOL_SIZE')

class RedisConfig(BaseSettings):
    """Redis configuration"""
    host: str = Field('localhost', env='REDIS_HOST')
    port: int = Field(6379, env='REDIS_PORT')
    password: Optional[str] = Field(None, env='REDIS_PASSWORD')
    db: int = Field(0, env='REDIS_DB')

class PaymentConfig(BaseSettings):
    """Payment processing configuration"""
    stripe_secret_key: str = Field(..., env='STRIPE_SECRET_KEY')
    stripe_publishable_key: str = Field(..., env='STRIPE_PUBLISHABLE_KEY')
    stripe_webhook_secret: str = Field(..., env='STRIPE_WEBHOOK_SECRET')
    crypto_wallet_address: Optional[str] = Field(None, env='CRYPTO_WALLET_ADDRESS')
    crypto_network: str = Field('ethereum', env='CRYPTO_NETWORK')

class MarketingConfig(BaseSettings):
    """Marketing automation configuration"""
    daily_prospect_limit: int = Field(100, env='DAILY_PROSPECT_LIMIT')
    conversation_limit: int = Field(25, env='CONVERSATION_LIMIT')
    messages_per_hour: int = Field(10, env='MESSAGES_PER_HOUR')
    min_qualification_score: int = Field(60, env='MIN_QUALIFICATION_SCORE')
    target_groups: List[str] = Field(
        default_factory=lambda: [
            'AI_developers', 'MachineLearning', 'OpenAI_community',
            'ChatGPT_developers', 'AIStartups', 'StartupFounders'
        ],
        env='TARGET_TELEGRAM_GROUPS'
    )

class PricingConfig(BaseSettings):
    """Dynamic pricing configuration"""
    base_price_gpt4: float = Field(8.00, env='BASE_PRICE_GPT4')
    base_price_claude: float = Field(6.00, env='BASE_PRICE_CLAUDE')
    base_price_gpt35: float = Field(2.00, env='BASE_PRICE_GPT35')
    dynamic_pricing_enabled: bool = Field(True, env='DYNAMIC_PRICING_ENABLED')

class SalesAgentConfig(BaseSettings):
    """Sales agent configuration"""
    name: str = Field('Alex', env='SALES_AGENT_NAME')
    role: str = Field('AI Solutions Consultant', env='SALES_AGENT_ROLE')
    personality: str = Field('professional', env='SALES_AGENT_PERSONALITY')
    conversation_timeout: int = Field(3600, env='CONVERSATION_TIMEOUT')

class SystemConfig(BaseSettings):
    """System configuration"""
    app_name: str = Field('Telegram Marketing Automation', env='APP_NAME')
    app_version: str = Field('1.0.0', env='APP_VERSION')
    debug: bool = Field(False, env='DEBUG')
    log_level: str = Field('INFO', env='LOG_LEVEL')
    host: str = Field('0.0.0.0', env='HOST')
    port: int = Field(8000, env='PORT')
    workers: int = Field(4, env='WORKERS')
    data_dir: str = Field('./data', env='DATA_DIR')
    logs_dir: str = Field('./logs', env='LOGS_DIR')
    temp_dir: str = Field('./temp', env='TEMP_DIR')

class MonitoringConfig(BaseSettings):
    """Monitoring and analytics configuration"""
    daily_revenue_target: float = Field(100.00, env='DAILY_REVENUE_TARGET')
    monthly_revenue_target: float = Field(3000.00, env='MONTHLY_REVENUE_TARGET')
    enable_metrics: bool = Field(True, env='ENABLE_METRICS')
    metrics_port: int = Field(9090, env='METRICS_PORT')

class SecurityConfig(BaseSettings):
    """Security configuration"""
    jwt_secret_key: str = Field(..., env='JWT_SECRET_KEY')
    jwt_algorithm: str = Field('HS256', env='JWT_ALGORITHM')
    jwt_expiration: int = Field(86400, env='JWT_EXPIRATION')
    rate_limit_requests: int = Field(100, env='RATE_LIMIT_REQUESTS')
    rate_limit_window: int = Field(3600, env='RATE_LIMIT_WINDOW')

class NotificationConfig(BaseSettings):
    """Notification configuration"""
    admin_telegram_ids: List[int] = Field(
        default_factory=list,
        env='ADMIN_TELEGRAM_IDS'
    )
    notification_channel: Optional[str] = Field(None, env='NOTIFICATION_CHANNEL')
    smtp_host: str = Field('smtp.gmail.com', env='SMTP_HOST')
    smtp_port: int = Field(587, env='SMTP_PORT')
    smtp_username: Optional[str] = Field(None, env='SMTP_USERNAME')
    smtp_password: Optional[str] = Field(None, env='SMTP_PASSWORD')

class FeatureFlags(BaseSettings):
    """Feature flags configuration"""
    enable_telegram_crawler: bool = Field(True, env='ENABLE_TELEGRAM_CRAWLER')
    enable_ai_sales_agent: bool = Field(True, env='ENABLE_AI_SALES_AGENT')
    enable_dynamic_pricing: bool = Field(True, env='ENABLE_DYNAMIC_PRICING')
    enable_payment_processing: bool = Field(True, env='ENABLE_PAYMENT_PROCESSING')
    enable_analytics: bool = Field(True, env='ENABLE_ANALYTICS')
    enable_automation: bool = Field(True, env='ENABLE_AUTOMATION')

class DevelopmentConfig(BaseSettings):
    """Development configuration"""
    test_mode: bool = Field(False, env='TEST_MODE')
    mock_payments: bool = Field(False, env='MOCK_PAYMENTS')
    simulate_conversations: bool = Field(False, env='SIMULATE_CONVERSATIONS')
    async_workers: int = Field(10, env='ASYNC_WORKERS')
    connection_timeout: int = Field(30, env='CONNECTION_TIMEOUT')

class Config:
    """Main configuration class"""
    
    def __init__(self):
        self.telegram = TelegramConfig()
        self.ai = AIConfig()
        self.openrouter = OpenRouterConfig()
        self.database = DatabaseConfig()
        self.redis = RedisConfig()
        self.payment = PaymentConfig()
        self.marketing = MarketingConfig()
        self.pricing = PricingConfig()
        self.sales_agent = SalesAgentConfig()
        self.system = SystemConfig()
        self.monitoring = MonitoringConfig()
        self.security = SecurityConfig()
        self.notification = NotificationConfig()
        self.features = FeatureFlags()
        self.development = DevelopmentConfig()
    
    def create_directories(self):
        """Create necessary directories"""
        directories = [
            self.system.data_dir,
            self.system.logs_dir,
            self.system.temp_dir,
            f"{self.system.data_dir}/sessions",
            f"{self.system.data_dir}/models",
            f"{self.system.data_dir}/exports"
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    @property
    def database_url(self) -> str:
        """Get appropriate database URL"""
        if self.database.type == 'sqlite':
            return self.database.sqlite_url
        return self.database.url
    
    @property
    def redis_url(self) -> str:
        """Get Redis URL"""
        if self.redis.password:
            return f"redis://:{self.redis.password}@{self.redis.host}:{self.redis.port}/{self.redis.db}"
        return f"redis://{self.redis.host}:{self.redis.port}/{self.redis.db}"
    
    @property
    def webhook_url(self) -> str:
        """Get webhook URL"""
        return f"{self.telegram.webhook_host}{self.telegram.webhook_path}"
    
    def validate_required_keys(self) -> List[str]:
        """Validate that all required API keys are present"""
        missing_keys = []
        
        # Check required API keys
        if not self.telegram.api_id:
            missing_keys.append('TELEGRAM_API_ID')
        if not self.telegram.api_hash:
            missing_keys.append('TELEGRAM_API_HASH')
        if not self.telegram.bot_token:
            missing_keys.append('TELEGRAM_BOT_TOKEN')
        if not self.ai.openai_api_key:
            missing_keys.append('OPENAI_API_KEY')
        if not self.openrouter.api_key:
            missing_keys.append('OPENROUTER_API_KEY')
        if not self.payment.stripe_secret_key:
            missing_keys.append('STRIPE_SECRET_KEY')
        if not self.security.jwt_secret_key:
            missing_keys.append('JWT_SECRET_KEY')
        
        return missing_keys

# Global configuration instance
config = Config()

# Legacy compatibility for existing code
TOKEN = config.telegram.bot_token
WEBHOOK_URL = config.webhook_url
WEBHOOK_SECRET_TOKEN = config.telegram.webhook_secret
ADMIN_ID_LIST = config.notification.admin_telegram_ids
WEBAPP_HOST = config.system.host
WEBAPP_PORT = config.system.port
REDIS_HOST = config.redis.host
REDIS_PASSWORD = config.redis.password

# Ensure directories exist
config.create_directories()

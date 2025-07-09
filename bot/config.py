import os
from typing import List, Optional
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

@dataclass
class Config:
    """Configuration class for Claude Token Resale Bot"""
    
    # Bot Configuration
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
    WEBHOOK_SECRET_TOKEN: str = os.getenv("WEBHOOK_SECRET_TOKEN", "")
    WEBHOOK_PATH: str = os.getenv("WEBHOOK_PATH", "/webhook")
    WEBAPP_HOST: str = os.getenv("WEBAPP_HOST", "0.0.0.0")
    WEBAPP_PORT: int = int(os.getenv("WEBAPP_PORT", "8443"))
    ADMIN_ID_LIST: List[int] = [int(x) for x in os.getenv("ADMIN_ID_LIST", "").split(",") if x]
    SUPPORT_LINK: str = os.getenv("SUPPORT_LINK", "https://t.me/support")
    
    # OpenRouter Integration
    OPENROUTER_KEY: str = os.getenv("OPENROUTER_KEY", "")
    OPENROUTER_URL: str = os.getenv("OPENROUTER_URL", "https://openrouter.ai/api/v1")
    
    # Payment Processing
    PAYMENTS_PROVIDER_TOKEN: str = os.getenv("PAYMENTS_PROVIDER_TOKEN", "")
    CURRENCY: str = os.getenv("CURRENCY", "USD")
    
    # Crypto Wallet Addresses
    BTC_WALLET: str = os.getenv("BTC_WALLET", "")
    LTC_WALLET: str = os.getenv("LTC_WALLET", "")
    TON_WALLET: str = os.getenv("TON_WALLET", "")
    USDT_TRC20_WALLET: str = os.getenv("USDT_TRC20_WALLET", "")
    
    # Database Configuration
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///claude_tokens.db")
    DB_ENCRYPTION: bool = os.getenv("DB_ENCRYPTION", "false").lower() == "true"
    DB_PASS: str = os.getenv("DB_PASS", "")
    
    # CRM Integration
    WEBHOOK_URL: str = os.getenv("WEBHOOK_URL", "")
    WEBHOOK_SECRET: str = os.getenv("WEBHOOK_SECRET", "")
    
    # GitHub Integration
    GITHUB_PAT: str = os.getenv("GITHUB_PAT", "")
    GITHUB_USERNAME: str = os.getenv("GITHUB_USERNAME", "")
    
    # Email Configuration
    SMTP_HOST: str = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER: str = os.getenv("SMTP_USER", "")
    SMTP_PASS: str = os.getenv("SMTP_PASS", "")
    EMAIL_FROM: str = os.getenv("EMAIL_FROM", "ClaudeToken Team <noreply@domain.com>")
    
    # Localization
    BOT_LANGUAGE: str = os.getenv("BOT_LANGUAGE", "en")
    
    # Redis Configuration
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_PASSWORD: str = os.getenv("REDIS_PASSWORD", "")
    REDIS_DB: int = int(os.getenv("REDIS_DB", "0"))
    
    # Environment Settings
    RUNTIME_ENVIRONMENT: str = os.getenv("RUNTIME_ENVIRONMENT", "dev")
    NGROK_TOKEN: str = os.getenv("NGROK_TOKEN", "")
    
    # Business Logic
    TOKEN_PRICE_PER_1K: float = float(os.getenv("TOKEN_PRICE_PER_1K", "0.50"))
    DEFAULT_TOKEN_PACKAGE: int = int(os.getenv("DEFAULT_TOKEN_PACKAGE", "10000"))
    MAX_TOKEN_PACKAGE: int = int(os.getenv("MAX_TOKEN_PACKAGE", "100000"))
    
    # Rate Limiting
    MAX_REQUESTS_PER_MINUTE: int = int(os.getenv("MAX_REQUESTS_PER_MINUTE", "10"))
    MAX_REQUESTS_PER_HOUR: int = int(os.getenv("MAX_REQUESTS_PER_HOUR", "100"))
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = os.getenv("LOG_FILE", "claude_bot.log")
    
    # Feature Flags
    ENABLE_CRYPTO_PAYMENTS: bool = os.getenv("ENABLE_CRYPTO_PAYMENTS", "true").lower() == "true"
    ENABLE_TELEGRAM_PAYMENTS: bool = os.getenv("ENABLE_TELEGRAM_PAYMENTS", "true").lower() == "true"
    ENABLE_GITHUB_UPLOAD: bool = os.getenv("ENABLE_GITHUB_UPLOAD", "false").lower() == "true"
    ENABLE_EMAIL_NOTIFICATIONS: bool = os.getenv("ENABLE_EMAIL_NOTIFICATIONS", "false").lower() == "true"
    ENABLE_CRM_SYNC: bool = os.getenv("ENABLE_CRM_SYNC", "true").lower() == "true"
    
    # Analytics
    ANALYTICS_ENABLED: bool = os.getenv("ANALYTICS_ENABLED", "true").lower() == "true"
    ANALYTICS_WEBHOOK: str = os.getenv("ANALYTICS_WEBHOOK", "")
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "")
    JWT_SECRET: str = os.getenv("JWT_SECRET", "")
    RATE_LIMIT_STORAGE: str = os.getenv("RATE_LIMIT_STORAGE", "redis")
    
    # Monitoring
    HEALTH_CHECK_ENDPOINT: str = os.getenv("HEALTH_CHECK_ENDPOINT", "/health")
    METRICS_ENDPOINT: str = os.getenv("METRICS_ENDPOINT", "/metrics")
    ENABLE_PROMETHEUS: bool = os.getenv("ENABLE_PROMETHEUS", "false").lower() == "true"
    
    def __post_init__(self):
        """Validate configuration after initialization"""
        if not self.BOT_TOKEN:
            raise ValueError("BOT_TOKEN is required")
        if not self.OPENROUTER_KEY:
            raise ValueError("OPENROUTER_KEY is required")
        if not self.WEBHOOK_SECRET_TOKEN:
            raise ValueError("WEBHOOK_SECRET_TOKEN is required")
    
    @property
    def is_development(self) -> bool:
        """Check if running in development mode"""
        return self.RUNTIME_ENVIRONMENT.lower() == "dev"
    
    @property
    def is_production(self) -> bool:
        """Check if running in production mode"""
        return self.RUNTIME_ENVIRONMENT.lower() == "prod"
    
    def get_database_url(self) -> str:
        """Get database URL with encryption if enabled"""
        if self.DB_ENCRYPTION and self.DB_PASS:
            return f"{self.DATABASE_URL}?passphrase={self.DB_PASS}"
        return self.DATABASE_URL


# Global configuration instance
config = Config()
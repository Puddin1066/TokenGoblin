from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy import (
    Column, Integer, String, Float, DateTime, Boolean, 
    Text, ForeignKey, Index, UniqueConstraint, CheckConstraint
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, Session
from sqlalchemy.sql import func
from enum import Enum

Base = declarative_base()


class PaymentStatus(Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


class PaymentMethod(Enum):
    TELEGRAM = "telegram"
    CRYPTO_BTC = "crypto_btc"
    CRYPTO_LTC = "crypto_ltc"
    CRYPTO_TON = "crypto_ton"
    CRYPTO_USDT = "crypto_usdt"


class TokenUsageType(Enum):
    PURCHASE = "purchase"
    DEDUCTION = "deduction"
    REFUND = "refund"
    ADMIN_CREDIT = "admin_credit"


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(Integer, unique=True, index=True, nullable=False)
    username = Column(String(100), index=True)
    first_name = Column(String(100))
    last_name = Column(String(100))
    email = Column(String(255), index=True)
    language_code = Column(String(10), default="en")
    
    # Campaign tracking
    campaign_id = Column(String(100), index=True)
    abstract_snippet = Column(Text)
    
    # Token balance
    token_balance = Column(Integer, default=0)
    total_tokens_purchased = Column(Integer, default=0)
    total_tokens_used = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    last_activity = Column(DateTime)
    
    # Relationships
    payments = relationship("Payment", back_populates="user")
    token_usage = relationship("TokenUsage", back_populates="user")
    
    def __repr__(self):
        return f"<User(telegram_id={self.telegram_id}, username={self.username})>"


class Campaign(Base):
    __tablename__ = "campaigns"
    
    id = Column(Integer, primary_key=True, index=True)
    campaign_id = Column(String(100), unique=True, index=True, nullable=False)
    name = Column(String(200))
    description = Column(Text)
    target_language = Column(String(10), default="en")
    
    # Campaign stats
    total_clicks = Column(Integer, default=0)
    total_registrations = Column(Integer, default=0)
    total_purchases = Column(Integer, default=0)
    total_revenue = Column(Float, default=0.0)
    
    # Campaign settings
    is_active = Column(Boolean, default=True)
    token_price_override = Column(Float)  # Override global token price
    max_tokens_per_user = Column(Integer)
    
    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    
    def __repr__(self):
        return f"<Campaign(campaign_id={self.campaign_id}, name={self.name})>"


class Payment(Base):
    __tablename__ = "payments"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Payment details
    payment_method = Column(String(50), nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String(10), nullable=False)
    tokens_purchased = Column(Integer, nullable=False)
    
    # Payment status
    status = Column(String(20), default=PaymentStatus.PENDING.value)
    
    # External payment IDs
    telegram_payment_id = Column(String(255))
    crypto_tx_hash = Column(String(255))
    provider_payment_id = Column(String(255))
    
    # Metadata
    payment_data = Column(Text)  # JSON data for additional payment info
    
    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    completed_at = Column(DateTime)
    
    # Relationships
    user = relationship("User", back_populates="payments")
    
    __table_args__ = (
        Index("ix_payments_status", "status"),
        Index("ix_payments_created_at", "created_at"),
        CheckConstraint("amount > 0", name="positive_amount"),
        CheckConstraint("tokens_purchased > 0", name="positive_tokens"),
    )
    
    def __repr__(self):
        return f"<Payment(id={self.id}, user_id={self.user_id}, amount={self.amount}, status={self.status})>"


class TokenUsage(Base):
    __tablename__ = "token_usage"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Usage details
    tokens_used = Column(Integer, nullable=False)
    usage_type = Column(String(50), nullable=False)
    description = Column(Text)
    
    # OpenRouter integration
    openrouter_request_id = Column(String(255))
    model_used = Column(String(100))
    prompt_tokens = Column(Integer)
    completion_tokens = Column(Integer)
    
    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    # Relationships
    user = relationship("User", back_populates="token_usage")
    
    __table_args__ = (
        Index("ix_token_usage_user_id", "user_id"),
        Index("ix_token_usage_created_at", "created_at"),
        Index("ix_token_usage_type", "usage_type"),
    )
    
    def __repr__(self):
        return f"<TokenUsage(id={self.id}, user_id={self.user_id}, tokens_used={self.tokens_used})>"


class AdminLog(Base):
    __tablename__ = "admin_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    admin_id = Column(Integer, nullable=False)
    action = Column(String(100), nullable=False)
    target_user_id = Column(Integer, ForeignKey("users.id"))
    details = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    
    __table_args__ = (
        Index("ix_admin_logs_admin_id", "admin_id"),
        Index("ix_admin_logs_created_at", "created_at"),
    )
    
    def __repr__(self):
        return f"<AdminLog(id={self.id}, admin_id={self.admin_id}, action={self.action})>"


class WebhookEvent(Base):
    __tablename__ = "webhook_events"
    
    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String(100), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    campaign_id = Column(String(100))
    
    # Event data
    event_data = Column(Text)  # JSON data
    
    # Processing status
    processed = Column(Boolean, default=False)
    retry_count = Column(Integer, default=0)
    last_error = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    processed_at = Column(DateTime)
    
    __table_args__ = (
        Index("ix_webhook_events_type", "event_type"),
        Index("ix_webhook_events_processed", "processed"),
        Index("ix_webhook_events_created_at", "created_at"),
    )
    
    def __repr__(self):
        return f"<WebhookEvent(id={self.id}, event_type={self.event_type}, processed={self.processed})>"


# Database helper functions
class DatabaseHelper:
    @staticmethod
    def get_user_by_telegram_id(session: Session, telegram_id: int) -> Optional[User]:
        """Get user by Telegram ID"""
        return session.query(User).filter(User.telegram_id == telegram_id).first()
    
    @staticmethod
    def create_user(session: Session, telegram_id: int, username: Optional[str] = None, 
                   first_name: Optional[str] = None, last_name: Optional[str] = None, 
                   email: Optional[str] = None, campaign_id: Optional[str] = None, 
                   abstract_snippet: Optional[str] = None) -> User:
        """Create a new user"""
        user = User(
            telegram_id=telegram_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email,
            campaign_id=campaign_id,
            abstract_snippet=abstract_snippet
        )
        session.add(user)
        session.commit()
        return user
    
    @staticmethod
    def update_user_balance(session: Session, user_id: int, tokens: int) -> bool:
        """Update user token balance"""
        user = session.query(User).filter(User.id == user_id).first()
        if user:
            user.token_balance += tokens
            if tokens > 0:
                user.total_tokens_purchased += tokens
            else:
                user.total_tokens_used += abs(tokens)
            session.commit()
            return True
        return False
    
    @staticmethod
    def create_payment(session: Session, user_id: int, amount: float, 
                      currency: str, tokens_purchased: int, 
                      payment_method: str) -> Payment:
        """Create a new payment record"""
        payment = Payment(
            user_id=user_id,
            amount=amount,
            currency=currency,
            tokens_purchased=tokens_purchased,
            payment_method=payment_method
        )
        session.add(payment)
        session.commit()
        return payment
    
    @staticmethod
    def log_token_usage(session: Session, user_id: int, tokens_used: int, 
                       usage_type: str, description: Optional[str] = None) -> TokenUsage:
        """Log token usage"""
        usage = TokenUsage(
            user_id=user_id,
            tokens_used=tokens_used,
            usage_type=usage_type,
            description=description
        )
        session.add(usage)
        session.commit()
        return usage
    
    @staticmethod
    def get_campaign_stats(session: Session, campaign_id: str) -> dict:
        """Get campaign statistics"""
        campaign = session.query(Campaign).filter(Campaign.campaign_id == campaign_id).first()
        if not campaign:
            return {}
        
        users_count = session.query(User).filter(User.campaign_id == campaign_id).count()
        payments_sum = session.query(func.sum(Payment.amount)).filter(
            Payment.user_id.in_(
                session.query(User.id).filter(User.campaign_id == campaign_id)
            ),
            Payment.status == PaymentStatus.COMPLETED.value
        ).scalar() or 0
        
        return {
            "campaign_id": campaign_id,
            "total_users": users_count,
            "total_revenue": float(payments_sum),
            "total_clicks": campaign.total_clicks,
            "conversion_rate": (campaign.total_purchases / campaign.total_clicks * 100) if campaign.total_clicks > 0 else 0
        }
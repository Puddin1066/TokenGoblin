from datetime import datetime, timedelta
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, DateTime, CheckConstraint
from sqlalchemy.orm import relationship, backref

from models.base import Base
import config


class AITokenPackage(Base):
    __tablename__ = 'ai_token_packages'

    id = Column(Integer, primary_key=True, unique=True)
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="CASCADE"), nullable=False)
    category = relationship("Category", backref=backref("token_categories", cascade="all"), passive_deletes="all",
                            lazy="joined")
    subcategory_id = Column(Integer, ForeignKey("subcategories.id", ondelete="CASCADE"), nullable=False)
    subcategory = relationship("Subcategory", backref=backref("token_subcategories", cascade="all"), passive_deletes="all",
                               lazy="joined")
    
    # Token details
    token_count = Column(Integer, nullable=False)  # Number of tokens in package
    model_access = Column(String, nullable=False)  # Which AI models this package provides access to
    cost_price = Column(Float, nullable=False)  # What we pay OpenRouter
    sell_price = Column(Float, nullable=False)  # What we charge (cost + markup)
    
    # Package status
    is_available = Column(Boolean, nullable=False, default=True)
    is_featured = Column(Boolean, nullable=False, default=False)
    description = Column(String, nullable=False)
    
    # Expiry and limits
    expiry_days = Column(Integer, nullable=False, default=config.DEFAULT_TOKEN_EXPIRY_DAYS)
    daily_limit = Column(Integer, nullable=True)  # Optional daily usage limit
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        CheckConstraint('token_count > 0', name='check_token_count_positive'),
        CheckConstraint('cost_price > 0', name='check_cost_price_positive'),
        CheckConstraint('sell_price > cost_price', name='check_profit_margin'),
    )


class AITokenAllocation(Base):
    __tablename__ = 'ai_token_allocations'

    id = Column(Integer, primary_key=True, unique=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    user = relationship("User", backref="token_allocations")
    package_id = Column(Integer, ForeignKey("ai_token_packages.id", ondelete="CASCADE"), nullable=False)
    package = relationship("AITokenPackage", backref="allocations")
    
    # Access details
    api_key = Column(String, nullable=False, unique=True)
    remaining_tokens = Column(Integer, nullable=False)
    total_tokens = Column(Integer, nullable=False)
    
    # Status and expiry
    is_active = Column(Boolean, nullable=False, default=True)
    expires_at = Column(DateTime, nullable=False)
    last_used = Column(DateTime, nullable=True)
    
    # Usage tracking
    total_requests = Column(Integer, nullable=False, default=0)
    tokens_used_today = Column(Integer, nullable=False, default=0)
    daily_reset_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class AITokenPackageDTO(BaseModel):
    id: int | None = None
    category_id: int | None = None
    subcategory_id: int | None = None
    token_count: int | None = None
    model_access: str | None = None
    cost_price: float | None = None
    sell_price: float | None = None
    is_available: bool | None = None
    is_featured: bool | None = None
    description: str | None = None
    expiry_days: int | None = None
    daily_limit: int | None = None


class AITokenAllocationDTO(BaseModel):
    id: int | None = None
    user_id: int | None = None
    package_id: int | None = None
    api_key: str | None = None
    remaining_tokens: int | None = None
    total_tokens: int | None = None
    is_active: bool | None = None
    expires_at: datetime | None = None
    last_used: datetime | None = None
    total_requests: int | None = None
    tokens_used_today: int | None = None
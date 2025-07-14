from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text
from sqlalchemy.sql import func
from models.base import Base


class TokenInventory(Base):
    __tablename__ = 'token_inventory'
    
    id = Column(Integer, primary_key=True)
    model_id = Column(String(100), nullable=False)  # e.g., 'anthropic/claude-3-sonnet'
    model_name = Column(String(200), nullable=False)  # e.g., 'Claude 3 Sonnet'
    tokens_available = Column(Integer, default=0)
    tokens_reserved = Column(Integer, default=0)
    unit_price_usd = Column(Float, nullable=False)
    cost_per_token = Column(Float, nullable=False)
    markup_percentage = Column(Float, default=0.2)  # 20% default markup
    is_active = Column(Boolean, default=True)
    last_restock_date = Column(DateTime, default=func.now())
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<TokenInventory(model_id='{self.model_id}', tokens_available={self.tokens_available})>"


class TokenPurchase(Base):
    __tablename__ = 'token_purchases'
    
    id = Column(Integer, primary_key=True)
    model_id = Column(String(100), nullable=False)
    tokens_purchased = Column(Integer, nullable=False)
    cost_usd = Column(Float, nullable=False)
    purchase_timestamp = Column(DateTime, default=func.now())
    openrouter_request_id = Column(String(200))
    status = Column(String(50), default='pending')  # pending, completed, failed
    created_at = Column(DateTime, default=func.now())
    
    def __repr__(self):
        return f"<TokenPurchase(model_id='{self.model_id}', tokens={self.tokens_purchased}, cost=${self.cost_usd})>"


class TokenUsage(Base):
    __tablename__ = 'token_usage'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    model_id = Column(String(100), nullable=False)
    tokens_used = Column(Integer, nullable=False)
    usage_type = Column(String(50), nullable=False)  # 'purchase', 'consumption'
    cost_usd = Column(Float, nullable=False)
    openrouter_request_id = Column(String(200))
    created_at = Column(DateTime, default=func.now())
    
    def __repr__(self):
        return f"<TokenUsage(user_id={self.user_id}, tokens={self.tokens_used}, cost=${self.cost_usd})>"


class PricingHistory(Base):
    __tablename__ = 'pricing_history'
    
    id = Column(Integer, primary_key=True)
    model_id = Column(String(100), nullable=False)
    price_usd = Column(Float, nullable=False)
    source = Column(String(50), nullable=False)  # 'openrouter', 'market', 'manual'
    reason = Column(Text)  # Reason for price change
    created_at = Column(DateTime, default=func.now())
    
    def __repr__(self):
        return f"<PricingHistory(model_id='{self.model_id}', price=${self.price_usd}, source='{self.source}')>"
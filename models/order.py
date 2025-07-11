"""
Order model for managing OpenRouter token sales
"""
from datetime import datetime
from typing import Dict, Any, Optional
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, JSON, Text, ForeignKey, func
from sqlalchemy.orm import relationship
from pydantic import BaseModel

from models.base import Base


class TokenPackage(Base):
    """Model for different token packages"""
    __tablename__ = 'token_packages'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    
    # Token allocation
    gpt4_tokens = Column(Integer, default=0)
    gpt35_tokens = Column(Integer, default=0)
    claude_tokens = Column(Integer, default=0)
    other_tokens = Column(Integer, default=0)
    
    # Pricing
    base_price = Column(Float, nullable=False)
    cost_price = Column(Float, nullable=False)  # Our cost from OpenRouter
    
    # Features
    features = Column(JSON, default=dict)
    rate_limit = Column(Integer, default=1000)  # requests per minute
    expiry_days = Column(Integer, default=30)
    
    # Status
    active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<TokenPackage(id={self.id}, name={self.name}, base_price={self.base_price})>"


class Order(Base):
    """Model for managing orders"""
    __tablename__ = 'orders'

    id = Column(Integer, primary_key=True)
    prospect_id = Column(Integer, ForeignKey('prospects.id'), nullable=False)
    package_id = Column(Integer, ForeignKey('token_packages.id'), nullable=False)
    
    # Order details
    order_number = Column(String(100), unique=True, nullable=False)
    status = Column(String(50), default='pending')  # pending, paid, fulfilled, cancelled, refunded
    
    # Pricing
    original_price = Column(Float, nullable=False)
    final_price = Column(Float, nullable=False)
    discount_amount = Column(Float, default=0.0)
    tax_amount = Column(Float, default=0.0)
    
    # Payment
    payment_method = Column(String(50), nullable=True)  # stripe, crypto, etc.
    payment_id = Column(String(255), nullable=True)
    payment_status = Column(String(50), default='pending')
    
    # Fulfillment
    openrouter_api_key = Column(String(255), nullable=True)
    api_key_created = Column(Boolean, default=False)
    fulfillment_status = Column(String(50), default='pending')
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    paid_at = Column(DateTime, nullable=True)
    fulfilled_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)
    
    # Metadata
    metadata = Column(JSON, default=dict)
    
    # Relationships
    prospect = relationship("Prospect", back_populates="orders")
    package = relationship("TokenPackage")
    
    def __repr__(self):
        return f"<Order(id={self.id}, order_number={self.order_number}, status={self.status})>"


class OrderDTO(BaseModel):
    """Pydantic model for order data transfer"""
    id: Optional[int] = None
    prospect_id: int
    package_id: int
    order_number: str
    status: str = 'pending'
    original_price: float
    final_price: float
    discount_amount: float = 0.0
    tax_amount: float = 0.0
    payment_method: Optional[str] = None
    payment_id: Optional[str] = None
    payment_status: str = 'pending'
    openrouter_api_key: Optional[str] = None
    api_key_created: bool = False
    fulfillment_status: str = 'pending'
    created_at: Optional[datetime] = None
    paid_at: Optional[datetime] = None
    fulfilled_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    metadata: Dict[str, Any] = {}
    
    class Config:
        from_attributes = True


class TokenPackageDTO(BaseModel):
    """Pydantic model for token package data transfer"""
    id: Optional[int] = None
    name: str
    description: Optional[str] = None
    gpt4_tokens: int = 0
    gpt35_tokens: int = 0
    claude_tokens: int = 0
    other_tokens: int = 0
    base_price: float
    cost_price: float
    features: Dict[str, Any] = {}
    rate_limit: int = 1000
    expiry_days: int = 30
    active: bool = True
    
    class Config:
        from_attributes = True
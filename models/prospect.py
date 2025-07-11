"""
Prospect model for lead management
"""
from datetime import datetime
from typing import Dict, Any, Optional
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, JSON, Text, func
from sqlalchemy.orm import relationship
from pydantic import BaseModel

from models.base import Base


class Prospect(Base):
    """Model for managing marketing prospects"""
    __tablename__ = 'prospects'

    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, nullable=False)
    username = Column(String(255), nullable=True)
    first_name = Column(String(255), nullable=True)
    last_name = Column(String(255), nullable=True)
    bio = Column(Text, nullable=True)
    
    # Qualification data
    qualification_score = Column(Float, default=0.0)
    qualification_data = Column(JSON, default=dict)
    
    # Engagement tracking
    status = Column(String(50), default='new')  # new, contacted, qualified, converted, lost
    last_seen = Column(DateTime, nullable=True)
    first_contact_date = Column(DateTime, nullable=True)
    last_contact_date = Column(DateTime, nullable=True)
    
    # Source information
    source_group = Column(String(255), nullable=True)
    discovery_method = Column(String(100), nullable=True)
    
    # Segmentation
    segment = Column(String(50), nullable=True)  # hot, warm, cold, low_priority
    customer_type = Column(String(100), nullable=True)  # startup_founder, developer, etc.
    
    # Conversion tracking
    converted = Column(Boolean, default=False)
    conversion_date = Column(DateTime, nullable=True)
    lifetime_value = Column(Float, default=0.0)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    conversations = relationship("Conversation", back_populates="prospect")
    orders = relationship("Order", back_populates="prospect")
    
    def __repr__(self):
        return f"<Prospect(id={self.id}, telegram_id={self.telegram_id}, status={self.status})>"


class ProspectDTO(BaseModel):
    """Pydantic model for prospect data transfer"""
    id: Optional[int] = None
    telegram_id: int
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    bio: Optional[str] = None
    qualification_score: float = 0.0
    qualification_data: Dict[str, Any] = {}
    status: str = 'new'
    last_seen: Optional[datetime] = None
    first_contact_date: Optional[datetime] = None
    last_contact_date: Optional[datetime] = None
    source_group: Optional[str] = None
    discovery_method: Optional[str] = None
    segment: Optional[str] = None
    customer_type: Optional[str] = None
    converted: bool = False
    conversion_date: Optional[datetime] = None
    lifetime_value: float = 0.0
    
    class Config:
        from_attributes = True
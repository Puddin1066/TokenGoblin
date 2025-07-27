from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, JSON
from sqlalchemy.sql import func
from models.base import Base


class Lead(Base):
    __tablename__ = 'leads'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    email = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    
    # Lead scoring
    qualification_score = Column(Float, default=0.0)
    grade = Column(String(10), default='D')  # A, B, C, D
    source = Column(String(100), nullable=True)  # content_download, webinar, demo_request, etc.
    
    # Behavioral data
    engagement_activities = Column(JSON, default=list)
    intent_signals = Column(JSON, default=list)
    budget_indicator = Column(Float, default=0.0)
    authority_level = Column(String(50), default='user')  # user, manager, decision_maker
    
    # Geographic and demographic
    region = Column(String(10), nullable=True)
    timezone = Column(String(50), nullable=True)
    language = Column(String(10), default='en')
    
    # Campaign tracking
    campaign_id = Column(String(100), nullable=True)
    first_touch_date = Column(DateTime, default=func.now())
    last_touch_date = Column(DateTime, default=func.now())
    touch_count = Column(Integer, default=0)
    
    # Status and lifecycle
    status = Column(String(50), default='new')  # new, qualified, nurtured, converted, lost
    lifecycle_stage = Column(String(50), default='awareness')  # awareness, interest, consideration, conversion
    
    # Conversion tracking
    converted_at = Column(DateTime, nullable=True)
    conversion_value = Column(Float, default=0.0)
    conversion_source = Column(String(100), nullable=True)
    
    # Notes and metadata
    notes = Column(Text, nullable=True)
    metadata = Column(JSON, default=dict)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<Lead(id={self.id}, user_id={self.user_id}, grade={self.grade}, status={self.status})>"
    
    def to_dict(self):
        """Convert lead to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'email': self.email,
            'phone': self.phone,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'qualification_score': self.qualification_score,
            'grade': self.grade,
            'source': self.source,
            'engagement_activities': self.engagement_activities,
            'intent_signals': self.intent_signals,
            'budget_indicator': self.budget_indicator,
            'authority_level': self.authority_level,
            'region': self.region,
            'timezone': self.timezone,
            'language': self.language,
            'campaign_id': self.campaign_id,
            'first_touch_date': self.first_touch_date.isoformat() if self.first_touch_date else None,
            'last_touch_date': self.last_touch_date.isoformat() if self.last_touch_date else None,
            'touch_count': self.touch_count,
            'status': self.status,
            'lifecycle_stage': self.lifecycle_stage,
            'converted_at': self.converted_at.isoformat() if self.converted_at else None,
            'conversion_value': self.conversion_value,
            'conversion_source': self.conversion_source,
            'notes': self.notes,
            'metadata': self.metadata,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        } 
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, JSON
from sqlalchemy.sql import func
from models.base import Base


class Engagement(Base):
    __tablename__ = 'engagements'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    
    # Engagement details
    engagement_type = Column(String(50), nullable=False)  # view, click, share, like, comment, conversion
    engagement_source = Column(String(100), nullable=True)  # campaign, content, organic, referral
    
    # Content and campaign tracking
    content_id = Column(Integer, nullable=True)
    campaign_id = Column(String(100), nullable=True)
    message_id = Column(String(100), nullable=True)
    
    # Engagement metrics
    duration_seconds = Column(Integer, default=0)
    interaction_count = Column(Integer, default=0)
    engagement_score = Column(Float, default=0.0)
    
    # Geographic and device data
    region = Column(String(10), nullable=True)
    timezone = Column(String(50), nullable=True)
    device_type = Column(String(50), nullable=True)  # mobile, desktop, tablet
    browser = Column(String(100), nullable=True)
    
    # Session data
    session_id = Column(String(100), nullable=True)
    session_duration = Column(Integer, default=0)
    page_views = Column(Integer, default=0)
    
    # Conversion tracking
    conversion_value = Column(Float, default=0.0)
    conversion_type = Column(String(50), nullable=True)  # purchase, signup, download, etc.
    
    # Behavioral data
    user_behavior = Column(JSON, default=dict)  # Store detailed behavioral data
    intent_signals = Column(JSON, default=list)  # Purchase intent signals
    
    # Engagement context
    context = Column(JSON, default=dict)  # Additional context about the engagement
    metadata = Column(JSON, default=dict)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    
    def __repr__(self):
        return f"<Engagement(id={self.id}, user_id={self.user_id}, type={self.engagement_type}, score={self.engagement_score})>"
    
    def to_dict(self):
        """Convert engagement to dictionary"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'engagement_type': self.engagement_type,
            'engagement_source': self.engagement_source,
            'content_id': self.content_id,
            'campaign_id': self.campaign_id,
            'message_id': self.message_id,
            'duration_seconds': self.duration_seconds,
            'interaction_count': self.interaction_count,
            'engagement_score': self.engagement_score,
            'region': self.region,
            'timezone': self.timezone,
            'device_type': self.device_type,
            'browser': self.browser,
            'session_id': self.session_id,
            'session_duration': self.session_duration,
            'page_views': self.page_views,
            'conversion_value': self.conversion_value,
            'conversion_type': self.conversion_type,
            'user_behavior': self.user_behavior,
            'intent_signals': self.intent_signals,
            'context': self.context,
            'metadata': self.metadata,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def calculate_engagement_score(self):
        """Calculate engagement score based on various factors"""
        score = 0.0
        
        # Base score for engagement type
        type_scores = {
            'view': 1.0,
            'click': 2.0,
            'share': 5.0,
            'like': 3.0,
            'comment': 4.0,
            'conversion': 10.0
        }
        score += type_scores.get(self.engagement_type, 1.0)
        
        # Duration bonus
        if self.duration_seconds > 0:
            score += min(self.duration_seconds / 60, 5.0)  # Max 5 points for duration
        
        # Interaction bonus
        score += min(self.interaction_count * 0.5, 3.0)  # Max 3 points for interactions
        
        # Conversion bonus
        if self.conversion_value > 0:
            score += min(self.conversion_value / 10, 5.0)  # Max 5 points for conversion value
        
        self.engagement_score = min(score, 20.0)  # Cap at 20 points
    
    def is_high_value_engagement(self) -> bool:
        """Check if this is a high-value engagement"""
        return self.engagement_score >= 8.0 or self.conversion_value > 0
    
    def get_engagement_category(self) -> str:
        """Get engagement category based on score"""
        if self.engagement_score >= 15:
            return 'high'
        elif self.engagement_score >= 8:
            return 'medium'
        elif self.engagement_score >= 3:
            return 'low'
        else:
            return 'minimal' 
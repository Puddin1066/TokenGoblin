from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, Text
from sqlalchemy.sql import func
from models.base import Base


class UserBehavior(Base):
    __tablename__ = 'user_behavior'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    interaction_type = Column(String(100), nullable=False)  # 'browse', 'cart_add', 'purchase', 'support'
    interaction_data = Column(Text)  # JSON data about the interaction
    session_duration = Column(Integer, default=0)  # in seconds
    page_views = Column(Integer, default=0)
    created_at = Column(DateTime, default=func.now())
    
    def __repr__(self):
        return f"<UserBehavior(user_id={self.user_id}, type='{self.interaction_type}')>"


class LeadScore(Base):
    __tablename__ = 'lead_scores'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    total_score = Column(Float, nullable=False)
    browse_frequency_score = Column(Float, default=0)
    cart_abandonment_score = Column(Float, default=0)
    session_duration_score = Column(Float, default=0)
    previous_purchases_score = Column(Float, default=0)
    engagement_score = Column(Float, default=0)
    last_calculated = Column(DateTime, default=func.now())
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<LeadScore(user_id={self.user_id}, score={self.total_score})>"


class SalesOpportunity(Base):
    __tablename__ = 'sales_opportunities'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    opportunity_type = Column(String(100), nullable=False)  # 'high_engagement', 'cart_abandonment', 'returning_customer'
    score = Column(Float, nullable=False)
    reason = Column(Text)
    recommended_products = Column(Text)  # JSON array of product IDs
    status = Column(String(50), default='open')  # open, contacted, converted, closed
    contacted_at = Column(DateTime)
    converted_at = Column(DateTime)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<SalesOpportunity(user_id={self.user_id}, type='{self.opportunity_type}', score={self.score})>"


class ProactiveMessage(Base):
    __tablename__ = 'proactive_messages'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    opportunity_id = Column(Integer)
    message_type = Column(String(100), nullable=False)  # 'lead_nurture', 'cart_recovery', 'cross_sell', 'retention'
    message_content = Column(Text, nullable=False)
    sent_at = Column(DateTime, default=func.now())
    response_received = Column(Boolean, default=False)
    response_content = Column(Text)
    response_at = Column(DateTime)
    conversion_result = Column(String(50))  # 'purchase', 'engagement', 'no_response'
    
    def __repr__(self):
        return f"<ProactiveMessage(user_id={self.user_id}, type='{self.message_type}')>"
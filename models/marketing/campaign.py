from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, JSON
from sqlalchemy.sql import func
from models.base import Base


class Campaign(Base):
    __tablename__ = 'campaigns'
    
    id = Column(String(100), primary_key=True)  # campaign_20241201_143022
    name = Column(String(255), nullable=False)
    type = Column(String(50), nullable=False)  # inbound, outbound, retention, viral
    status = Column(String(50), default='draft')  # draft, active, paused, completed, archived
    
    # Campaign configuration
    target_audience = Column(String(100), nullable=True)
    channels = Column(JSON, default=list)  # ['telegram', 'email', 'linkedin']
    budget = Column(Float, default=0.0)
    budget_spent = Column(Float, default=0.0)
    
    # Campaign timing
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    scheduled_start = Column(DateTime, nullable=True)
    scheduled_end = Column(DateTime, nullable=True)
    
    # Campaign content
    message_templates = Column(JSON, default=dict)
    visual_assets = Column(JSON, default=list)
    tracking_links = Column(JSON, default=list)
    
    # Performance metrics
    impressions = Column(Integer, default=0)
    clicks = Column(Integer, default=0)
    conversions = Column(Integer, default=0)
    revenue = Column(Float, default=0.0)
    
    # Conversion rates
    click_through_rate = Column(Float, default=0.0)
    conversion_rate = Column(Float, default=0.0)
    cost_per_click = Column(Float, default=0.0)
    cost_per_conversion = Column(Float, default=0.0)
    roi = Column(Float, default=0.0)
    
    # Targeting and segmentation
    target_criteria = Column(JSON, default=dict)
    exclusion_criteria = Column(JSON, default=dict)
    segment_filters = Column(JSON, default=dict)
    
    # Automation settings
    automation_enabled = Column(Boolean, default=True)
    auto_optimize = Column(Boolean, default=False)
    auto_pause_threshold = Column(Float, default=0.0)  # Pause if conversion rate drops below this
    
    # A/B testing
    ab_test_enabled = Column(Boolean, default=False)
    ab_test_variants = Column(JSON, default=list)
    winning_variant = Column(String(50), nullable=True)
    
    # Campaign metadata
    description = Column(Text, nullable=True)
    tags = Column(JSON, default=list)
    notes = Column(Text, nullable=True)
    metadata = Column(JSON, default=dict)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<Campaign(id={self.id}, name={self.name}, type={self.type}, status={self.status})>"
    
    def to_dict(self):
        """Convert campaign to dictionary"""
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'status': self.status,
            'target_audience': self.target_audience,
            'channels': self.channels,
            'budget': self.budget,
            'budget_spent': self.budget_spent,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'scheduled_start': self.scheduled_start.isoformat() if self.scheduled_start else None,
            'scheduled_end': self.scheduled_end.isoformat() if self.scheduled_end else None,
            'message_templates': self.message_templates,
            'visual_assets': self.visual_assets,
            'tracking_links': self.tracking_links,
            'impressions': self.impressions,
            'clicks': self.clicks,
            'conversions': self.conversions,
            'revenue': self.revenue,
            'click_through_rate': self.click_through_rate,
            'conversion_rate': self.conversion_rate,
            'cost_per_click': self.cost_per_click,
            'cost_per_conversion': self.cost_per_conversion,
            'roi': self.roi,
            'target_criteria': self.target_criteria,
            'exclusion_criteria': self.exclusion_criteria,
            'segment_filters': self.segment_filters,
            'automation_enabled': self.automation_enabled,
            'auto_optimize': self.auto_optimize,
            'auto_pause_threshold': self.auto_pause_threshold,
            'ab_test_enabled': self.ab_test_enabled,
            'ab_test_variants': self.ab_test_variants,
            'winning_variant': self.winning_variant,
            'description': self.description,
            'tags': self.tags,
            'notes': self.notes,
            'metadata': self.metadata,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def calculate_metrics(self):
        """Calculate campaign performance metrics"""
        if self.impressions > 0:
            self.click_through_rate = (self.clicks / self.impressions) * 100
        
        if self.clicks > 0:
            self.conversion_rate = (self.conversions / self.clicks) * 100
            self.cost_per_click = self.budget_spent / self.clicks
        
        if self.conversions > 0:
            self.cost_per_conversion = self.budget_spent / self.conversions
        
        if self.budget_spent > 0:
            self.roi = ((self.revenue - self.budget_spent) / self.budget_spent) * 100 
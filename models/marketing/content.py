from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, JSON
from sqlalchemy.sql import func
from models.base import Base


class Content(Base):
    __tablename__ = 'content'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    content_type = Column(String(50), nullable=False)  # blog_post, social_media, email, video, case_study
    
    # Content details
    content = Column(Text, nullable=False)
    excerpt = Column(Text, nullable=True)
    meta_description = Column(Text, nullable=True)
    
    # SEO and targeting
    target_keywords = Column(JSON, default=list)
    seo_score = Column(Float, default=0.0)
    readability_score = Column(Float, default=0.0)
    
    # Content metadata
    author = Column(String(100), nullable=True)
    language = Column(String(10), default='en')
    region = Column(String(10), nullable=True)
    target_audience = Column(String(100), nullable=True)
    
    # Publishing and scheduling
    status = Column(String(50), default='draft')  # draft, published, scheduled, archived
    published_at = Column(DateTime, nullable=True)
    scheduled_at = Column(DateTime, nullable=True)
    
    # Performance metrics
    views = Column(Integer, default=0)
    shares = Column(Integer, default=0)
    engagement_rate = Column(Float, default=0.0)
    conversion_rate = Column(Float, default=0.0)
    
    # Campaign association
    campaign_id = Column(String(100), nullable=True)
    content_calendar_id = Column(String(100), nullable=True)
    
    # Content optimization
    ab_test_variants = Column(JSON, default=list)
    winning_variant = Column(String(50), nullable=True)
    optimization_suggestions = Column(JSON, default=list)
    
    # Assets and media
    featured_image = Column(String(255), nullable=True)
    media_assets = Column(JSON, default=list)
    external_links = Column(JSON, default=list)
    
    # Content categorization
    categories = Column(JSON, default=list)
    tags = Column(JSON, default=list)
    topics = Column(JSON, default=list)
    
    # AI generation metadata
    ai_generated = Column(Boolean, default=False)
    generation_model = Column(String(100), nullable=True)
    generation_prompt = Column(Text, nullable=True)
    generation_metadata = Column(JSON, default=dict)
    
    # Content lifecycle
    content_stage = Column(String(50), default='creation')  # creation, review, approval, published, archived
    review_notes = Column(Text, nullable=True)
    approval_status = Column(String(50), default='pending')  # pending, approved, rejected
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<Content(id={self.id}, title={self.title}, type={self.content_type}, status={self.status})>"
    
    def to_dict(self):
        """Convert content to dictionary"""
        return {
            'id': self.id,
            'title': self.title,
            'content_type': self.content_type,
            'content': self.content,
            'excerpt': self.excerpt,
            'meta_description': self.meta_description,
            'target_keywords': self.target_keywords,
            'seo_score': self.seo_score,
            'readability_score': self.readability_score,
            'author': self.author,
            'language': self.language,
            'region': self.region,
            'target_audience': self.target_audience,
            'status': self.status,
            'published_at': self.published_at.isoformat() if self.published_at else None,
            'scheduled_at': self.scheduled_at.isoformat() if self.scheduled_at else None,
            'views': self.views,
            'shares': self.shares,
            'engagement_rate': self.engagement_rate,
            'conversion_rate': self.conversion_rate,
            'campaign_id': self.campaign_id,
            'content_calendar_id': self.content_calendar_id,
            'ab_test_variants': self.ab_test_variants,
            'winning_variant': self.winning_variant,
            'optimization_suggestions': self.optimization_suggestions,
            'featured_image': self.featured_image,
            'media_assets': self.media_assets,
            'external_links': self.external_links,
            'categories': self.categories,
            'tags': self.tags,
            'topics': self.topics,
            'ai_generated': self.ai_generated,
            'generation_model': self.generation_model,
            'generation_prompt': self.generation_prompt,
            'generation_metadata': self.generation_metadata,
            'content_stage': self.content_stage,
            'review_notes': self.review_notes,
            'approval_status': self.approval_status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def calculate_engagement_rate(self, total_impressions: int):
        """Calculate engagement rate based on views and interactions"""
        if total_impressions > 0:
            self.engagement_rate = (self.views / total_impressions) * 100
    
    def is_published(self) -> bool:
        """Check if content is published"""
        return self.status == 'published' and self.published_at is not None
    
    def is_scheduled(self) -> bool:
        """Check if content is scheduled for future publication"""
        return self.status == 'scheduled' and self.scheduled_at is not None 
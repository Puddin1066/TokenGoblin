"""
Conversation model for managing sales conversations
"""
from datetime import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, JSON, Text, ForeignKey, func
from sqlalchemy.orm import relationship
from pydantic import BaseModel

from models.base import Base


class Conversation(Base):
    """Model for managing sales conversations"""
    __tablename__ = 'conversations'

    id = Column(Integer, primary_key=True)
    prospect_id = Column(Integer, ForeignKey('prospects.id'), nullable=False)
    
    # Conversation state
    status = Column(String(50), default='active')  # active, closed, paused, converted
    stage = Column(String(50), default='initial_contact')  # initial_contact, needs_assessment, value_proposition, objection_handling, closing, follow_up
    
    # Engagement metrics
    message_count = Column(Integer, default=0)
    prospect_responses = Column(Integer, default=0)
    last_message_from = Column(String(20), nullable=True)  # 'agent' or 'prospect'
    
    # Conversion tracking
    conversion_probability = Column(Float, default=0.0)
    engagement_score = Column(Float, default=0.0)
    
    # Timing
    started_at = Column(DateTime, default=func.now())
    last_interaction = Column(DateTime, default=func.now())
    closed_at = Column(DateTime, nullable=True)
    
    # Outcomes
    outcome = Column(String(100), nullable=True)  # converted, lost, not_interested, no_response
    outcome_reason = Column(Text, nullable=True)
    
    # Metadata
    metadata = Column(JSON, default=dict)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    prospect = relationship("Prospect", back_populates="conversations")
    messages = relationship("ConversationMessage", back_populates="conversation")
    
    def __repr__(self):
        return f"<Conversation(id={self.id}, prospect_id={self.prospect_id}, status={self.status})>"


class ConversationMessage(Base):
    """Model for individual conversation messages"""
    __tablename__ = 'conversation_messages'

    id = Column(Integer, primary_key=True)
    conversation_id = Column(Integer, ForeignKey('conversations.id'), nullable=False)
    
    # Message content
    sender = Column(String(20), nullable=False)  # 'agent' or 'prospect'
    content = Column(Text, nullable=False)
    message_type = Column(String(50), default='text')  # text, image, document, etc.
    
    # AI metadata
    ai_generated = Column(Boolean, default=False)
    ai_model = Column(String(100), nullable=True)
    ai_prompt = Column(Text, nullable=True)
    
    # Engagement metrics
    read = Column(Boolean, default=False)
    responded = Column(Boolean, default=False)
    
    # Telegram metadata
    telegram_message_id = Column(Integer, nullable=True)
    
    # Timestamps
    sent_at = Column(DateTime, default=func.now())
    read_at = Column(DateTime, nullable=True)
    
    # Relationships
    conversation = relationship("Conversation", back_populates="messages")
    
    def __repr__(self):
        return f"<ConversationMessage(id={self.id}, conversation_id={self.conversation_id}, sender={self.sender})>"


class ConversationDTO(BaseModel):
    """Pydantic model for conversation data transfer"""
    id: Optional[int] = None
    prospect_id: int
    status: str = 'active'
    stage: str = 'initial_contact'
    message_count: int = 0
    prospect_responses: int = 0
    last_message_from: Optional[str] = None
    conversion_probability: float = 0.0
    engagement_score: float = 0.0
    started_at: Optional[datetime] = None
    last_interaction: Optional[datetime] = None
    closed_at: Optional[datetime] = None
    outcome: Optional[str] = None
    outcome_reason: Optional[str] = None
    metadata: Dict[str, Any] = {}
    
    class Config:
        from_attributes = True


class ConversationMessageDTO(BaseModel):
    """Pydantic model for conversation message data transfer"""
    id: Optional[int] = None
    conversation_id: int
    sender: str
    content: str
    message_type: str = 'text'
    ai_generated: bool = False
    ai_model: Optional[str] = None
    ai_prompt: Optional[str] = None
    read: bool = False
    responded: bool = False
    telegram_message_id: Optional[int] = None
    sent_at: Optional[datetime] = None
    read_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
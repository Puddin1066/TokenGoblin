from datetime import datetime
from enum import Enum
from pydantic import BaseModel
from sqlalchemy import Column, Integer, String, Float, DateTime, func, Text
from sqlalchemy.types import Enum as SQLEnum

from models.base import Base


class TransactionStatus(Enum):
    PENDING_PAYMENT = "pending_payment"
    PROCESSING = "processing"  
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"


class Transaction(Base):
    __tablename__ = 'transactions'

    id = Column(Integer, primary_key=True, unique=True)
    user_telegram_id = Column(Integer, nullable=False)
    
    # Payment details
    payment_method = Column(String(20), nullable=False)  # 'crypto' or 'fiat'
    payment_amount = Column(Float, nullable=False)
    payment_currency = Column(String(10), nullable=False)  # USD, BTC, ETH, etc.
    
    # Token details
    token_symbol = Column(String(10), nullable=False)
    token_amount = Column(Float, nullable=False)
    recipient_address = Column(String(100), nullable=False)
    
    # Transaction tracking
    status = Column(SQLEnum(TransactionStatus), default=TransactionStatus.PENDING_PAYMENT)
    fees = Column(Float, nullable=False)
    tx_hash = Column(String(100), nullable=True)  # Blockchain transaction hash
    error_message = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class TransactionDTO(BaseModel):
    id: int | None = None
    user_telegram_id: int
    payment_method: str
    payment_amount: float
    payment_currency: str
    token_symbol: str
    token_amount: float
    recipient_address: str
    status: TransactionStatus = TransactionStatus.PENDING_PAYMENT
    fees: float
    tx_hash: str | None = None
    error_message: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None
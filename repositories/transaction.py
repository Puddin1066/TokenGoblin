from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from sqlalchemy import select, update

from models.transaction import Transaction, TransactionDTO, TransactionStatus


class TransactionRepository:
    
    @staticmethod
    async def create(transaction_dto: TransactionDTO, session: AsyncSession | Session) -> int:
        """Create a new transaction record"""
        transaction = Transaction(
            user_telegram_id=transaction_dto.user_telegram_id,
            payment_method=transaction_dto.payment_method,
            payment_amount=transaction_dto.payment_amount,
            payment_currency=transaction_dto.payment_currency,
            token_symbol=transaction_dto.token_symbol,
            token_amount=transaction_dto.token_amount,
            recipient_address=transaction_dto.recipient_address,
            status=transaction_dto.status,
            fees=transaction_dto.fees
        )
        
        session.add(transaction)
        await session.flush()
        return transaction.id
    
    @staticmethod
    async def get_by_id(transaction_id: int, session: AsyncSession | Session) -> TransactionDTO | None:
        """Get transaction by ID"""
        if isinstance(session, AsyncSession):
            result = await session.execute(
                select(Transaction).where(Transaction.id == transaction_id)
            )
            transaction = result.scalar_one_or_none()
        else:
            transaction = session.query(Transaction).filter(Transaction.id == transaction_id).first()
        
        if transaction:
            return TransactionDTO(
                id=transaction.id,
                user_telegram_id=transaction.user_telegram_id,
                payment_method=transaction.payment_method,
                payment_amount=transaction.payment_amount,
                payment_currency=transaction.payment_currency,
                token_symbol=transaction.token_symbol,
                token_amount=transaction.token_amount,
                recipient_address=transaction.recipient_address,
                status=transaction.status,
                fees=transaction.fees,
                tx_hash=transaction.tx_hash,
                error_message=transaction.error_message,
                created_at=transaction.created_at,
                updated_at=transaction.updated_at
            )
        return None
    
    @staticmethod
    async def update(transaction_dto: TransactionDTO, session: AsyncSession | Session):
        """Update transaction"""
        if isinstance(session, AsyncSession):
            await session.execute(
                update(Transaction)
                .where(Transaction.id == transaction_dto.id)
                .values(
                    status=transaction_dto.status,
                    tx_hash=transaction_dto.tx_hash,
                    error_message=transaction_dto.error_message
                )
            )
        else:
            session.query(Transaction).filter(Transaction.id == transaction_dto.id).update({
                'status': transaction_dto.status,
                'tx_hash': transaction_dto.tx_hash,
                'error_message': transaction_dto.error_message
            })
    
    @staticmethod
    async def get_by_user(
        telegram_id: int, 
        session: AsyncSession | Session,
        limit: int = 10
    ) -> list[TransactionDTO]:
        """Get user's transaction history"""
        if isinstance(session, AsyncSession):
            result = await session.execute(
                select(Transaction)
                .where(Transaction.user_telegram_id == telegram_id)
                .order_by(Transaction.created_at.desc())
                .limit(limit)
            )
            transactions = result.scalars().all()
        else:
            transactions = (session.query(Transaction)
                          .filter(Transaction.user_telegram_id == telegram_id)
                          .order_by(Transaction.created_at.desc())
                          .limit(limit)
                          .all())
        
        return [
            TransactionDTO(
                id=t.id,
                user_telegram_id=t.user_telegram_id,
                payment_method=t.payment_method,
                payment_amount=t.payment_amount,
                payment_currency=t.payment_currency,
                token_symbol=t.token_symbol,
                token_amount=t.token_amount,
                recipient_address=t.recipient_address,
                status=t.status,
                fees=t.fees,
                tx_hash=t.tx_hash,
                error_message=t.error_message,
                created_at=t.created_at,
                updated_at=t.updated_at
            )
            for t in transactions
        ]
    
    @staticmethod
    async def get_pending_transactions(session: AsyncSession | Session) -> list[TransactionDTO]:
        """Get all pending transactions for processing"""
        if isinstance(session, AsyncSession):
            result = await session.execute(
                select(Transaction)
                .where(Transaction.status.in_([
                    TransactionStatus.PENDING_PAYMENT,
                    TransactionStatus.PROCESSING
                ]))
                .order_by(Transaction.created_at.asc())
            )
            transactions = result.scalars().all()
        else:
            transactions = (session.query(Transaction)
                          .filter(Transaction.status.in_([
                              TransactionStatus.PENDING_PAYMENT,
                              TransactionStatus.PROCESSING
                          ]))
                          .order_by(Transaction.created_at.asc())
                          .all())
        
        return [
            TransactionDTO(
                id=t.id,
                user_telegram_id=t.user_telegram_id,
                payment_method=t.payment_method,
                payment_amount=t.payment_amount,
                payment_currency=t.payment_currency,
                token_symbol=t.token_symbol,
                token_amount=t.token_amount,
                recipient_address=t.recipient_address,
                status=t.status,
                fees=t.fees,
                tx_hash=t.tx_hash,
                error_message=t.error_message,
                created_at=t.created_at,
                updated_at=t.updated_at
            )
            for t in transactions
        ]
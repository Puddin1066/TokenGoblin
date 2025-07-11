from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy import select, and_, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from models.ai_token import AITokenPackage, AITokenAllocation, AITokenPackageDTO, AITokenAllocationDTO
from repositories.base import BaseRepository


class AITokenPackageRepository(BaseRepository):
    
    @staticmethod
    async def create(package_dto: AITokenPackageDTO, session: AsyncSession | Session) -> AITokenPackage:
        package = AITokenPackage(**package_dto.model_dump(exclude_none=True))
        session.add(package)
        await session.flush()
        return package
    
    @staticmethod
    async def get_available_packages(session: AsyncSession | Session) -> List[AITokenPackage]:
        query = select(AITokenPackage).where(AITokenPackage.is_available == True)
        result = await session.execute(query)
        return result.scalars().all()
    
    @staticmethod
    async def get_featured_packages(session: AsyncSession | Session) -> List[AITokenPackage]:
        query = select(AITokenPackage).where(
            and_(AITokenPackage.is_available == True, AITokenPackage.is_featured == True)
        )
        result = await session.execute(query)
        return result.scalars().all()
    
    @staticmethod
    async def get_by_category(category_id: int, session: AsyncSession | Session) -> List[AITokenPackage]:
        query = select(AITokenPackage).where(
            and_(AITokenPackage.category_id == category_id, AITokenPackage.is_available == True)
        )
        result = await session.execute(query)
        return result.scalars().all()
    
    @staticmethod
    async def get_by_subcategory(subcategory_id: int, session: AsyncSession | Session) -> List[AITokenPackage]:
        query = select(AITokenPackage).where(
            and_(AITokenPackage.subcategory_id == subcategory_id, AITokenPackage.is_available == True)
        )
        result = await session.execute(query)
        return result.scalars().all()
    
    @staticmethod
    async def get_by_id(package_id: int, session: AsyncSession | Session) -> Optional[AITokenPackage]:
        query = select(AITokenPackage).where(AITokenPackage.id == package_id)
        result = await session.execute(query)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def update_availability(package_id: int, is_available: bool, session: AsyncSession | Session):
        package = await AITokenPackageRepository.get_by_id(package_id, session)
        if package:
            package.is_available = is_available
            package.updated_at = datetime.utcnow()
    
    @staticmethod
    async def get_profit_stats(days: int, session: AsyncSession | Session) -> dict:
        """Get profit statistics for the last N days"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        query = select(
            func.count(AITokenPackage.id).label('total_packages'),
            func.sum(AITokenPackage.sell_price - AITokenPackage.cost_price).label('total_profit'),
            func.avg(AITokenPackage.sell_price - AITokenPackage.cost_price).label('avg_profit')
        ).where(AITokenPackage.created_at >= cutoff_date)
        
        result = await session.execute(query)
        row = result.first()
        
        return {
            'total_packages': row.total_packages or 0,
            'total_profit': float(row.total_profit or 0),
            'avg_profit': float(row.avg_profit or 0)
        }


class AITokenAllocationRepository(BaseRepository):
    
    @staticmethod
    async def create(allocation_dto: AITokenAllocationDTO, session: AsyncSession | Session) -> AITokenAllocation:
        allocation = AITokenAllocation(**allocation_dto.model_dump(exclude_none=True))
        session.add(allocation)
        await session.flush()
        return allocation
    
    @staticmethod
    async def get_by_user(user_id: int, session: AsyncSession | Session) -> List[AITokenAllocation]:
        query = select(AITokenAllocation).where(
            and_(AITokenAllocation.user_id == user_id, AITokenAllocation.is_active == True)
        ).order_by(desc(AITokenAllocation.created_at))
        result = await session.execute(query)
        return result.scalars().all()
    
    @staticmethod
    async def get_by_api_key(api_key: str, session: AsyncSession | Session) -> Optional[AITokenAllocation]:
        query = select(AITokenAllocation).where(AITokenAllocation.api_key == api_key)
        result = await session.execute(query)
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_active_allocations(session: AsyncSession | Session) -> List[AITokenAllocation]:
        query = select(AITokenAllocation).where(
            and_(
                AITokenAllocation.is_active == True,
                AITokenAllocation.expires_at > datetime.utcnow()
            )
        )
        result = await session.execute(query)
        return result.scalars().all()
    
    @staticmethod
    async def get_expired_allocations(session: AsyncSession | Session) -> List[AITokenAllocation]:
        query = select(AITokenAllocation).where(
            and_(
                AITokenAllocation.is_active == True,
                AITokenAllocation.expires_at <= datetime.utcnow()
            )
        )
        result = await session.execute(query)
        return result.scalars().all()
    
    @staticmethod
    async def use_tokens(api_key: str, token_count: int, session: AsyncSession | Session) -> bool:
        """Use tokens from an allocation and return True if successful"""
        allocation = await AITokenAllocationRepository.get_by_api_key(api_key, session)
        
        if not allocation or not allocation.is_active:
            return False
        
        if allocation.expires_at <= datetime.utcnow():
            allocation.is_active = False
            return False
        
        if allocation.remaining_tokens < token_count:
            return False
        
        # Reset daily counter if needed
        now = datetime.utcnow()
        if now.date() > allocation.daily_reset_at.date():
            allocation.tokens_used_today = 0
            allocation.daily_reset_at = now
        
        # Check daily limit
        if allocation.package.daily_limit:
            if allocation.tokens_used_today + token_count > allocation.package.daily_limit:
                return False
        
        # Update usage
        allocation.remaining_tokens -= token_count
        allocation.tokens_used_today += token_count
        allocation.total_requests += 1
        allocation.last_used = now
        allocation.updated_at = now
        
        # Deactivate if no tokens left
        if allocation.remaining_tokens <= 0:
            allocation.is_active = False
        
        return True
    
    @staticmethod
    async def cleanup_expired(session: AsyncSession | Session) -> int:
        """Deactivate expired allocations and return count"""
        expired = await AITokenAllocationRepository.get_expired_allocations(session)
        count = 0
        
        for allocation in expired:
            allocation.is_active = False
            allocation.updated_at = datetime.utcnow()
            count += 1
        
        return count
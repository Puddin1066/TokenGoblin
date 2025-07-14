from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from sqlalchemy import select, update, and_, func
from typing import List, Optional, Dict
from datetime import datetime, timedelta

from models.user_behavior import UserBehavior, LeadScore, SalesOpportunity, ProactiveMessage


class UserBehaviorRepository:
    
    @staticmethod
    async def create(behavior: UserBehavior, session: AsyncSession | Session) -> UserBehavior:
        """Create new user behavior record"""
        session.add(behavior)
        await session.commit()
        await session.refresh(behavior)
        return behavior
    
    @staticmethod
    async def get_user_behaviors(user_id: int, days: int = 30, session: AsyncSession | Session) -> List[UserBehavior]:
        """Get user behaviors for specified days"""
        cutoff_date = datetime.now() - timedelta(days=days)
        result = await session.execute(
            select(UserBehavior).where(
                and_(
                    UserBehavior.user_id == user_id,
                    UserBehavior.created_at >= cutoff_date
                )
            ).order_by(UserBehavior.created_at.desc())
        )
        return result.scalars().all()
    
    @staticmethod
    async def get_browse_behaviors(user_id: int, days: int = 7, session: AsyncSession | Session) -> List[UserBehavior]:
        """Get user's browse behaviors"""
        cutoff_date = datetime.now() - timedelta(days=days)
        result = await session.execute(
            select(UserBehavior).where(
                and_(
                    UserBehavior.user_id == user_id,
                    UserBehavior.interaction_type == 'browse',
                    UserBehavior.created_at >= cutoff_date
                )
            )
        )
        return result.scalars().all()
    
    @staticmethod
    async def get_cart_behaviors(user_id: int, days: int = 7, session: AsyncSession | Session) -> List[UserBehavior]:
        """Get user's cart behaviors"""
        cutoff_date = datetime.now() - timedelta(days=days)
        result = await session.execute(
            select(UserBehavior).where(
                and_(
                    UserBehavior.user_id == user_id,
                    UserBehavior.interaction_type.in_(['cart_add', 'cart_remove']),
                    UserBehavior.created_at >= cutoff_date
                )
            )
        )
        return result.scalars().all()
    
    @staticmethod
    async def get_purchase_behaviors(user_id: int, days: int = 30, session: AsyncSession | Session) -> List[UserBehavior]:
        """Get user's purchase behaviors"""
        cutoff_date = datetime.now() - timedelta(days=days)
        result = await session.execute(
            select(UserBehavior).where(
                and_(
                    UserBehavior.user_id == user_id,
                    UserBehavior.interaction_type == 'purchase',
                    UserBehavior.created_at >= cutoff_date
                )
            )
        )
        return result.scalars().all()


class LeadScoreRepository:
    
    @staticmethod
    async def get_by_user_id(user_id: int, session: AsyncSession | Session) -> Optional[LeadScore]:
        """Get lead score by user ID"""
        result = await session.execute(select(LeadScore).where(LeadScore.user_id == user_id))
        return result.scalar_one_or_none()
    
    @staticmethod
    async def create(lead_score: LeadScore, session: AsyncSession | Session) -> LeadScore:
        """Create new lead score"""
        session.add(lead_score)
        await session.commit()
        await session.refresh(lead_score)
        return lead_score
    
    @staticmethod
    async def update(lead_score: LeadScore, session: AsyncSession | Session) -> LeadScore:
        """Update lead score"""
        lead_score.updated_at = datetime.now()
        await session.commit()
        await session.refresh(lead_score)
        return lead_score
    
    @staticmethod
    async def get_high_value_leads(threshold: float = 0.7, session: AsyncSession | Session) -> List[LeadScore]:
        """Get high-value leads above threshold"""
        result = await session.execute(
            select(LeadScore).where(LeadScore.total_score >= threshold)
        )
        return result.scalars().all()
    
    @staticmethod
    async def get_recent_scores(days: int = 7, session: AsyncSession | Session) -> List[LeadScore]:
        """Get recently calculated lead scores"""
        cutoff_date = datetime.now() - timedelta(days=days)
        result = await session.execute(
            select(LeadScore).where(LeadScore.last_calculated >= cutoff_date)
        )
        return result.scalars().all()


class SalesOpportunityRepository:
    
    @staticmethod
    async def create(opportunity: SalesOpportunity, session: AsyncSession | Session) -> SalesOpportunity:
        """Create new sales opportunity"""
        session.add(opportunity)
        await session.commit()
        await session.refresh(opportunity)
        return opportunity
    
    @staticmethod
    async def get_open_opportunities(session: AsyncSession | Session) -> List[SalesOpportunity]:
        """Get open sales opportunities"""
        result = await session.execute(
            select(SalesOpportunity).where(SalesOpportunity.status == 'open')
        )
        return result.scalars().all()
    
    @staticmethod
    async def get_by_user_id(user_id: int, session: AsyncSession | Session) -> List[SalesOpportunity]:
        """Get sales opportunities for user"""
        result = await session.execute(
            select(SalesOpportunity).where(SalesOpportunity.user_id == user_id)
        )
        return result.scalars().all()
    
    @staticmethod
    async def update_status(opportunity_id: int, status: str, session: AsyncSession | Session) -> bool:
        """Update opportunity status"""
        result = await session.execute(
            update(SalesOpportunity).where(SalesOpportunity.id == opportunity_id).values(
                status=status,
                updated_at=datetime.now()
            )
        )
        await session.commit()
        return result.rowcount > 0
    
    @staticmethod
    async def mark_contacted(opportunity_id: int, session: AsyncSession | Session) -> bool:
        """Mark opportunity as contacted"""
        result = await session.execute(
            update(SalesOpportunity).where(SalesOpportunity.id == opportunity_id).values(
                status='contacted',
                contacted_at=datetime.now(),
                updated_at=datetime.now()
            )
        )
        await session.commit()
        return result.rowcount > 0
    
    @staticmethod
    async def mark_converted(opportunity_id: int, session: AsyncSession | Session) -> bool:
        """Mark opportunity as converted"""
        result = await session.execute(
            update(SalesOpportunity).where(SalesOpportunity.id == opportunity_id).values(
                status='converted',
                converted_at=datetime.now(),
                updated_at=datetime.now()
            )
        )
        await session.commit()
        return result.rowcount > 0


class ProactiveMessageRepository:
    
    @staticmethod
    async def create(message: ProactiveMessage, session: AsyncSession | Session) -> ProactiveMessage:
        """Create new proactive message"""
        session.add(message)
        await session.commit()
        await session.refresh(message)
        return message
    
    @staticmethod
    async def get_recent_messages(user_id: int, days: int = 7, session: AsyncSession | Session) -> List[ProactiveMessage]:
        """Get recent proactive messages for user"""
        cutoff_date = datetime.now() - timedelta(days=days)
        result = await session.execute(
            select(ProactiveMessage).where(
                and_(
                    ProactiveMessage.user_id == user_id,
                    ProactiveMessage.sent_at >= cutoff_date
                )
            )
        )
        return result.scalars().all()
    
    @staticmethod
    async def update_response(message_id: int, response_content: str, session: AsyncSession | Session) -> bool:
        """Update message with response"""
        result = await session.execute(
            update(ProactiveMessage).where(ProactiveMessage.id == message_id).values(
                response_received=True,
                response_content=response_content,
                response_at=datetime.now()
            )
        )
        await session.commit()
        return result.rowcount > 0
    
    @staticmethod
    async def update_conversion_result(message_id: int, result: str, session: AsyncSession | Session) -> bool:
        """Update message conversion result"""
        result_update = await session.execute(
            update(ProactiveMessage).where(ProactiveMessage.id == message_id).values(
                conversion_result=result
            )
        )
        await session.commit()
        return result_update.rowcount > 0
    
    @staticmethod
    async def get_conversion_stats(days: int = 30, session: AsyncSession | Session) -> Dict:
        """Get conversion statistics for proactive messages"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        # Get total messages sent
        total_result = await session.execute(
            select(func.count(ProactiveMessage.id)).where(
                ProactiveMessage.sent_at >= cutoff_date
            )
        )
        total_messages = total_result.scalar()
        
        # Get conversion results
        conversion_result = await session.execute(
            select(ProactiveMessage.conversion_result, func.count(ProactiveMessage.id)).where(
                and_(
                    ProactiveMessage.sent_at >= cutoff_date,
                    ProactiveMessage.conversion_result.isnot(None)
                )
            ).group_by(ProactiveMessage.conversion_result)
        )
        
        conversion_stats = {}
        for row in conversion_result.fetchall():
            conversion_stats[row[0]] = row[1]
        
        return {
            'total_messages': total_messages,
            'conversion_stats': conversion_stats
        }
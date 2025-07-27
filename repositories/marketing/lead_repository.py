import asyncio
import logging
from typing import Dict, List, Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_, desc
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from models.marketing.lead import Lead
from models.user import User

logger = logging.getLogger(__name__)


class LeadRepository:
    """Repository for lead data operations"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create_lead(self, lead_data: Dict[str, Any]) -> Lead:
        """Create a new lead"""
        try:
            lead = Lead(**lead_data)
            self.session.add(lead)
            await self.session.commit()
            await self.session.refresh(lead)
            logger.info(f"Created lead {lead.id} for user {lead.user_id}")
            return lead
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error creating lead: {e}")
            raise
    
    async def get_lead_by_id(self, lead_id: int) -> Optional[Lead]:
        """Get lead by ID"""
        try:
            result = await self.session.execute(
                select(Lead).where(Lead.id == lead_id)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting lead {lead_id}: {e}")
            return None
    
    async def get_lead_by_user_id(self, user_id: int) -> Optional[Lead]:
        """Get lead by user ID"""
        try:
            result = await self.session.execute(
                select(Lead).where(Lead.user_id == user_id)
            )
            return result.scalar_one_or_none()
        except Exception as e:
            logger.error(f"Error getting lead for user {user_id}: {e}")
            return None
    
    async def get_leads_by_status(self, status: str, limit: int = 100) -> List[Lead]:
        """Get leads by status"""
        try:
            result = await self.session.execute(
                select(Lead)
                .where(Lead.status == status)
                .order_by(desc(Lead.qualification_score))
                .limit(limit)
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error getting leads by status {status}: {e}")
            return []
    
    async def get_qualified_leads(self, min_score: float = 0.6, limit: int = 50) -> List[Lead]:
        """Get qualified leads above minimum score"""
        try:
            result = await self.session.execute(
                select(Lead)
                .where(Lead.qualification_score >= min_score)
                .order_by(desc(Lead.qualification_score))
                .limit(limit)
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error getting qualified leads: {e}")
            return []
    
    async def get_leads_by_grade(self, grade: str, limit: int = 100) -> List[Lead]:
        """Get leads by grade (A, B, C, D)"""
        try:
            result = await self.session.execute(
                select(Lead)
                .where(Lead.grade == grade)
                .order_by(desc(Lead.qualification_score))
                .limit(limit)
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error getting leads by grade {grade}: {e}")
            return []
    
    async def get_leads_by_region(self, region: str, limit: int = 100) -> List[Lead]:
        """Get leads by region"""
        try:
            result = await self.session.execute(
                select(Lead)
                .where(Lead.region == region)
                .order_by(desc(Lead.qualification_score))
                .limit(limit)
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error getting leads by region {region}: {e}")
            return []
    
    async def get_leads_by_campaign(self, campaign_id: str, limit: int = 100) -> List[Lead]:
        """Get leads by campaign ID"""
        try:
            result = await self.session.execute(
                select(Lead)
                .where(Lead.campaign_id == campaign_id)
                .order_by(desc(Lead.qualification_score))
                .limit(limit)
            )
            return result.scalars().all()
        except Exception as e:
            logger.error(f"Error getting leads by campaign {campaign_id}: {e}")
            return []
    
    async def update_lead(self, lead_id: int, update_data: Dict[str, Any]) -> Optional[Lead]:
        """Update lead data"""
        try:
            lead = await self.get_lead_by_id(lead_id)
            if not lead:
                return None
            
            for key, value in update_data.items():
                if hasattr(lead, key):
                    setattr(lead, key, value)
            
            lead.updated_at = datetime.now()
            await self.session.commit()
            await self.session.refresh(lead)
            logger.info(f"Updated lead {lead_id}")
            return lead
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error updating lead {lead_id}: {e}")
            return None
    
    async def update_lead_score(self, lead_id: int, new_score: float, new_grade: str = None) -> bool:
        """Update lead qualification score and grade"""
        try:
            lead = await self.get_lead_by_id(lead_id)
            if not lead:
                return False
            
            lead.qualification_score = new_score
            if new_grade:
                lead.grade = new_grade
            lead.updated_at = datetime.now()
            
            await self.session.commit()
            logger.info(f"Updated lead {lead_id} score to {new_score}")
            return True
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error updating lead score {lead_id}: {e}")
            return False
    
    async def update_lead_status(self, lead_id: int, new_status: str, lifecycle_stage: str = None) -> bool:
        """Update lead status and lifecycle stage"""
        try:
            lead = await self.get_lead_by_id(lead_id)
            if not lead:
                return False
            
            lead.status = new_status
            if lifecycle_stage:
                lead.lifecycle_stage = lifecycle_stage
            lead.updated_at = datetime.now()
            
            await self.session.commit()
            logger.info(f"Updated lead {lead_id} status to {new_status}")
            return True
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error updating lead status {lead_id}: {e}")
            return False
    
    async def add_engagement_activity(self, lead_id: int, activity: Dict[str, Any]) -> bool:
        """Add engagement activity to lead"""
        try:
            lead = await self.get_lead_by_id(lead_id)
            if not lead:
                return False
            
            if not lead.engagement_activities:
                lead.engagement_activities = []
            
            lead.engagement_activities.append({
                'activity': activity,
                'timestamp': datetime.now().isoformat()
            })
            lead.touch_count += 1
            lead.last_touch_date = datetime.now()
            lead.updated_at = datetime.now()
            
            await self.session.commit()
            logger.info(f"Added engagement activity to lead {lead_id}")
            return True
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error adding engagement activity to lead {lead_id}: {e}")
            return False
    
    async def add_intent_signal(self, lead_id: int, signal: Dict[str, Any]) -> bool:
        """Add intent signal to lead"""
        try:
            lead = await self.get_lead_by_id(lead_id)
            if not lead:
                return False
            
            if not lead.intent_signals:
                lead.intent_signals = []
            
            lead.intent_signals.append({
                'signal': signal,
                'timestamp': datetime.now().isoformat()
            })
            lead.updated_at = datetime.now()
            
            await self.session.commit()
            logger.info(f"Added intent signal to lead {lead_id}")
            return True
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error adding intent signal to lead {lead_id}: {e}")
            return False
    
    async def mark_lead_converted(self, lead_id: int, conversion_value: float = 0.0, conversion_source: str = None) -> bool:
        """Mark lead as converted"""
        try:
            lead = await self.get_lead_by_id(lead_id)
            if not lead:
                return False
            
            lead.status = 'converted'
            lead.lifecycle_stage = 'conversion'
            lead.converted_at = datetime.now()
            lead.conversion_value = conversion_value
            if conversion_source:
                lead.conversion_source = conversion_source
            lead.updated_at = datetime.now()
            
            await self.session.commit()
            logger.info(f"Marked lead {lead_id} as converted")
            return True
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error marking lead {lead_id} as converted: {e}")
            return False
    
    async def get_lead_analytics(self, days: int = 30) -> Dict[str, Any]:
        """Get lead analytics for the specified period"""
        try:
            start_date = datetime.now() - timedelta(days=days)
            
            # Total leads
            total_result = await self.session.execute(
                select(func.count(Lead.id))
                .where(Lead.created_at >= start_date)
            )
            total_leads = total_result.scalar()
            
            # Leads by status
            status_result = await self.session.execute(
                select(Lead.status, func.count(Lead.id))
                .where(Lead.created_at >= start_date)
                .group_by(Lead.status)
            )
            leads_by_status = dict(status_result.all())
            
            # Leads by grade
            grade_result = await self.session.execute(
                select(Lead.grade, func.count(Lead.id))
                .where(Lead.created_at >= start_date)
                .group_by(Lead.grade)
            )
            leads_by_grade = dict(grade_result.all())
            
            # Conversion rate
            converted_result = await self.session.execute(
                select(func.count(Lead.id))
                .where(and_(
                    Lead.created_at >= start_date,
                    Lead.status == 'converted'
                ))
            )
            converted_leads = converted_result.scalar()
            conversion_rate = (converted_leads / total_leads * 100) if total_leads > 0 else 0
            
            return {
                'total_leads': total_leads,
                'leads_by_status': leads_by_status,
                'leads_by_grade': leads_by_grade,
                'conversion_rate': conversion_rate,
                'converted_leads': converted_leads,
                'period_days': days
            }
        except Exception as e:
            logger.error(f"Error getting lead analytics: {e}")
            return {}
    
    async def delete_lead(self, lead_id: int) -> bool:
        """Delete a lead"""
        try:
            lead = await self.get_lead_by_id(lead_id)
            if not lead:
                return False
            
            await self.session.delete(lead)
            await self.session.commit()
            logger.info(f"Deleted lead {lead_id}")
            return True
        except Exception as e:
            await self.session.rollback()
            logger.error(f"Error deleting lead {lead_id}: {e}")
            return False 
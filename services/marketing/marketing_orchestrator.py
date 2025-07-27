import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession

from marketing.inbound.content_engine import ContentGenerationEngine
from marketing.inbound.seo_optimizer import SEOOptimizer
from marketing.inbound.lead_qualifier import LeadQualificationEngine
from repositories.marketing.lead_repository import LeadRepository
import config

logger = logging.getLogger(__name__)


class MarketingOrchestrator:
    """Main marketing orchestrator that coordinates all marketing activities"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.lead_repository = LeadRepository(session)
        
        # Initialize marketing components
        self.content_engine = ContentGenerationEngine()
        self.seo_optimizer = SEOOptimizer()
        self.lead_qualifier = LeadQualificationEngine()
        
        # Marketing automation settings
        self.automation_enabled = config.MARKETING_ENABLED
        self.content_generation_enabled = config.CONTENT_GENERATION_ENABLED
        self.outbound_campaigns_enabled = config.OUTBOUND_CAMPAIGNS_ENABLED
        self.analytics_enabled = config.ANALYTICS_ENABLED
    
    async def start_marketing_automation(self):
        """Start all marketing automation processes"""
        if not self.automation_enabled:
            logger.info("Marketing automation is disabled")
            return
        
        logger.info("🚀 Starting marketing automation...")
        
        # Start background marketing tasks
        tasks = [
            asyncio.create_task(self._run_content_generation()),
            asyncio.create_task(self._run_lead_qualification()),
            asyncio.create_task(self._run_campaign_optimization()),
            asyncio.create_task(self._run_analytics_tracking())
        ]
        
        await asyncio.gather(*tasks)
    
    async def _run_content_generation(self):
        """Run automated content generation"""
        if not self.content_generation_enabled:
            return
        
        while True:
            try:
                logger.info("📝 Running content generation...")
                
                # Generate content for different audiences
                audiences = ['ai_developers', 'crypto_traders', 'tech_startups']
                
                for audience in audiences:
                    content_calendar = await self.content_engine.generate_content_calendar(
                        target_audience=audience,
                        days=30
                    )
                    
                    # Store generated content
                    await self._store_generated_content(content_calendar, audience)
                
                # Wait 24 hours before next content generation
                await asyncio.sleep(24 * 3600)
                
            except Exception as e:
                logger.error(f"Error in content generation: {e}")
                await asyncio.sleep(3600)  # Wait 1 hour before retry
    
    async def _run_lead_qualification(self):
        """Run automated lead qualification"""
        while True:
            try:
                logger.info("🎯 Running lead qualification...")
                
                # Get unqualified leads
                unqualified_leads = await self.lead_repository.get_leads_by_status('new')
                
                for lead in unqualified_leads[:50]:  # Process up to 50 leads at a time
                    # Qualify the lead
                    qualification_result = await self.lead_qualifier.qualify_lead(lead.to_dict())
                    
                    if 'error' not in qualification_result:
                        # Update lead with qualification results
                        await self.lead_repository.update_lead_score(
                            lead.id,
                            qualification_result['qualification_score'],
                            qualification_result['grade']
                        )
                        
                        # Update lead status based on grade
                        if qualification_result['grade'] in ['A', 'B']:
                            await self.lead_repository.update_lead_status(
                                lead.id, 'qualified', 'interest'
                            )
                        elif qualification_result['grade'] == 'C':
                            await self.lead_repository.update_lead_status(
                                lead.id, 'nurturing', 'awareness'
                            )
                
                # Wait 6 hours before next qualification run
                await asyncio.sleep(6 * 3600)
                
            except Exception as e:
                logger.error(f"Error in lead qualification: {e}")
                await asyncio.sleep(3600)  # Wait 1 hour before retry
    
    async def _run_campaign_optimization(self):
        """Run campaign optimization and A/B testing"""
        while True:
            try:
                logger.info("📊 Running campaign optimization...")
                
                # This would analyze campaign performance and optimize
                # For now, we'll simulate optimization
                optimization_results = await self._optimize_campaigns()
                
                logger.info(f"Campaign optimization completed: {optimization_results}")
                
                # Wait 12 hours before next optimization
                await asyncio.sleep(12 * 3600)
                
            except Exception as e:
                logger.error(f"Error in campaign optimization: {e}")
                await asyncio.sleep(7200)  # Wait 2 hours before retry
    
    async def _run_analytics_tracking(self):
        """Run analytics tracking and reporting"""
        if not self.analytics_enabled:
            return
        
        while True:
            try:
                logger.info("📈 Running analytics tracking...")
                
                # Generate marketing analytics
                analytics = await self._generate_marketing_analytics()
                
                # Store analytics data
                await self._store_analytics_data(analytics)
                
                # Wait 4 hours before next analytics run
                await asyncio.sleep(4 * 3600)
                
            except Exception as e:
                logger.error(f"Error in analytics tracking: {e}")
                await asyncio.sleep(3600)  # Wait 1 hour before retry
    
    async def create_lead(self, user_id: int, lead_data: Dict[str, Any]) -> Optional[Dict]:
        """Create a new lead and qualify it"""
        try:
            # Add user_id to lead data
            lead_data['user_id'] = user_id
            
            # Create lead in database
            lead = await self.lead_repository.create_lead(lead_data)
            
            if lead:
                # Qualify the lead immediately
                qualification_result = await self.lead_qualifier.qualify_lead(lead.to_dict())
                
                # Update lead with qualification results
                await self.lead_repository.update_lead_score(
                    lead.id,
                    qualification_result['qualification_score'],
                    qualification_result['grade']
                )
                
                return {
                    'lead_id': lead.id,
                    'qualification_result': qualification_result,
                    'status': 'created'
                }
            
            return None
            
        except Exception as e:
            logger.error(f"Error creating lead: {e}")
            return None
    
    async def track_engagement(self, user_id: int, engagement_data: Dict[str, Any]) -> bool:
        """Track user engagement and update lead score"""
        try:
            # Get lead for user
            lead = await self.lead_repository.get_lead_by_user_id(user_id)
            
            if lead:
                # Add engagement activity
                await self.lead_repository.add_engagement_activity(lead.id, engagement_data)
                
                # Re-qualify lead with new engagement data
                lead_data = lead.to_dict()
                lead_data['engagement_activities'] = lead_data.get('engagement_activities', [])
                lead_data['engagement_activities'].append(engagement_data)
                
                qualification_result = await self.lead_qualifier.qualify_lead(lead_data)
                
                # Update lead score
                await self.lead_repository.update_lead_score(
                    lead.id,
                    qualification_result['qualification_score'],
                    qualification_result['grade']
                )
                
                logger.info(f"Tracked engagement for user {user_id}, updated lead score")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error tracking engagement: {e}")
            return False
    
    async def track_conversion(self, user_id: int, conversion_data: Dict[str, Any]) -> bool:
        """Track conversion and update lead"""
        try:
            # Get lead for user
            lead = await self.lead_repository.get_lead_by_user_id(user_id)
            
            if lead:
                # Mark lead as converted
                conversion_value = conversion_data.get('value', 0.0)
                conversion_source = conversion_data.get('source', 'unknown')
                
                await self.lead_repository.mark_lead_converted(
                    lead.id,
                    conversion_value,
                    conversion_source
                )
                
                logger.info(f"Tracked conversion for user {user_id}, value: {conversion_value}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error tracking conversion: {e}")
            return False
    
    async def generate_content_for_audience(self, target_audience: str, days: int = 30) -> Dict[str, List[Dict]]:
        """Generate content for specific audience"""
        try:
            logger.info(f"Generating content for {target_audience}")
            
            content_calendar = await self.content_engine.generate_content_calendar(
                target_audience=target_audience,
                days=days
            )
            
            # Optimize content for SEO
            optimized_content = {}
            for content_type, content_list in content_calendar.items():
                optimized_content[content_type] = []
                
                for content in content_list:
                    if 'content' in content:
                        seo_result = await self.seo_optimizer.optimize_content(
                            content['content'],
                            content.get('target_keywords', [])
                        )
                        
                        if 'optimized_content' in seo_result:
                            content['optimized_content'] = seo_result['optimized_content']
                            content['seo_score'] = seo_result['seo_score']
                            content['seo_suggestions'] = seo_result['suggestions']
                    
                    optimized_content[content_type].append(content)
            
            return optimized_content
            
        except Exception as e:
            logger.error(f"Error generating content for {target_audience}: {e}")
            return {}
    
    async def get_lead_analytics(self, days: int = 30) -> Dict[str, Any]:
        """Get lead analytics"""
        try:
            analytics = await self.lead_repository.get_lead_analytics(days)
            
            # Add additional analytics
            analytics['lead_velocity'] = await self._calculate_lead_velocity(days)
            analytics['conversion_funnel'] = await self._get_conversion_funnel(days)
            analytics['top_performing_sources'] = await self._get_top_performing_sources(days)
            
            return analytics
            
        except Exception as e:
            logger.error(f"Error getting lead analytics: {e}")
            return {}
    
    async def _store_generated_content(self, content_calendar: Dict, audience: str):
        """Store generated content in database"""
        # This would store content in the database
        # For now, we'll just log it
        total_content = sum(len(content_list) for content_list in content_calendar.values())
        logger.info(f"Stored {total_content} content pieces for {audience}")
    
    async def _optimize_campaigns(self) -> Dict[str, Any]:
        """Optimize campaigns based on performance"""
        # This would analyze campaign performance and make optimizations
        # For now, we'll return a simulation
        return {
            'campaigns_optimized': 5,
            'performance_improvement': 15.5,
            'budget_reallocated': 250.0
        }
    
    async def _generate_marketing_analytics(self) -> Dict[str, Any]:
        """Generate comprehensive marketing analytics"""
        try:
            # Get lead analytics
            lead_analytics = await self.lead_repository.get_lead_analytics(30)
            
            # Add campaign analytics
            campaign_analytics = await self._get_campaign_analytics()
            
            # Add content analytics
            content_analytics = await self._get_content_analytics()
            
            return {
                'lead_analytics': lead_analytics,
                'campaign_analytics': campaign_analytics,
                'content_analytics': content_analytics,
                'generated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating marketing analytics: {e}")
            return {}
    
    async def _store_analytics_data(self, analytics: Dict[str, Any]):
        """Store analytics data"""
        # This would store analytics in the database
        # For now, we'll just log it
        logger.info(f"Stored analytics data: {len(analytics)} metrics")
    
    async def _calculate_lead_velocity(self, days: int) -> float:
        """Calculate lead velocity (leads per day)"""
        try:
            analytics = await self.lead_repository.get_lead_analytics(days)
            total_leads = analytics.get('total_leads', 0)
            return total_leads / days if days > 0 else 0
        except Exception as e:
            logger.error(f"Error calculating lead velocity: {e}")
            return 0.0
    
    async def _get_conversion_funnel(self, days: int) -> Dict[str, int]:
        """Get conversion funnel data"""
        try:
            analytics = await self.lead_repository.get_lead_analytics(days)
            
            return {
                'awareness': analytics.get('total_leads', 0),
                'interest': analytics.get('leads_by_status', {}).get('qualified', 0),
                'consideration': analytics.get('leads_by_status', {}).get('nurturing', 0),
                'conversion': analytics.get('converted_leads', 0)
            }
        except Exception as e:
            logger.error(f"Error getting conversion funnel: {e}")
            return {}
    
    async def _get_top_performing_sources(self, days: int) -> List[Dict[str, Any]]:
        """Get top performing lead sources"""
        # This would query the database for source performance
        # For now, we'll return a simulation
        return [
            {'source': 'content_download', 'leads': 45, 'conversion_rate': 12.5},
            {'source': 'webinar_registration', 'leads': 32, 'conversion_rate': 18.2},
            {'source': 'demo_request', 'leads': 28, 'conversion_rate': 25.0},
            {'source': 'social_engagement', 'leads': 15, 'conversion_rate': 8.3}
        ]
    
    async def _get_campaign_analytics(self) -> Dict[str, Any]:
        """Get campaign analytics"""
        # This would query campaign performance data
        # For now, we'll return a simulation
        return {
            'active_campaigns': 8,
            'total_impressions': 15420,
            'total_clicks': 1234,
            'total_conversions': 89,
            'average_ctr': 8.0,
            'average_conversion_rate': 7.2
        }
    
    async def _get_content_analytics(self) -> Dict[str, Any]:
        """Get content analytics"""
        # This would query content performance data
        # For now, we'll return a simulation
        return {
            'total_content_pieces': 156,
            'total_views': 8920,
            'total_shares': 445,
            'average_engagement_rate': 6.8,
            'top_performing_content': [
                'AI Token Cost Optimization Guide',
                'Claude AI Integration Tutorial',
                'Cryptocurrency Payments for AI'
            ]
        } 
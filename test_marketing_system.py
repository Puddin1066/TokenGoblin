#!/usr/bin/env python3
"""
Test script for the TokenGoblin Marketing System
Demonstrates the comprehensive marketing implementation
"""

import asyncio
import logging
from datetime import datetime
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# Import marketing components
from marketing.inbound.content_engine import ContentGenerationEngine
from marketing.inbound.seo_optimizer import SEOOptimizer
from marketing.inbound.lead_qualifier import LeadQualificationEngine
from services.marketing.marketing_orchestrator import MarketingOrchestrator
from repositories.marketing.lead_repository import LeadRepository

# Import models
from models.marketing.lead import Lead
from models.marketing.campaign import Campaign
from models.marketing.content import Content
from models.marketing.engagement import Engagement

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_content_generation():
    """Test AI content generation"""
    logger.info("🧪 Testing Content Generation Engine")
    
    content_engine = ContentGenerationEngine()
    
    # Test content generation for different audiences
    audiences = ['ai_developers', 'crypto_traders']
    
    for audience in audiences:
        logger.info(f"Generating content for {audience}")
        
        try:
            content_calendar = await content_engine.generate_content_calendar(
                target_audience=audience,
                days=7  # Generate 1 week of content
            )
            
            logger.info(f"✅ Generated content for {audience}:")
            for content_type, content_list in content_calendar.items():
                logger.info(f"  - {content_type}: {len(content_list)} pieces")
                
                # Show first content piece as example
                if content_list:
                    first_content = content_list[0]
                    logger.info(f"    Example: {first_content.get('title', 'Untitled')}")
                    logger.info(f"    SEO Score: {first_content.get('seo_score', 'N/A')}")
                    logger.info(f"    Readability: {first_content.get('readability_score', 'N/A')}")
            
        except Exception as e:
            logger.error(f"❌ Error generating content for {audience}: {e}")


async def test_seo_optimization():
    """Test SEO optimization"""
    logger.info("🧪 Testing SEO Optimization Engine")
    
    seo_optimizer = SEOOptimizer()
    
    # Test content
    test_content = """
    AI tokens are becoming increasingly popular for developers who want to optimize their costs.
    OpenRouter provides access to various AI models including Claude AI.
    Cryptocurrency payments make it easy to purchase tokens without traditional banking.
    """
    
    try:
        # Test content optimization
        optimization_result = await seo_optimizer.optimize_content(test_content)
        
        if 'error' not in optimization_result:
            logger.info("✅ SEO Optimization Results:")
            logger.info(f"  - Original SEO Score: {optimization_result.get('readability_score', 'N/A')}")
            logger.info(f"  - Final SEO Score: {optimization_result.get('seo_score', 'N/A')}")
            logger.info(f"  - Improvement: {optimization_result.get('improvement_percentage', 'N/A')}%")
            logger.info(f"  - Suggestions: {len(optimization_result.get('suggestions', []))}")
            
            # Show optimization suggestions
            suggestions = optimization_result.get('suggestions', [])
            if suggestions:
                logger.info("  - Top suggestions:")
                for i, suggestion in enumerate(suggestions[:3], 1):
                    logger.info(f"    {i}. {suggestion}")
        else:
            logger.error(f"❌ SEO optimization failed: {optimization_result['error']}")
            
    except Exception as e:
        logger.error(f"❌ Error in SEO optimization: {e}")


async def test_lead_qualification():
    """Test lead qualification"""
    logger.info("🧪 Testing Lead Qualification Engine")
    
    lead_qualifier = LeadQualificationEngine()
    
    # Test lead data
    test_lead_data = {
        'id': 1,
        'user_id': 123456,
        'engagement_activities': [
            {'type': 'page_view', 'timestamp': datetime.now().isoformat()},
            {'type': 'content_download', 'timestamp': datetime.now().isoformat()},
            {'type': 'demo_request', 'timestamp': datetime.now().isoformat()}
        ],
        'intent_signals': [
            {'type': 'pricing_check', 'value': 'high'},
            {'type': 'feature_research', 'value': 'claude_ai'}
        ],
        'budget_indicator': 1500.0,
        'authority_level': 'decision_maker',
        'timeline_days': 15,
        'source': 'demo_request',
        'region': 'en'
    }
    
    try:
        qualification_result = await lead_qualifier.qualify_lead(test_lead_data)
        
        if 'error' not in qualification_result:
            logger.info("✅ Lead Qualification Results:")
            logger.info(f"  - Qualification Score: {qualification_result['qualification_score']:.2f}")
            logger.info(f"  - Lead Grade: {qualification_result['grade']}")
            logger.info(f"  - Estimated Value: ${qualification_result['estimated_value']:.2f}")
            logger.info(f"  - Recommendations: {len(qualification_result['recommendations'])}")
            logger.info(f"  - Next Actions: {len(qualification_result['next_actions'])}")
            
            # Show recommendations
            recommendations = qualification_result.get('recommendations', [])
            if recommendations:
                logger.info("  - Top recommendations:")
                for i, rec in enumerate(recommendations[:3], 1):
                    logger.info(f"    {i}. {rec}")
            
            # Show risk and opportunity factors
            risk_factors = qualification_result.get('risk_factors', [])
            opportunity_factors = qualification_result.get('opportunity_factors', [])
            
            if risk_factors:
                logger.info(f"  - Risk Factors: {len(risk_factors)}")
                for factor in risk_factors[:2]:
                    logger.info(f"    • {factor}")
            
            if opportunity_factors:
                logger.info(f"  - Opportunity Factors: {len(opportunity_factors)}")
                for factor in opportunity_factors[:2]:
                    logger.info(f"    • {factor}")
        else:
            logger.error(f"❌ Lead qualification failed: {qualification_result['error']}")
            
    except Exception as e:
        logger.error(f"❌ Error in lead qualification: {e}")


async def test_marketing_orchestrator():
    """Test marketing orchestrator"""
    logger.info("🧪 Testing Marketing Orchestrator")
    
    # Create async engine and session
    engine = create_async_engine("sqlite+aiosqlite:///test_marketing.db")
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        # Create tables
        async with engine.begin() as conn:
            await conn.run_sync(Lead.metadata.create_all)
            await conn.run_sync(Campaign.metadata.create_all)
            await conn.run_sync(Content.metadata.create_all)
            await conn.run_sync(Engagement.metadata.create_all)
        
        marketing_orchestrator = MarketingOrchestrator(session)
        
        try:
            # Test lead creation
            lead_data = {
                'email': 'test@example.com',
                'first_name': 'John',
                'last_name': 'Doe',
                'source': 'demo_request',
                'region': 'en',
                'authority_level': 'decision_maker',
                'budget_indicator': 2000.0,
                'timeline_days': 30
            }
            
            lead_result = await marketing_orchestrator.create_lead(123456, lead_data)
            
            if lead_result:
                logger.info("✅ Lead Creation Results:")
                logger.info(f"  - Lead ID: {lead_result['lead_id']}")
                logger.info(f"  - Status: {lead_result['status']}")
                
                qualification = lead_result['qualification_result']
                logger.info(f"  - Qualification Score: {qualification['qualification_score']:.2f}")
                logger.info(f"  - Grade: {qualification['grade']}")
                logger.info(f"  - Estimated Value: ${qualification['estimated_value']:.2f}")
            
            # Test engagement tracking
            engagement_data = {
                'type': 'content_view',
                'content_id': 1,
                'duration_seconds': 120,
                'engagement_score': 8.5
            }
            
            engagement_result = await marketing_orchestrator.track_engagement(123456, engagement_data)
            logger.info(f"✅ Engagement Tracking: {'Success' if engagement_result else 'Failed'}")
            
            # Test content generation
            content_result = await marketing_orchestrator.generate_content_for_audience(
                'ai_developers', days=3
            )
            
            if content_result:
                logger.info("✅ Content Generation Results:")
                total_content = sum(len(content_list) for content_list in content_result.values())
                logger.info(f"  - Total Content Pieces: {total_content}")
                
                for content_type, content_list in content_result.items():
                    logger.info(f"  - {content_type}: {len(content_list)} pieces")
            
            # Test analytics
            analytics = await marketing_orchestrator.get_lead_analytics(days=30)
            
            if analytics:
                logger.info("✅ Analytics Results:")
                logger.info(f"  - Total Leads: {analytics.get('total_leads', 0)}")
                logger.info(f"  - Conversion Rate: {analytics.get('conversion_rate', 0):.1f}%")
                logger.info(f"  - Lead Velocity: {analytics.get('lead_velocity', 0):.1f} leads/day")
                
                conversion_funnel = analytics.get('conversion_funnel', {})
                if conversion_funnel:
                    logger.info("  - Conversion Funnel:")
                    for stage, count in conversion_funnel.items():
                        logger.info(f"    • {stage}: {count}")
            
        except Exception as e:
            logger.error(f"❌ Error in marketing orchestrator test: {e}")
        
        finally:
            await engine.dispose()


async def test_behavioral_scoring():
    """Test behavioral scoring"""
    logger.info("🧪 Testing Behavioral Scoring")
    
    lead_qualifier = LeadQualificationEngine()
    
    # Test user behavior data
    user_behavior = {
        'page_views': 15,
        'time_spent': 1800,  # 30 minutes
        'cart_adds': 3,
        'purchase_history': ['token_package_1', 'token_package_2'],
        'social_shares': 2
    }
    
    try:
        behavioral_score = await lead_qualifier.calculate_behavioral_score(user_behavior)
        
        logger.info("✅ Behavioral Scoring Results:")
        logger.info(f"  - Behavioral Score: {behavioral_score:.2f}")
        logger.info(f"  - Score Category: {lead_qualifier._get_engagement_category(behavioral_score)}")
        
        # Test with different behavior patterns
        low_engagement = {
            'page_views': 2,
            'time_spent': 60,
            'cart_adds': 0,
            'purchase_history': [],
            'social_shares': 0
        }
        
        high_engagement = {
            'page_views': 25,
            'time_spent': 3600,
            'cart_adds': 5,
            'purchase_history': ['premium_package'],
            'social_shares': 5
        }
        
        low_score = await lead_qualifier.calculate_behavioral_score(low_engagement)
        high_score = await lead_qualifier.calculate_behavioral_score(high_engagement)
        
        logger.info(f"  - Low Engagement Score: {low_score:.2f}")
        logger.info(f"  - High Engagement Score: {high_score:.2f}")
        
    except Exception as e:
        logger.error(f"❌ Error in behavioral scoring: {e}")


async def main():
    """Run all marketing system tests"""
    logger.info("🚀 Starting TokenGoblin Marketing System Tests")
    logger.info("=" * 60)
    
    # Run tests
    await test_content_generation()
    logger.info("-" * 40)
    
    await test_seo_optimization()
    logger.info("-" * 40)
    
    await test_lead_qualification()
    logger.info("-" * 40)
    
    await test_behavioral_scoring()
    logger.info("-" * 40)
    
    await test_marketing_orchestrator()
    logger.info("-" * 40)
    
    logger.info("✅ All marketing system tests completed!")
    logger.info("=" * 60)


if __name__ == "__main__":
    asyncio.run(main()) 
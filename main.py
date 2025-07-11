"""
Main application entry point for Automated Telegram Marketing System
"""
import asyncio
import logging
import sys
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI, Request, status, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger

from config import config
from services.telegram_crawler import TelegramCrawler
from services.ai_sales_agent import AISalesAgent
from services.dynamic_pricing import DynamicPricingEngine
from services.payment_processor import PaymentProcessor
from services.conversation_manager import ConversationManager
from services.marketing_automation import MarketingAutomationEngine
from services.database import DatabaseService
from services.analytics import AnalyticsService
from api.routes import api_router
from utils.logging_config import setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Global service instances
telegram_crawler = None
ai_sales_agent = None
pricing_engine = None
payment_processor = None
conversation_manager = None
marketing_automation = None
db_service = None
analytics_service = None
scheduler = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    # Startup
    logger.info("Starting Automated Telegram Marketing System...")
    
    # Validate configuration
    missing_keys = config.validate_required_keys()
    if missing_keys:
        logger.error(f"Missing required configuration keys: {missing_keys}")
        logger.error("Please check your .env file and ensure all required API keys are set")
        sys.exit(1)
    
    # Initialize services
    await initialize_services()
    
    # Start automation
    await start_automation()
    
    logger.info("✅ Automated Telegram Marketing System started successfully!")
    logger.info(f"🎯 Daily revenue target: ${config.monitoring.daily_revenue_target}")
    logger.info(f"📊 System ready to generate automated sales 24/7")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Automated Telegram Marketing System...")
    await shutdown_services()
    logger.info("✅ Shutdown complete")


async def initialize_services():
    """Initialize all services"""
    global telegram_crawler, ai_sales_agent, pricing_engine, payment_processor
    global conversation_manager, marketing_automation, db_service, analytics_service
    
    try:
        # Initialize database service first
        db_service = DatabaseService()
        await db_service.initialize()
        logger.info("✅ Database service initialized")
        
        # Initialize core services
        if config.features.enable_telegram_crawler:
            telegram_crawler = TelegramCrawler()
            await telegram_crawler.start()
            logger.info("✅ Telegram crawler initialized")
        
        if config.features.enable_ai_sales_agent:
            ai_sales_agent = AISalesAgent()
            logger.info("✅ AI sales agent initialized")
        
        if config.features.enable_dynamic_pricing:
            pricing_engine = DynamicPricingEngine()
            logger.info("✅ Dynamic pricing engine initialized")
        
        if config.features.enable_payment_processing:
            payment_processor = PaymentProcessor()
            logger.info("✅ Payment processor initialized")
        
        # Initialize conversation manager
        conversation_manager = ConversationManager(
            ai_agent=ai_sales_agent,
            pricing_engine=pricing_engine,
            payment_processor=payment_processor,
            db_service=db_service
        )
        logger.info("✅ Conversation manager initialized")
        
        # Initialize marketing automation
        if config.features.enable_automation:
            marketing_automation = MarketingAutomationEngine(
                telegram_crawler=telegram_crawler,
                ai_agent=ai_sales_agent,
                conversation_manager=conversation_manager,
                db_service=db_service
            )
            logger.info("✅ Marketing automation initialized")
        
        # Initialize analytics
        if config.features.enable_analytics:
            analytics_service = AnalyticsService(db_service=db_service)
            logger.info("✅ Analytics service initialized")
        
    except Exception as e:
        logger.error(f"❌ Error initializing services: {e}")
        raise


async def start_automation():
    """Start automated marketing workflows"""
    global scheduler
    
    if not config.features.enable_automation:
        logger.info("🚫 Automation disabled in configuration")
        return
    
    try:
        scheduler = AsyncIOScheduler()
        
        # Lead generation every 2 hours
        scheduler.add_job(
            run_lead_generation,
            IntervalTrigger(hours=2),
            id='lead_generation',
            name='Automated Lead Generation'
        )
        
        # Process conversations every 15 minutes
        scheduler.add_job(
            process_conversations,
            IntervalTrigger(minutes=15),
            id='conversation_processing',
            name='Conversation Processing'
        )
        
        # Follow-up sequences every hour
        scheduler.add_job(
            run_follow_up_sequences,
            IntervalTrigger(hours=1),
            id='follow_up_sequences',
            name='Follow-up Sequences'
        )
        
        # Daily analytics and optimization
        scheduler.add_job(
            run_daily_analytics,
            CronTrigger(hour=9, minute=0),
            id='daily_analytics',
            name='Daily Analytics'
        )
        
        # Hourly performance check
        scheduler.add_job(
            check_performance_targets,
            IntervalTrigger(hours=1),
            id='performance_check',
            name='Performance Check'
        )
        
        scheduler.start()
        logger.info("🚀 Automation scheduler started")
        
    except Exception as e:
        logger.error(f"❌ Error starting automation: {e}")
        raise


async def run_lead_generation():
    """Run automated lead generation"""
    try:
        logger.info("🔍 Starting lead generation cycle...")
        
        if not telegram_crawler:
            logger.warning("Telegram crawler not available")
            return
        
        # Crawl for new prospects
        prospects = await telegram_crawler.crawl_groups()
        
        if prospects:
            # Save prospects to database
            saved_count = await telegram_crawler.save_prospects(prospects)
            logger.info(f"✅ Lead generation complete: {saved_count} new prospects saved")
            
            # Start conversations with high-quality prospects
            await start_conversations_with_prospects(prospects)
        else:
            logger.info("No new prospects found in this cycle")
            
    except Exception as e:
        logger.error(f"❌ Error in lead generation: {e}")


async def start_conversations_with_prospects(prospects):
    """Start conversations with qualified prospects"""
    try:
        if not conversation_manager:
            return
        
        # Filter for high-quality prospects
        qualified_prospects = [p for p in prospects if p.qualification_score >= config.marketing.min_qualification_score]
        
        # Limit to prevent overwhelming
        qualified_prospects = qualified_prospects[:config.marketing.conversation_limit]
        
        for prospect in qualified_prospects:
            try:
                await conversation_manager.start_conversation(prospect)
                logger.info(f"💬 Started conversation with {prospect.username or prospect.telegram_id}")
                
                # Delay between conversations
                await asyncio.sleep(30)
                
            except Exception as e:
                logger.error(f"Error starting conversation with {prospect.telegram_id}: {e}")
                
    except Exception as e:
        logger.error(f"❌ Error starting conversations: {e}")


async def process_conversations():
    """Process active conversations"""
    try:
        if not conversation_manager:
            return
        
        # Get active conversations
        active_conversations = await conversation_manager.get_active_conversations()
        
        logger.info(f"📞 Processing {len(active_conversations)} active conversations")
        
        for conversation in active_conversations:
            try:
                await conversation_manager.process_conversation(conversation)
                
                # Small delay between processing
                await asyncio.sleep(5)
                
            except Exception as e:
                logger.error(f"Error processing conversation {conversation['id']}: {e}")
                
    except Exception as e:
        logger.error(f"❌ Error processing conversations: {e}")


async def run_follow_up_sequences():
    """Run follow-up sequences"""
    try:
        if not marketing_automation:
            return
        
        logger.info("📧 Running follow-up sequences...")
        
        await marketing_automation.run_follow_up_sequences()
        
    except Exception as e:
        logger.error(f"❌ Error in follow-up sequences: {e}")


async def run_daily_analytics():
    """Run daily analytics and optimization"""
    try:
        if not analytics_service:
            return
        
        logger.info("📊 Running daily analytics...")
        
        # Generate daily report
        daily_report = await analytics_service.generate_daily_report()
        
        # Check if we're meeting targets
        daily_revenue = daily_report.get('revenue', 0)
        target_revenue = config.monitoring.daily_revenue_target
        
        if daily_revenue >= target_revenue:
            logger.info(f"🎉 Daily revenue target achieved: ${daily_revenue:.2f} (target: ${target_revenue:.2f})")
        else:
            logger.warning(f"⚠️ Daily revenue below target: ${daily_revenue:.2f} (target: ${target_revenue:.2f})")
            
            # Trigger optimization if needed
            await trigger_optimization()
        
        # Send daily report to admins
        await send_daily_report(daily_report)
        
    except Exception as e:
        logger.error(f"❌ Error in daily analytics: {e}")


async def check_performance_targets():
    """Check if we're meeting performance targets"""
    try:
        if not analytics_service:
            return
        
        # Get current performance metrics
        metrics = await analytics_service.get_realtime_metrics()
        
        # Check revenue target
        current_revenue = metrics.get('daily_revenue', 0)
        target_revenue = config.monitoring.daily_revenue_target
        
        # Calculate progress
        progress = (current_revenue / target_revenue) * 100 if target_revenue > 0 else 0
        
        logger.info(f"📈 Revenue progress: ${current_revenue:.2f} / ${target_revenue:.2f} ({progress:.1f}%)")
        
        # Alert if significantly behind
        if progress < 50 and metrics.get('hours_into_day', 0) > 12:
            logger.warning(f"⚠️ Revenue significantly behind target. Triggering optimization...")
            await trigger_optimization()
        
    except Exception as e:
        logger.error(f"❌ Error checking performance targets: {e}")


async def trigger_optimization():
    """Trigger optimization processes"""
    try:
        logger.info("🔧 Triggering optimization processes...")
        
        if marketing_automation:
            await marketing_automation.optimize_performance()
        
        if pricing_engine:
            await pricing_engine.optimize_pricing()
        
        logger.info("✅ Optimization processes triggered")
        
    except Exception as e:
        logger.error(f"❌ Error in optimization: {e}")


async def send_daily_report(report):
    """Send daily report to admins"""
    try:
        # Implementation would send report via Telegram or email
        logger.info("📧 Daily report sent to admins")
        
    except Exception as e:
        logger.error(f"❌ Error sending daily report: {e}")


async def shutdown_services():
    """Shutdown all services"""
    global scheduler
    
    try:
        if scheduler:
            scheduler.shutdown()
            logger.info("✅ Scheduler shutdown")
        
        if telegram_crawler:
            await telegram_crawler.stop()
            logger.info("✅ Telegram crawler stopped")
        
        if db_service:
            await db_service.close()
            logger.info("✅ Database service closed")
        
    except Exception as e:
        logger.error(f"❌ Error during shutdown: {e}")


# Create FastAPI app
app = FastAPI(
    title=config.system.app_name,
    version=config.system.app_version,
    description="Automated Telegram Marketing System for OpenRouter API Token Sales",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api")

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": config.system.app_version,
        "services": {
            "telegram_crawler": telegram_crawler is not None,
            "ai_sales_agent": ai_sales_agent is not None,
            "pricing_engine": pricing_engine is not None,
            "payment_processor": payment_processor is not None,
            "conversation_manager": conversation_manager is not None,
            "marketing_automation": marketing_automation is not None,
            "analytics_service": analytics_service is not None
        }
    }

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": str(exc)}
    )

# Metrics endpoint
@app.get("/metrics")
async def get_metrics():
    """Get system metrics"""
    try:
        if analytics_service:
            metrics = await analytics_service.get_realtime_metrics()
            return metrics
        else:
            return {"error": "Analytics service not available"}
    except Exception as e:
        logger.error(f"Error getting metrics: {e}")
        return {"error": str(e)}

# Status endpoint
@app.get("/status")
async def get_status():
    """Get system status"""
    return {
        "system": config.system.app_name,
        "version": config.system.app_version,
        "uptime": "Active",
        "features": {
            "telegram_crawler": config.features.enable_telegram_crawler,
            "ai_sales_agent": config.features.enable_ai_sales_agent,
            "dynamic_pricing": config.features.enable_dynamic_pricing,
            "payment_processing": config.features.enable_payment_processing,
            "analytics": config.features.enable_analytics,
            "automation": config.features.enable_automation
        },
        "targets": {
            "daily_revenue": config.monitoring.daily_revenue_target,
            "monthly_revenue": config.monitoring.monthly_revenue_target
        }
    }


def main():
    """Main entry point"""
    logger.info(f"Starting {config.system.app_name} v{config.system.app_version}")
    logger.info(f"Environment: {'Development' if config.system.debug else 'Production'}")
    
    uvicorn.run(
        "main:app",
        host=config.system.host,
        port=config.system.port,
        reload=config.system.debug,
        log_level=config.system.log_level.lower(),
        workers=1  # Must be 1 for background tasks to work properly
    )


if __name__ == "__main__":
    main()
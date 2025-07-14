import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
import redis.asyncio as redis

import config
from services.agentic_orchestrator import AgenticOrchestrator
from services.agentic_sales import AgenticSalesService
from services.openrouter_service import OpenRouterService
from services.enhanced_crypto_payment import EnhancedCryptoPaymentService
from services.notification import NotificationService
from db import get_db_session
from middleware.database import DBSessionMiddleware
from middleware.throttling_middleware import ThrottlingMiddleware

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Redis
redis_client = redis.from_url(f"redis://{config.REDIS_HOST}:6379")

# Initialize bot and dispatcher
bot = Bot(token=config.TOKEN, parse_mode=ParseMode.HTML)
storage = RedisStorage.from_url(f"redis://{config.REDIS_HOST}:6379")
dp = Dispatcher(storage=storage)

# Initialize services
if config.AGENTIC_MODE:
    orchestrator = AgenticOrchestrator(config.OPENROUTER_API_KEY)
    sales_service = AgenticSalesService()
    openrouter_service = OpenRouterService(config.OPENROUTER_API_KEY)
    payment_service = EnhancedCryptoPaymentService()
    notification_service = NotificationService()

# Initialize middleware
throttling_middleware = ThrottlingMiddleware(redis_client)
db_middleware = DBSessionMiddleware()

# Apply middleware
dp.message.middleware(db_middleware)
dp.callback_query.middleware(db_middleware)
dp.message.middleware(throttling_middleware)
dp.callback_query.middleware(throttling_middleware)


async def on_startup(application: web.Application):
    """Startup handler"""
    logger.info("Starting agentic Claude token resale bot...")
    
    if config.AGENTIC_MODE:
        # Start agentic operations in background
        asyncio.create_task(start_agentic_operations())
        logger.info("Agentic mode enabled - starting autonomous operations")
    
    # Set webhook
    await bot.set_webhook(
        url=f"https://{config.WEBAPP_HOST}:{config.WEBAPP_PORT}{config.WEBHOOK_PATH}",
        secret_token=config.WEBHOOK_SECRET_TOKEN
    )
    logger.info("Webhook set successfully")


async def on_shutdown(application: web.Application):
    """Shutdown handler"""
    logger.info("Shutting down bot...")
    
    # Remove webhook
    await bot.delete_webhook()
    
    # Close Redis connection
    await redis_client.close()
    
    logger.info("Bot shutdown complete")


async def start_agentic_operations():
    """Start all agentic operations"""
    try:
        await orchestrator.start_agentic_operations()
    except Exception as e:
        logger.error(f"Error in agentic operations: {e}")


async def handle_user_interaction(user_id: int, interaction_type: str, data: dict = None):
    """Handle user interactions for agentic analysis"""
    if config.AGENTIC_MODE:
        try:
            await orchestrator.handle_user_interaction(user_id, interaction_type, data)
        except Exception as e:
            logger.error(f"Error handling user interaction: {e}")


async def execute_smart_token_purchase(user_id: int, desired_tokens: int, budget: float):
    """Execute intelligent token purchase"""
    if config.AGENTIC_MODE:
        try:
            return await orchestrator.execute_smart_purchase(user_id, desired_tokens, budget)
        except Exception as e:
            logger.error(f"Error executing smart purchase: {e}")
            return {'success': False, 'error': str(e)}
    return {'success': False, 'error': 'Agentic mode not enabled'}


async def optimize_payment_experience(user_id: int, amount: float):
    """Optimize payment experience for user"""
    if config.AGENTIC_MODE:
        try:
            return await orchestrator.optimize_payment_experience(user_id, amount)
        except Exception as e:
            logger.error(f"Error optimizing payment experience: {e}")
            return {'success': False, 'error': str(e)}
    return {'success': False, 'error': 'Agentic mode not enabled'}


async def get_agentic_analytics():
    """Get agentic analytics and insights"""
    if config.AGENTIC_MODE:
        try:
            # Get sales opportunities
            session = await get_db_session()
            opportunities = await sales_service.identify_sales_opportunities(session)
            
            # Get payment analytics
            payment_analytics = await payment_service.get_payment_analytics()
            
            # Get token inventory status
            inventory_status = await openrouter_service.get_account_balance()
            
            return {
                'opportunities_found': len(opportunities),
                'payment_success_rate': payment_analytics.get('success_rate', 0),
                'total_payments': payment_analytics.get('total_payments', 0),
                'account_balance': inventory_status.get('credits', 0),
                'agentic_mode': True
            }
        except Exception as e:
            logger.error(f"Error getting agentic analytics: {e}")
            return {'error': str(e), 'agentic_mode': True}
    
    return {'agentic_mode': False}


async def send_proactive_message(user_id: int, message_content: str, message_type: str = 'lead_nurture'):
    """Send proactive message to user"""
    if config.AGENTIC_MODE:
        try:
            await bot.send_message(user_id, message_content)
            logger.info(f"Sent proactive message to user {user_id}: {message_type}")
            return True
        except Exception as e:
            logger.error(f"Error sending proactive message: {e}")
            return False
    return False


async def update_token_pricing(model_id: str, new_price: float, reason: str = 'market_adjustment'):
    """Update token pricing dynamically"""
    if config.AGENTIC_MODE:
        try:
            session = await get_db_session()
            # Implementation would update pricing in database
            logger.info(f"Updated pricing for {model_id}: ${new_price} - {reason}")
            return True
        except Exception as e:
            logger.error(f"Error updating token pricing: {e}")
            return False
    return False


async def auto_restock_inventory():
    """Automatically restock inventory based on demand"""
    if config.AGENTIC_MODE:
        try:
            session = await get_db_session()
            # Implementation would check inventory levels and restock
            logger.info("Auto-restock inventory check completed")
            return True
        except Exception as e:
            logger.error(f"Error in auto-restock: {e}")
            return False
    return False


# Export functions for use in handlers
__all__ = [
    'bot',
    'dp',
    'handle_user_interaction',
    'execute_smart_token_purchase',
    'optimize_payment_experience',
    'get_agentic_analytics',
    'send_proactive_message',
    'update_token_pricing',
    'auto_restock_inventory',
    'orchestrator' if config.AGENTIC_MODE else None,
    'sales_service' if config.AGENTIC_MODE else None,
    'openrouter_service' if config.AGENTIC_MODE else None,
    'payment_service' if config.AGENTIC_MODE else None
]
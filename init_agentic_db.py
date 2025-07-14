#!/usr/bin/env python3
"""
Database initialization script for the Agentic Claude Token Resale Bot
"""

import asyncio
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

import config
from models.base import Base
from models.token_inventory import TokenInventory, TokenPurchase, TokenUsage, PricingHistory
from models.user_behavior import UserBehavior, LeadScore, SalesOpportunity, ProactiveMessage
from models.user import User
from models.item import Item
from models.category import Category
from models.subcategory import Subcategory
from models.buy import Buy
from models.buyItem import BuyItem
from models.cart import Cart
from models.cartItem import CartItem
from models.deposit import Deposit
from models.payment import Payment
from models.withdrawal import Withdrawal

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def init_database():
    """Initialize the database with all tables"""
    try:
        # Create async engine
        if config.DB_ENCRYPTION:
            # For encrypted database
            engine = create_async_engine(
                f"sqlite+aiosqlite:///{config.DB_NAME}",
                echo=True
            )
        else:
            # For regular database
            engine = create_async_engine(
                f"sqlite+aiosqlite:///{config.DB_NAME}",
                echo=True
            )
        
        # Create all tables
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
        logger.info("✅ Database tables created successfully")
        
        # Initialize with sample data
        await initialize_sample_data(engine)
        
        logger.info("✅ Sample data initialized successfully")
        
    except Exception as e:
        logger.error(f"❌ Error initializing database: {e}")
        raise


async def initialize_sample_data(engine):
    """Initialize database with sample data"""
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        # Create sample Claude token inventories
        sample_inventories = [
            TokenInventory(
                model_id="anthropic/claude-3-sonnet",
                model_name="Claude 3 Sonnet",
                tokens_available=10000,
                tokens_reserved=0,
                unit_price_usd=0.015,
                cost_per_token=0.012,
                markup_percentage=0.25,
                is_active=True
            ),
            TokenInventory(
                model_id="anthropic/claude-3-opus",
                model_name="Claude 3 Opus",
                tokens_available=5000,
                tokens_reserved=0,
                unit_price_usd=0.015,
                cost_per_token=0.012,
                markup_percentage=0.25,
                is_active=True
            ),
            TokenInventory(
                model_id="anthropic/claude-3-haiku",
                model_name="Claude 3 Haiku",
                tokens_available=20000,
                tokens_reserved=0,
                unit_price_usd=0.00025,
                cost_per_token=0.0002,
                markup_percentage=0.25,
                is_active=True
            )
        ]
        
        for inventory in sample_inventories:
            session.add(inventory)
        
        # Create sample categories and items
        sample_category = Category(name="Claude AI Tokens")
        session.add(sample_category)
        await session.flush()
        
        sample_subcategory = Subcategory(
            name="Claude 3 Sonnet",
            category_id=sample_category.id
        )
        session.add(sample_subcategory)
        await session.flush()
        
        sample_item = Item(
            category_id=sample_category.id,
            subcategory_id=sample_subcategory.id,
            description="Claude 3 Sonnet - 1000 tokens",
            private_data="Your Claude 3 Sonnet tokens will be delivered instantly",
            price=15.0,
            is_sold=False,
            is_new=True
        )
        session.add(sample_item)
        
        await session.commit()
        logger.info("✅ Sample token inventories and items created")


async def verify_database():
    """Verify that all tables exist and are accessible"""
    try:
        engine = create_async_engine(f"sqlite+aiosqlite:///{config.DB_NAME}")
        
        async with engine.begin() as conn:
            # Check if tables exist
            result = await conn.execute(text("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name IN (
                    'token_inventory', 'token_purchases', 'token_usage', 
                    'pricing_history', 'user_behavior', 'lead_scores',
                    'sales_opportunities', 'proactive_messages'
                )
            """))
            
            tables = [row[0] for row in result.fetchall()]
            expected_tables = [
                'token_inventory', 'token_purchases', 'token_usage',
                'pricing_history', 'user_behavior', 'lead_scores',
                'sales_opportunities', 'proactive_messages'
            ]
            
            missing_tables = set(expected_tables) - set(tables)
            
            if missing_tables:
                logger.warning(f"⚠️ Missing tables: {missing_tables}")
                return False
            else:
                logger.info("✅ All agentic tables verified successfully")
                return True
                
    except Exception as e:
        logger.error(f"❌ Error verifying database: {e}")
        return False


async def main():
    """Main function"""
    logger.info("🚀 Initializing Agentic Claude Token Resale Bot Database...")
    
    # Initialize database
    await init_database()
    
    # Verify database
    success = await verify_database()
    
    if success:
        logger.info("🎉 Database initialization completed successfully!")
        logger.info(f"📁 Database file: {config.DB_NAME}")
        logger.info("🤖 Agentic features are ready to use!")
    else:
        logger.error("❌ Database initialization failed!")
        exit(1)


if __name__ == "__main__":
    asyncio.run(main())
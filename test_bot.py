#!/usr/bin/env python3
"""
Test script to demonstrate TokenGoblin bot functionality
This script shows how the bot works without requiring a real Telegram token
"""

import asyncio
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import *
from db import create_db_and_tables
from models.user import User
from models.category import Category
from models.subcategory import Subcategory
from models.item import Item
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_database():
    """Test database connection and create sample data"""
    try:
        # Create database and tables
        await create_db_and_tables()
        logger.info("✅ Database and tables created successfully")
        
        # Create engine for synchronous operations
        engine = create_engine(f"sqlite:///data/{DB_NAME}")
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        
        with SessionLocal() as session:
            # Create sample categories
            categories = [
                Category(name="Digital Products"),
                Category(name="Gaming"),
                Category(name="Entertainment")
            ]
            
            for category in categories:
                session.add(category)
            session.commit()
            logger.info("✅ Sample categories created")
            
            # Create sample subcategories
            subcategories = [
                Subcategory(name="Software"),
                Subcategory(name="Ebooks"),
                Subcategory(name="Game Keys"),
                Subcategory(name="Streaming")
            ]
            
            for subcategory in subcategories:
                session.add(subcategory)
            session.commit()
            logger.info("✅ Sample subcategories created")
            
            # Create sample items
            items = [
                Item(
                    private_data="Adobe Photoshop License Key: PS-2024-XXXX-XXXX",
                    description="1-year license for Adobe Photoshop",
                    price=99.99,
                    category_id=1,
                    subcategory_id=1
                ),
                Item(
                    private_data="Python Programming Ebook: PDF download link",
                    description="Complete guide to Python programming",
                    price=29.99,
                    category_id=1,
                    subcategory_id=2
                ),
                Item(
                    private_data="Steam Game Key: CYBER-XXXX-XXXX-XXXX",
                    description="Digital game key for Cyberpunk 2077",
                    price=59.99,
                    category_id=2,
                    subcategory_id=3
                ),
                Item(
                    private_data="Netflix Premium Account: email@example.com / password123",
                    description="1-month Netflix Premium subscription",
                    price=15.99,
                    category_id=3,
                    subcategory_id=4
                )
            ]
            
            for item in items:
                session.add(item)
            session.commit()
            logger.info("✅ Sample items created")
            
            # Display sample data
            print("\n📊 Sample Data Created:")
            print("=" * 50)
            
            categories = session.query(Category).all()
            for category in categories:
                print(f"📁 Category: {category.name}")
                subcategories = session.query(Subcategory).filter_by(category_id=category.id).all()
                for subcategory in subcategories:
                    print(f"  └── Subcategory: {subcategory.name}")
                    items = session.query(Item).filter_by(subcategory_id=subcategory.id).all()
                    for item in items:
                        print(f"      └── Item: {item.description} - ${item.price}")
            
            print("\n✅ Database test completed successfully!")
            
    except Exception as e:
        logger.error(f"❌ Database test failed: {e}")
        raise

def test_configuration():
    """Test configuration loading"""
    print("\n🔧 Configuration Test:")
    print("=" * 50)
    
    config_vars = [
        ("Database Name", DB_NAME),
        ("Redis Host", REDIS_HOST),
        ("Currency", CURRENCY),
        ("Bot Language", BOT_LANGUAGE),
        ("Runtime Environment", RUNTIME_ENVIRONMENT),
        ("Page Entries", PAGE_ENTRIES),
        ("Webhook Path", WEBHOOK_PATH),
        ("Webhook URL", WEBHOOK_URL)
    ]
    
    for name, value in config_vars:
        print(f"  {name}: {value}")
    
    print("\n✅ Configuration loaded successfully!")

def test_redis_connection():
    """Test Redis connection"""
    try:
        import redis
        r = redis.Redis(host=REDIS_HOST, password=REDIS_PASSWORD)
        r.ping()
        print("✅ Redis connection successful!")
        return True
    except Exception as e:
        print(f"❌ Redis connection failed: {e}")
        return False

def main():
    """Main test function"""
    print("🤖 TokenGoblin Bot Test Suite")
    print("=" * 50)
    
    # Test configuration
    test_configuration()
    
    # Test Redis connection
    test_redis_connection()
    
    # Test database
    print("\n🗄️ Testing Database...")
    asyncio.run(test_database())
    
    print("\n🎉 All tests completed!")
    print("\n📝 Next Steps:")
    print("1. Get a Telegram bot token from @BotFather")
    print("2. Update the TOKEN in your .env file")
    print("3. Get your Telegram ID from @userinfobot")
    print("4. Update ADMIN_ID_LIST in your .env file")
    print("5. Run 'python run.py' to start the bot")
    print("\n📚 For more information, see LOCAL_DEPLOYMENT_GUIDE.md")

if __name__ == "__main__":
    main() 
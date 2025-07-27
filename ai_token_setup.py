#!/usr/bin/env python3
"""
AI Token Resale Setup Script
Transforms TokenGoblin into a specialized AI token resale platform
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

async def setup_ai_token_store():
    """Set up the database with AI token categories and products"""
    try:
        # Create database and tables
        await create_db_and_tables()
        logger.info("✅ Database and tables created successfully")
        
        # Create engine for synchronous operations
        engine = create_engine(f"sqlite:///data/{DB_NAME}")
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        
        with SessionLocal() as session:
            # Create AI-focused categories
            ai_categories = [
                Category(name="Claude AI Models"),
                Category(name="GPT Models"),
                Category(name="Specialized AI"),
                Category(name="Bulk Packages")
            ]
            
            for category in ai_categories:
                session.add(category)
            session.commit()
            logger.info("✅ AI categories created")
            
            # Create AI model subcategories
            ai_subcategories = [
                # Claude Models
                Subcategory(name="Claude 3 Sonnet", category_id=1),
                Subcategory(name="Claude 3 Opus", category_id=1),
                Subcategory(name="Claude 3 Haiku", category_id=1),
                
                # GPT Models
                Subcategory(name="GPT-4 Turbo", category_id=2),
                Subcategory(name="GPT-3.5 Turbo", category_id=2),
                Subcategory(name="GPT-4", category_id=2),
                
                # Specialized AI
                Subcategory(name="Code Generation", category_id=3),
                Subcategory(name="Image Generation", category_id=3),
                Subcategory(name="Text Analysis", category_id=3),
                
                # Bulk Packages
                Subcategory(name="Developer Pack", category_id=4),
                Subcategory(name="Enterprise Pack", category_id=4),
                Subcategory(name="Student Pack", category_id=4)
            ]
            
            for subcategory in ai_subcategories:
                session.add(subcategory)
            session.commit()
            logger.info("✅ AI subcategories created")
            
            # Create AI token products
            ai_products = [
                # Claude 3 Sonnet
                Item(
                    private_data="Claude 3 Sonnet API Key: claude-3-sonnet-xxxxx\nUsage: 1000 tokens\nExpires: 30 days",
                    description="High-performance AI model for complex reasoning tasks. Perfect for analysis, coding, and creative writing.",
                    price=0.015,
                    category_id=1,
                    subcategory_id=1
                ),
                Item(
                    private_data="Claude 3 Sonnet API Key: claude-3-sonnet-yyyyy\nUsage: 5000 tokens\nExpires: 30 days",
                    description="Claude 3 Sonnet - 5000 tokens package. Ideal for extended projects and heavy usage.",
                    price=0.015,
                    category_id=1,
                    subcategory_id=1
                ),
                
                # Claude 3 Opus
                Item(
                    private_data="Claude 3 Opus API Key: claude-3-opus-xxxxx\nUsage: 1000 tokens\nExpires: 30 days",
                    description="Most powerful Claude model for advanced reasoning and analysis. Best for research and complex tasks.",
                    price=0.015,
                    category_id=1,
                    subcategory_id=2
                ),
                
                # Claude 3 Haiku
                Item(
                    private_data="Claude 3 Haiku API Key: claude-3-haiku-xxxxx\nUsage: 10000 tokens\nExpires: 30 days",
                    description="Fast and efficient AI model for quick responses. Great for chat applications and simple tasks.",
                    price=0.00025,
                    category_id=1,
                    subcategory_id=3
                ),
                
                # GPT-4 Turbo
                Item(
                    private_data="GPT-4 Turbo API Key: gpt-4-turbo-xxxxx\nUsage: 1000 tokens\nExpires: 30 days",
                    description="Latest GPT-4 model with improved performance and lower costs. Perfect for general AI tasks.",
                    price=0.01,
                    category_id=2,
                    subcategory_id=4
                ),
                
                # GPT-3.5 Turbo
                Item(
                    private_data="GPT-3.5 Turbo API Key: gpt-3.5-turbo-xxxxx\nUsage: 10000 tokens\nExpires: 30 days",
                    description="Fast and cost-effective GPT model. Ideal for chat applications and simple text generation.",
                    price=0.002,
                    category_id=2,
                    subcategory_id=5
                ),
                
                # Code Generation
                Item(
                    private_data="Code Generation API Key: code-gen-xxxxx\nUsage: 5000 tokens\nExpires: 30 days",
                    description="Specialized AI for code generation and programming assistance. Supports multiple languages.",
                    price=0.02,
                    category_id=3,
                    subcategory_id=7
                ),
                
                # Developer Pack
                Item(
                    private_data="Developer Pack:\n- Claude 3 Sonnet: 5000 tokens\n- GPT-4 Turbo: 3000 tokens\n- Code Generation: 2000 tokens\nExpires: 30 days",
                    description="Complete developer toolkit with multiple AI models for coding, debugging, and development tasks.",
                    price=0.012,
                    category_id=4,
                    subcategory_id=10
                ),
                
                # Enterprise Pack
                Item(
                    private_data="Enterprise Pack:\n- Claude 3 Opus: 10000 tokens\n- GPT-4 Turbo: 8000 tokens\n- All specialized models: 5000 tokens each\nExpires: 90 days",
                    description="Comprehensive AI solution for enterprise needs. Includes all models with extended validity.",
                    price=0.014,
                    category_id=4,
                    subcategory_id=11
                )
            ]
            
            for item in ai_products:
                session.add(item)
            session.commit()
            logger.info("✅ AI token products created")
            
            # Display the AI store setup
            print("\n🤖 AI Token Store Setup Complete!")
            print("=" * 50)
            
            categories = session.query(Category).all()
            for category in categories:
                print(f"📁 Category: {category.name}")
                subcategories = session.query(Subcategory).filter_by(category_id=category.id).all()
                for subcategory in subcategories:
                    print(f"  └── Subcategory: {subcategory.name}")
                    items = session.query(Item).filter_by(subcategory_id=subcategory.id).all()
                    for item in items:
                        print(f"      └── Item: {item.description[:50]}... - ${item.price}/token")
            
            print("\n✅ AI Token Store is ready!")
            
    except Exception as e:
        logger.error(f"❌ AI store setup failed: {e}")
        raise

def update_localization_for_ai():
    """Update localization file for AI-focused language"""
    print("\n🎨 Updating UI text for AI focus...")
    
    # This would modify l10n/en.json
    ai_updates = {
        "user": {
            "all_categories": "🧠 AI Models",
            "my_profile": "👤 My AI Profile", 
            "cart": "🛒 Token Cart",
            "top_up_balance_button": "💰 Buy Tokens",
            "purchase_history_button": "📊 Usage History",
            "faq": "❓ AI FAQ",
            "help": "🆘 AI Support"
        },
        "admin": {
            "menu": "🔑 AI Token Admin",
            "inventory_management": "🧠 Model Management",
            "statistics": "📊 AI Analytics",
            "user_management": "👥 User Management"
        }
    }
    
    print("✅ AI-focused language updates ready")
    print("📝 Edit l10n/en.json to apply these changes")

def create_ai_config():
    """Create AI-focused configuration"""
    print("\n⚙️ Creating AI-focused configuration...")
    
    ai_config = """
# AI Token Store Configuration
AGENTIC_MODE=true
OPENROUTER_API_KEY=your_openrouter_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# AI-specific settings
MIN_INVENTORY_THRESHOLD=1000
MAX_PURCHASE_BUDGET=500
OPPORTUNITY_CHECK_INTERVAL=3600
PRICING_UPDATE_INTERVAL=1800

# Bot Configuration
TOKEN=your_telegram_bot_token_here
ADMIN_ID_LIST=your_telegram_id_here
SUPPORT_LINK=https://t.me/your_username

# Database Configuration
DB_NAME=database.db
DB_ENCRYPTION=false
DB_PASS=

# Webhook Configuration
WEBHOOK_PATH=/
WEBAPP_HOST=localhost
WEBAPP_PORT=5000
WEBHOOK_SECRET_TOKEN=your_secret_token_here

# Redis Configuration
REDIS_HOST=localhost
REDIS_PASSWORD=your_redis_password_here

# Development Configuration
NGROK_TOKEN=your_ngrok_token_here
PAGE_ENTRIES=8
BOT_LANGUAGE=en
MULTIBOT=false
CURRENCY=USD
RUNTIME_ENVIRONMENT=dev

# Crypto Payment Configuration
KRYPTO_EXPRESS_API_KEY=your_krypto_express_api_key_here
KRYPTO_EXPRESS_API_URL=https://kryptoexpress.pro/api
KRYPTO_EXPRESS_API_SECRET=your_krypto_express_secret_here
"""
    
    with open('.env.ai', 'w') as f:
        f.write(ai_config)
    
    print("✅ AI configuration file created: .env.ai")
    print("📝 Copy .env.ai to .env to use AI-focused settings")

def main():
    """Main setup function"""
    print("🤖 AI Token Store Setup")
    print("=" * 50)
    
    # Set up AI database
    print("\n🗄️ Setting up AI token database...")
    asyncio.run(setup_ai_token_store())
    
    # Update localization
    update_localization_for_ai()
    
    # Create AI config
    create_ai_config()
    
    print("\n🎉 AI Token Store Setup Complete!")
    print("\n📋 Next Steps:")
    print("1. Copy .env.ai to .env")
    print("2. Add your API keys to .env")
    print("3. Edit l10n/en.json for AI language")
    print("4. Run: python run_agentic.py")
    print("\n🤖 Your bot is now ready for AI token resale!")

if __name__ == "__main__":
    main() 
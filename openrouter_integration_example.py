"""
OpenRouter AI Token Resale Integration Example
============================================

This module demonstrates how to integrate OpenRouter API with AiogramShopBot
for a minimal inventory AI token resale service with automated marketing.
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from decimal import Decimal

try:
    import aiohttp
    import redis
    from aiogram import Bot, Dispatcher, types
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    from sqlalchemy import create_engine, Column, String, DateTime, Decimal as SQLDecimal, Integer, Boolean
    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy.orm import sessionmaker
except ImportError as e:
    print(f"Missing dependency: {e}")
    print("Please install required packages:")
    print("pip install aiohttp redis aiogram sqlalchemy")
    exit(1)

# Configuration
OPENROUTER_API_KEY = "your_openrouter_api_key"
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
TELEGRAM_BOT_TOKEN = "your_telegram_bot_token"
REDIS_URL = "redis://localhost:6379"

# Database setup
Base = declarative_base()
engine = create_engine('sqlite:///ai_resale.db')
Session = sessionmaker(bind=engine)

@dataclass
class UsageResponse:
    """Response from OpenRouter API call"""
    content: str
    model: str
    tokens_used: int
    cost: float
    success: bool
    error: Optional[str] = None

class Customer(Base):
    __tablename__ = 'customers'
    
    id = Column(String, primary_key=True)
    telegram_id = Column(Integer, unique=True)
    email = Column(String)
    credits = Column(SQLDecimal(10, 4), default=0)
    tier = Column(String, default='basic')
    created_at = Column(DateTime, default=datetime.utcnow)
    last_activity = Column(DateTime, default=datetime.utcnow)
    total_spent = Column(SQLDecimal(10, 4), default=0)
    api_key = Column(String, unique=True)

class UsageLog(Base):
    __tablename__ = 'usage_logs'
    
    id = Column(String, primary_key=True)
    customer_id = Column(String)
    model = Column(String)
    tokens_used = Column(Integer)
    cost = Column(SQLDecimal(8, 4))
    markup_applied = Column(SQLDecimal(4, 2))
    created_at = Column(DateTime, default=datetime.utcnow)

class MarketingInteraction(Base):
    __tablename__ = 'marketing_interactions'
    
    id = Column(String, primary_key=True)
    customer_id = Column(String)
    channel = Column(String)
    interaction_type = Column(String)
    response_rate = Column(SQLDecimal(4, 2))
    created_at = Column(DateTime, default=datetime.utcnow)

class OpenRouterClient:
    """Client for interacting with OpenRouter API"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = OPENROUTER_BASE_URL
        self.session: Optional[Any] = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
        
    async def get_models(self) -> List[Dict]:
        """Get available models from OpenRouter"""
        async with self.session.get(
            f"{self.base_url}/models",
            headers={"Authorization": f"Bearer {self.api_key}"}
        ) as response:
            data = await response.json()
            return data.get('data', [])
    
    async def chat_completion(self, model: str, messages: List[Dict], max_tokens: int = 1000) -> UsageResponse:
        """Make a chat completion request through OpenRouter"""
        try:
            payload = {
                "model": model,
                "messages": messages,
                "max_tokens": max_tokens
            }
            
            async with self.session.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json=payload
            ) as response:
                data = await response.json()
                
                if response.status == 200:
                    usage = data.get('usage', {})
                    return UsageResponse(
                        content=data['choices'][0]['message']['content'],
                        model=model,
                        tokens_used=usage.get('total_tokens', 0),
                        cost=usage.get('total_cost', 0),
                        success=True
                    )
                else:
                    return UsageResponse(
                        content="",
                        model=model,
                        tokens_used=0,
                        cost=0,
                        success=False,
                        error=data.get('error', {}).get('message', 'Unknown error')
                    )
                    
        except Exception as e:
            return UsageResponse(
                content="",
                model=model,
                tokens_used=0,
                cost=0,
                success=False,
                error=str(e)
            )

class DynamicPricingEngine:
    """Dynamic pricing engine for AI token resale"""
    
    def __init__(self, redis_client):
        self.redis = redis_client
        self.base_markup = 0.4  # 40% base markup
        self.tier_discounts = {
            'basic': 0.0,
            'professional': 0.1,  # 10% discount
            'enterprise': 0.2     # 20% discount
        }
    
    async def get_current_demand(self, model: str) -> float:
        """Get current demand multiplier for a model"""
        key = f"demand:{model}"
        demand = await self.redis.get(key)
        return float(demand) if demand else 1.0
    
    async def update_demand(self, model: str, usage_count: int):
        """Update demand based on usage"""
        key = f"demand:{model}"
        current_demand = await self.get_current_demand(model)
        
        # Simple demand calculation based on usage
        new_demand = min(2.0, max(0.5, current_demand + (usage_count * 0.01)))
        await self.redis.setex(key, 3600, str(new_demand))  # Cache for 1 hour
    
    async def calculate_markup(self, customer_tier: str, model: str) -> float:
        """Calculate markup for a customer and model"""
        markup = self.base_markup
        
        # Apply tier discount
        tier_discount = self.tier_discounts.get(customer_tier, 0)
        markup -= tier_discount
        
        # Apply demand multiplier
        demand = await self.get_current_demand(model)
        markup *= demand
        
        # Premium model adjustment
        if model in ['gpt-4', 'claude-3-opus', 'gpt-4-turbo']:
            markup *= 1.1
        
        return max(0.1, markup)  # Minimum 10% markup

class AITokenResaleService:
    """Main service for AI token resale"""
    
    def __init__(self):
        self.openrouter_client = None
        self.pricing_engine = None
        self.redis_client = None
        self.bot = None
        
    async def initialize(self):
        """Initialize the service"""
        self.redis_client = redis.Redis.from_url(REDIS_URL)
        self.pricing_engine = DynamicPricingEngine(self.redis_client)
        self.bot = Bot(token=TELEGRAM_BOT_TOKEN)
        
        # Create database tables
        Base.metadata.create_all(engine)
        
    async def process_customer_request(self, customer_id: str, model: str, messages: List[Dict], max_tokens: int = 1000) -> Dict:
        """Process a customer's AI request"""
        session = Session()
        
        try:
            # Get customer
            customer = session.query(Customer).filter_by(id=customer_id).first()
            if not customer:
                return {"error": "Customer not found"}
            
            # Estimate cost
            estimated_cost = await self.estimate_cost(model, messages, max_tokens)
            markup = await self.pricing_engine.calculate_markup(customer.tier, model)
            final_cost = estimated_cost * (1 + markup)
            
            # Check credits
            if customer.credits < final_cost:
                # Send low credit notification
                await self.send_low_credit_notification(customer)
                return {"error": "Insufficient credits", "required": float(final_cost), "available": float(customer.credits)}
            
            # Make API call
            async with OpenRouterClient(OPENROUTER_API_KEY) as client:
                response = await client.chat_completion(model, messages, max_tokens)
            
            if response.success:
                # Calculate actual cost with markup
                actual_cost = response.cost * (1 + markup)
                
                # Deduct credits
                customer.credits -= Decimal(str(actual_cost))
                customer.total_spent += Decimal(str(actual_cost))
                customer.last_activity = datetime.utcnow()
                
                # Log usage
                usage_log = UsageLog(
                    id=f"usage_{datetime.utcnow().isoformat()}_{customer_id}",
                    customer_id=customer_id,
                    model=model,
                    tokens_used=response.tokens_used,
                    cost=Decimal(str(response.cost)),
                    markup_applied=Decimal(str(markup))
                )
                session.add(usage_log)
                session.commit()
                
                # Update demand
                await self.pricing_engine.update_demand(model, 1)
                
                # Trigger marketing actions
                await self.trigger_marketing_actions(customer, response)
                
                return {
                    "content": response.content,
                    "model": response.model,
                    "tokens_used": response.tokens_used,
                    "cost": float(actual_cost),
                    "remaining_credits": float(customer.credits)
                }
            else:
                return {"error": response.error}
                
        except Exception as e:
            session.rollback()
            return {"error": str(e)}
        finally:
            session.close()
    
    async def estimate_cost(self, model: str, messages: List[Dict], max_tokens: int) -> float:
        """Estimate the cost of a request"""
        # Simple estimation based on input length and model
        input_length = sum(len(msg.get('content', '')) for msg in messages)
        estimated_tokens = (input_length // 4) + max_tokens  # Rough estimation
        
        # Model-specific pricing (simplified)
        model_pricing = {
            'gpt-4': 0.00003,  # $0.03 per 1K tokens
            'gpt-3.5-turbo': 0.000002,  # $0.002 per 1K tokens
            'claude-3-sonnet': 0.000003,  # $0.003 per 1K tokens
            'claude-3-haiku': 0.0000008,  # $0.0008 per 1K tokens
        }
        
        price_per_token = model_pricing.get(model, 0.00001)  # Default pricing
        return estimated_tokens * price_per_token
    
    async def send_low_credit_notification(self, customer: Customer):
        """Send low credit notification to customer"""
        try:
            message = f"""
💰 **Low Credit Alert**

Hello! Your AI credit balance is running low: ${customer.credits:.2f}

To continue using our AI services, please top up your account:
- Basic Plan: $50 (500K tokens)
- Pro Plan: $200 (2M tokens)  
- Enterprise: $750 (8M tokens)

Click /topup to add credits instantly!
            """
            
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="💳 Top Up Credits", callback_data=f"topup_{customer.id}")],
                [InlineKeyboardButton(text="📊 View Usage", callback_data=f"usage_{customer.id}")]
            ])
            
            await self.bot.send_message(
                chat_id=customer.telegram_id,
                text=message,
                parse_mode="Markdown",
                reply_markup=keyboard
            )
        except Exception as e:
            logging.error(f"Failed to send low credit notification: {e}")

class AIMarketingBot:
    """AI-powered marketing automation bot"""
    
    def __init__(self, resale_service: AITokenResaleService):
        self.resale_service = resale_service
        self.content_templates = {
            'welcome': """
🚀 **Welcome to AI Token Resale!**

Get access to 100+ AI models including GPT-4, Claude, and Gemini at competitive prices!

✨ **Features:**
- 20-40% markup on wholesale prices
- Instant access to all major AI models
- Crypto payments accepted
- 24/7 automated service

💰 **Pricing Tiers:**
- Basic: $50/month (500K tokens)
- Pro: $200/month (2M tokens)
- Enterprise: $750/month (8M tokens)

Ready to start? Click /start to begin!
            """,
            'upsell': """
📈 **Upgrade Your AI Experience**

Based on your usage patterns, upgrading to {tier} would save you ${savings:.2f}/month!

🎯 **Your Benefits:**
- {discount}% lower markup rates
- Priority support
- Advanced analytics
- Custom integrations

Upgrade now and start saving immediately!
            """,
            'reactivation': """
🔄 **We Miss You!**

It's been {days} days since your last AI request. 

Here's what you're missing:
- New models: GPT-4 Turbo, Claude 3.5
- 25% price reduction on popular models
- Improved response times

Come back with 50% off your next $100 credit purchase!
            """
        }
    
    async def welcome_new_customer(self, customer: Customer):
        """Send welcome message to new customer"""
        try:
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🚀 Start Free Trial", callback_data=f"trial_{customer.id}")],
                [InlineKeyboardButton(text="💰 View Pricing", callback_data=f"pricing_{customer.id}")],
                [InlineKeyboardButton(text="📚 API Documentation", url="https://docs.example.com")]
            ])
            
            await self.resale_service.bot.send_message(
                chat_id=customer.telegram_id,
                text=self.content_templates['welcome'],
                parse_mode="Markdown",
                reply_markup=keyboard
            )
        except Exception as e:
            logging.error(f"Failed to send welcome message: {e}")
    
    async def trigger_upsell_campaign(self, customer: Customer):
        """Trigger upsell campaign based on usage"""
        try:
            # Calculate potential savings
            current_tier = customer.tier
            next_tier = self.get_next_tier(current_tier)
            
            if next_tier:
                savings = await self.calculate_potential_savings(customer, next_tier)
                discount = self.get_tier_discount(next_tier)
                
                message = self.content_templates['upsell'].format(
                    tier=next_tier.title(),
                    savings=savings,
                    discount=discount * 100
                )
                
                keyboard = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text=f"⬆️ Upgrade to {next_tier.title()}", callback_data=f"upgrade_{customer.id}_{next_tier}")],
                    [InlineKeyboardButton(text="📊 View Detailed Analysis", callback_data=f"analysis_{customer.id}")]
                ])
                
                await self.resale_service.bot.send_message(
                    chat_id=customer.telegram_id,
                    text=message,
                    parse_mode="Markdown",
                    reply_markup=keyboard
                )
        except Exception as e:
            logging.error(f"Failed to trigger upsell campaign: {e}")
    
    def get_next_tier(self, current_tier: str) -> Optional[str]:
        """Get the next tier for upselling"""
        tiers = ['basic', 'professional', 'enterprise']
        try:
            current_index = tiers.index(current_tier)
            return tiers[current_index + 1] if current_index < len(tiers) - 1 else None
        except ValueError:
            return 'professional'
    
    def get_tier_discount(self, tier: str) -> float:
        """Get discount for a tier"""
        discounts = {
            'basic': 0.0,
            'professional': 0.1,
            'enterprise': 0.2
        }
        return discounts.get(tier, 0.0)
    
    async def calculate_potential_savings(self, customer: Customer, target_tier: str) -> float:
        """Calculate potential monthly savings for tier upgrade"""
        # Get last 30 days usage
        session = Session()
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        
        usage_logs = session.query(UsageLog).filter(
            UsageLog.customer_id == customer.id,
            UsageLog.created_at >= thirty_days_ago
        ).all()
        
        if not usage_logs:
            return 0.0
        
        # Calculate current cost
        current_cost = sum(float(log.cost) * (1 + float(log.markup_applied)) for log in usage_logs)
        
        # Calculate cost with new tier
        new_discount = self.get_tier_discount(target_tier)
        new_cost = sum(float(log.cost) * (1 + float(log.markup_applied) - new_discount) for log in usage_logs)
        
        session.close()
        return max(0, current_cost - new_cost)

class TelegramBotHandler:
    """Telegram bot handler for customer interactions"""
    
    def __init__(self, resale_service: AITokenResaleService, marketing_bot: AIMarketingBot):
        self.resale_service = resale_service
        self.marketing_bot = marketing_bot
        self.dispatcher = Dispatcher()
        self.register_handlers()
    
    def register_handlers(self):
        """Register all bot handlers"""
        self.dispatcher.message.register(self.start_command, commands=["start"])
        self.dispatcher.message.register(self.help_command, commands=["help"])
        self.dispatcher.message.register(self.balance_command, commands=["balance"])
        self.dispatcher.message.register(self.topup_command, commands=["topup"])
        self.dispatcher.message.register(self.usage_command, commands=["usage"])
        self.dispatcher.callback_query.register(self.handle_callback_query)
    
    async def start_command(self, message: types.Message):
        """Handle /start command"""
        try:
            session = Session()
            customer = session.query(Customer).filter_by(telegram_id=message.from_user.id).first()
            
            if not customer:
                # Create new customer
                customer = Customer(
                    id=f"customer_{message.from_user.id}_{datetime.utcnow().timestamp()}",
                    telegram_id=message.from_user.id,
                    email=None,
                    credits=Decimal('10.00'),  # Free trial credits
                    tier='basic'
                )
                session.add(customer)
                session.commit()
                
                # Send welcome message
                await self.marketing_bot.welcome_new_customer(customer)
            else:
                # Existing customer
                await message.reply(
                    f"Welcome back! Your current balance: ${customer.credits:.2f}\n"
                    f"Tier: {customer.tier.title()}\n"
                    f"Use /help for available commands."
                )
            
            session.close()
            
        except Exception as e:
            logging.error(f"Error in start command: {e}")
            await message.reply("Sorry, something went wrong. Please try again.")
    
    async def balance_command(self, message: types.Message):
        """Handle /balance command"""
        try:
            session = Session()
            customer = session.query(Customer).filter_by(telegram_id=message.from_user.id).first()
            
            if customer:
                await message.reply(
                    f"💰 **Account Balance**\n\n"
                    f"Credits: ${customer.credits:.2f}\n"
                    f"Tier: {customer.tier.title()}\n"
                    f"Total Spent: ${customer.total_spent:.2f}\n"
                    f"Member Since: {customer.created_at.strftime('%Y-%m-%d')}",
                    parse_mode="Markdown"
                )
            else:
                await message.reply("Please use /start to create your account first.")
            
            session.close()
            
        except Exception as e:
            logging.error(f"Error in balance command: {e}")
            await message.reply("Sorry, something went wrong. Please try again.")
    
    async def help_command(self, message: types.Message):
        """Handle /help command"""
        help_text = """
🤖 **AI Token Resale Bot Commands**

**Account Management:**
/start - Create account or get status
/balance - Check your credit balance
/topup - Add credits to your account
/usage - View your usage statistics

**API Access:**
Your API endpoint: `https://api.example.com/v1/chat/completions`
Your API key: Check your account settings

**Pricing:**
- Basic: 40% markup on wholesale prices
- Pro: 30% markup + priority support
- Enterprise: 20% markup + custom features

**Supported Models:**
- GPT-4, GPT-3.5 Turbo
- Claude 3.5 Sonnet, Claude 3 Haiku
- Gemini Pro, Gemini Flash
- And 100+ more models!

Need help? Contact support: @support_username
        """
        await message.reply(help_text, parse_mode="Markdown")
    
    async def handle_callback_query(self, callback_query: types.CallbackQuery):
        """Handle callback queries from inline keyboards"""
        try:
            action, *params = callback_query.data.split('_')
            
            if action == 'topup':
                await self.handle_topup_callback(callback_query, params[0])
            elif action == 'upgrade':
                await self.handle_upgrade_callback(callback_query, params[0], params[1])
            elif action == 'trial':
                await self.handle_trial_callback(callback_query, params[0])
            
            await callback_query.answer()
            
        except Exception as e:
            logging.error(f"Error in callback query: {e}")
            await callback_query.answer("Sorry, something went wrong.")
    
    async def handle_topup_callback(self, callback_query: types.CallbackQuery, customer_id: str):
        """Handle topup callback"""
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="💳 $50 (500K tokens)", callback_data=f"pay_50_{customer_id}")],
            [InlineKeyboardButton(text="💳 $200 (2M tokens)", callback_data=f"pay_200_{customer_id}")],
            [InlineKeyboardButton(text="💳 $750 (8M tokens)", callback_data=f"pay_750_{customer_id}")],
            [InlineKeyboardButton(text="💰 Custom Amount", callback_data=f"custom_{customer_id}")]
        ])
        
        await callback_query.message.edit_text(
            "💳 **Choose Top-up Amount**\n\n"
            "Select a package or enter a custom amount:",
            parse_mode="Markdown",
            reply_markup=keyboard
        )

# Main application
async def main():
    """Main application entry point"""
    # Initialize services
    resale_service = AITokenResaleService()
    await resale_service.initialize()
    
    marketing_bot = AIMarketingBot(resale_service)
    telegram_handler = TelegramBotHandler(resale_service, marketing_bot)
    
    # Start the bot
    dp = telegram_handler.dispatcher
    await dp.start_polling(resale_service.bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
#!/usr/bin/env python3
"""
AI Token Arbitrage Agent - Main Engine
=====================================

Complete arbitrage system for AI tokens targeting $10K monthly revenue.
Integrates with AiogramShopBot for payments and customer management.

Usage:
    python arbitrage_agent.py --config config.json
"""

import asyncio
import json
import logging
import os
import time
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
import aiohttp
import websockets
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

# Configuration
@dataclass
class Config:
    # API Keys
    telegram_bot_token: str
    openrouter_api_key: str
    binance_api_key: str
    binance_secret_key: str
    coingecko_api_key: str
    etherscan_api_key: str
    
    # Database
    database_url: str
    redis_url: str
    
    # Trading Parameters
    min_profit_threshold: float = 0.02  # 2% minimum profit
    max_position_size: float = 1000.0   # $1000 max per trade
    stop_loss_percentage: float = 0.05  # 5% stop loss
    
    # Revenue Targets
    monthly_revenue_target: float = 10000.0
    daily_revenue_target: float = 333.33
    
    # Markup Rates
    basic_tier_markup: float = 0.30      # 30% markup
    premium_tier_markup: float = 0.20    # 20% markup
    enterprise_tier_markup: float = 0.15 # 15% markup

@dataclass
class ArbitrageOpportunity:
    exchange_a: str
    exchange_b: str
    token: str
    price_a: float
    price_b: float
    profit_percentage: float
    volume_available: float
    estimated_profit: float
    timestamp: datetime
    confidence_score: float

@dataclass
class Customer:
    user_id: int
    telegram_id: int
    tier: str  # basic, premium, enterprise
    balance: float
    total_spent: float
    created_at: datetime
    last_activity: datetime
    api_calls_this_month: int
    
class CustomerStates(StatesGroup):
    waiting_for_payment = State()
    selecting_service = State()
    configuring_api = State()

class ArbitrageEngine:
    """Core arbitrage detection and execution engine"""
    
    def __init__(self, config: Config):
        self.config = config
        self.session = None
        self.opportunities = []
        self.active_trades = {}
        self.daily_profit = 0.0
        self.monthly_profit = 0.0
        
    async def initialize(self):
        """Initialize the arbitrage engine"""
        self.session = aiohttp.ClientSession()
        await self.setup_exchange_connections()
        
    async def setup_exchange_connections(self):
        """Setup connections to various exchanges"""
        # Binance WebSocket for real-time prices
        self.binance_ws_url = "wss://stream.binance.com:9443/ws/!ticker@arr"
        
        # Exchange API endpoints
        self.exchange_apis = {
            'binance': 'https://api.binance.com',
            'coinbase': 'https://api.exchange.coinbase.com',
            'kraken': 'https://api.kraken.com',
            'kucoin': 'https://api.kucoin.com',
            'huobi': 'https://api.huobi.pro'
        }
        
    async def get_market_data(self) -> Dict[str, Dict]:
        """Fetch market data from multiple exchanges"""
        market_data = {}
        
        for exchange, api_url in self.exchange_apis.items():
            try:
                if exchange == 'binance':
                    data = await self.get_binance_prices()
                elif exchange == 'coinbase':
                    data = await self.get_coinbase_prices()
                # Add more exchanges as needed
                
                market_data[exchange] = data
            except Exception as e:
                logging.error(f"Error fetching data from {exchange}: {e}")
                
        return market_data
    
    async def get_binance_prices(self) -> Dict:
        """Get current prices from Binance"""
        try:
            async with self.session.get(f"{self.exchange_apis['binance']}/api/v3/ticker/24hr") as response:
                data = await response.json()
                prices = {}
                for item in data:
                    symbol = item['symbol']
                    prices[symbol] = {
                        'price': float(item['lastPrice']),
                        'volume': float(item['volume']),
                        'change': float(item['priceChangePercent'])
                    }
                return prices
        except Exception as e:
            logging.error(f"Binance API error: {e}")
            return {}
    
    async def get_coinbase_prices(self) -> Dict:
        """Get current prices from Coinbase"""
        try:
            async with self.session.get(f"{self.exchange_apis['coinbase']}/products") as response:
                products = await response.json()
                prices = {}
                
                for product in products[:50]:  # Limit to avoid rate limits
                    product_id = product['id']
                    async with self.session.get(f"{self.exchange_apis['coinbase']}/products/{product_id}/ticker") as ticker_response:
                        ticker = await ticker_response.json()
                        prices[product_id] = {
                            'price': float(ticker.get('price', 0)),
                            'volume': float(ticker.get('volume', 0)),
                            'bid': float(ticker.get('bid', 0)),
                            'ask': float(ticker.get('ask', 0))
                        }
                        await asyncio.sleep(0.1)  # Rate limiting
                        
                return prices
        except Exception as e:
            logging.error(f"Coinbase API error: {e}")
            return {}
    
    async def detect_arbitrage_opportunities(self, market_data: Dict) -> List[ArbitrageOpportunity]:
        """Detect arbitrage opportunities across exchanges"""
        opportunities = []
        
        # Compare prices across exchanges
        exchanges = list(market_data.keys())
        for i, exchange_a in enumerate(exchanges):
            for exchange_b in exchanges[i+1:]:
                opportunities.extend(
                    await self.compare_exchange_prices(
                        exchange_a, market_data[exchange_a],
                        exchange_b, market_data[exchange_b]
                    )
                )
        
        # Filter by profit threshold
        filtered_opportunities = [
            opp for opp in opportunities 
            if opp.profit_percentage >= self.config.min_profit_threshold
        ]
        
        # Sort by profit potential
        filtered_opportunities.sort(key=lambda x: x.estimated_profit, reverse=True)
        
        return filtered_opportunities[:10]  # Top 10 opportunities
    
    async def compare_exchange_prices(self, exchange_a: str, data_a: Dict, 
                                    exchange_b: str, data_b: Dict) -> List[ArbitrageOpportunity]:
        """Compare prices between two exchanges"""
        opportunities = []
        
        # Find common trading pairs
        common_pairs = set(data_a.keys()) & set(data_b.keys())
        
        for pair in common_pairs:
            try:
                price_a = data_a[pair]['price']
                price_b = data_b[pair]['price']
                
                if price_a == 0 or price_b == 0:
                    continue
                
                # Calculate profit percentage
                if price_a > price_b:
                    profit_pct = (price_a - price_b) / price_b
                    buy_exchange, sell_exchange = exchange_b, exchange_a
                    buy_price, sell_price = price_b, price_a
                else:
                    profit_pct = (price_b - price_a) / price_a
                    buy_exchange, sell_exchange = exchange_a, exchange_b
                    buy_price, sell_price = price_a, price_b
                
                if profit_pct >= self.config.min_profit_threshold:
                    # Estimate available volume
                    volume_a = data_a[pair].get('volume', 0)
                    volume_b = data_b[pair].get('volume', 0)
                    available_volume = min(volume_a, volume_b) * 0.01  # 1% of volume
                    
                    # Calculate estimated profit
                    position_size = min(self.config.max_position_size, available_volume * buy_price)
                    estimated_profit = position_size * profit_pct * 0.95  # Account for fees
                    
                    # Calculate confidence score
                    confidence = self.calculate_confidence_score(
                        profit_pct, available_volume, pair
                    )
                    
                    opportunity = ArbitrageOpportunity(
                        exchange_a=buy_exchange,
                        exchange_b=sell_exchange,
                        token=pair,
                        price_a=buy_price,
                        price_b=sell_price,
                        profit_percentage=profit_pct,
                        volume_available=available_volume,
                        estimated_profit=estimated_profit,
                        timestamp=datetime.now(),
                        confidence_score=confidence
                    )
                    
                    opportunities.append(opportunity)
                    
            except (KeyError, ValueError, ZeroDivisionError) as e:
                continue
                
        return opportunities
    
    def calculate_confidence_score(self, profit_pct: float, volume: float, pair: str) -> float:
        """Calculate confidence score for an opportunity"""
        score = 0.0
        
        # Profit percentage factor (higher is better, but diminishing returns)
        score += min(profit_pct * 10, 5.0)
        
        # Volume factor (higher volume = more confidence)
        if volume > 10000:
            score += 3.0
        elif volume > 1000:
            score += 2.0
        elif volume > 100:
            score += 1.0
        
        # Popular pair factor
        major_pairs = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'ADAUSDT', 'DOTUSDT']
        if pair in major_pairs:
            score += 2.0
        
        return min(score, 10.0)
    
    async def execute_arbitrage(self, opportunity: ArbitrageOpportunity) -> Dict:
        """Execute an arbitrage trade"""
        trade_id = f"arb_{int(time.time())}"
        
        try:
            # Simulate trade execution (implement actual trading logic)
            result = await self.simulate_trade_execution(opportunity)
            
            if result['success']:
                self.daily_profit += result['profit']
                self.monthly_profit += result['profit']
                
                logging.info(f"Arbitrage executed: {trade_id}, Profit: ${result['profit']:.2f}")
                
                return {
                    'trade_id': trade_id,
                    'success': True,
                    'profit': result['profit'],
                    'opportunity': asdict(opportunity)
                }
            else:
                return {
                    'trade_id': trade_id,
                    'success': False,
                    'error': result['error']
                }
                
        except Exception as e:
            logging.error(f"Trade execution failed: {e}")
            return {
                'trade_id': trade_id,
                'success': False,
                'error': str(e)
            }
    
    async def simulate_trade_execution(self, opportunity: ArbitrageOpportunity) -> Dict:
        """Simulate trade execution (replace with real trading logic)"""
        # Simulate execution time and slippage
        await asyncio.sleep(0.5)
        
        # Simulate 95% success rate
        if opportunity.confidence_score > 5.0:
            slippage = 0.002  # 0.2% slippage
            actual_profit = opportunity.estimated_profit * (1 - slippage)
            return {
                'success': True,
                'profit': actual_profit,
                'fees': opportunity.estimated_profit * 0.002  # 0.2% fees
            }
        else:
            return {
                'success': False,
                'error': 'Low confidence score'
            }

class AITokenReseller:
    """AI Token resale service with markup"""
    
    def __init__(self, config: Config):
        self.config = config
        self.customers = {}
        self.session = None
        
    async def initialize(self):
        """Initialize the token reseller"""
        self.session = aiohttp.ClientSession()
        
    async def process_ai_request(self, customer_id: int, model: str, prompt: str) -> Dict:
        """Process AI request with markup"""
        customer = self.customers.get(customer_id)
        if not customer:
            return {'error': 'Customer not found'}
        
        # Calculate cost with markup
        base_cost = await self.estimate_ai_cost(model, prompt)
        markup_rate = self.get_markup_rate(customer.tier)
        final_cost = base_cost * (1 + markup_rate)
        
        # Check customer balance
        if customer.balance < final_cost:
            return {
                'error': 'Insufficient balance',
                'required': final_cost,
                'available': customer.balance
            }
        
        # Make API call to OpenRouter
        response = await self.call_openrouter_api(model, prompt)
        
        if response['success']:
            # Deduct from customer balance
            customer.balance -= final_cost
            customer.total_spent += final_cost
            customer.api_calls_this_month += 1
            customer.last_activity = datetime.now()
            
            return {
                'success': True,
                'response': response['content'],
                'cost': final_cost,
                'remaining_balance': customer.balance
            }
        else:
            return {'error': response['error']}
    
    async def estimate_ai_cost(self, model: str, prompt: str) -> float:
        """Estimate AI API cost"""
        # Simplified cost estimation
        token_count = len(prompt.split()) * 1.3  # Rough estimation
        
        model_costs = {
            'gpt-4': 0.00003,
            'gpt-3.5-turbo': 0.000002,
            'claude-3-sonnet': 0.000003,
            'claude-3-haiku': 0.0000008
        }
        
        cost_per_token = model_costs.get(model, 0.00001)
        return token_count * cost_per_token
    
    def get_markup_rate(self, tier: str) -> float:
        """Get markup rate based on customer tier"""
        rates = {
            'basic': self.config.basic_tier_markup,
            'premium': self.config.premium_tier_markup,
            'enterprise': self.config.enterprise_tier_markup
        }
        return rates.get(tier, self.config.basic_tier_markup)
    
    async def call_openrouter_api(self, model: str, prompt: str) -> Dict:
        """Make API call to OpenRouter"""
        try:
            headers = {
                'Authorization': f'Bearer {self.config.openrouter_api_key}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'model': model,
                'messages': [{'role': 'user', 'content': prompt}],
                'max_tokens': 1000
            }
            
            async with self.session.post(
                'https://openrouter.ai/api/v1/chat/completions',
                headers=headers,
                json=payload
            ) as response:
                data = await response.json()
                
                if response.status == 200:
                    return {
                        'success': True,
                        'content': data['choices'][0]['message']['content']
                    }
                else:
                    return {
                        'success': False,
                        'error': data.get('error', {}).get('message', 'Unknown error')
                    }
                    
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

class TelegramSalesBot:
    """Telegram bot for customer acquisition and sales"""
    
    def __init__(self, config: Config, arbitrage_engine: ArbitrageEngine, token_reseller: AITokenReseller):
        self.config = config
        self.arbitrage_engine = arbitrage_engine
        self.token_reseller = token_reseller
        
        # Initialize bot
        self.bot = Bot(token=config.telegram_bot_token)
        storage = RedisStorage.from_url(config.redis_url)
        self.dp = Dispatcher(storage=storage)
        
        # Register handlers
        self.register_handlers()
        
    def register_handlers(self):
        """Register all bot handlers"""
        # Command handlers
        self.dp.message.register(self.start_command, commands=['start'])
        self.dp.message.register(self.help_command, commands=['help'])
        self.dp.message.register(self.balance_command, commands=['balance'])
        self.dp.message.register(self.deposit_command, commands=['deposit'])
        self.dp.message.register(self.arbitrage_command, commands=['arbitrage'])
        self.dp.message.register(self.ai_command, commands=['ai'])
        
        # Callback handlers
        self.dp.callback_query.register(self.handle_callback)
        
        # Message handlers
        self.dp.message.register(self.handle_text_message, F.text)
    
    async def start_command(self, message: types.Message, state: FSMContext):
        """Handle /start command"""
        user_id = message.from_user.id
        
        # Check if customer exists
        if user_id not in self.token_reseller.customers:
            # Create new customer
            customer = Customer(
                user_id=user_id,
                telegram_id=user_id,
                tier='basic',
                balance=0.0,
                total_spent=0.0,
                created_at=datetime.now(),
                last_activity=datetime.now(),
                api_calls_this_month=0
            )
            self.token_reseller.customers[user_id] = customer
            
            # Send welcome message
            await self.send_welcome_message(message)
        else:
            # Existing customer
            await self.send_dashboard(message)
    
    async def send_welcome_message(self, message: types.Message):
        """Send welcome message to new customers"""
        welcome_text = """
🚀 **Welcome to AI Arbitrage Agent!**

Your gateway to profitable AI token arbitrage and premium AI services!

💰 **Our Services:**
• AI Token Arbitrage (Auto-trading)
• Premium AI API Access (GPT-4, Claude, etc.)
• Real-time Market Analytics
• Crypto Payment Integration

📊 **Revenue Potential:**
• Basic Plan: $30/month (30% markup)
• Premium Plan: $100/month (20% markup) 
• Enterprise Plan: $300/month (15% markup)

🎯 **Get Started:**
1. Deposit crypto (BTC/ETH/USDT)
2. Choose your service tier
3. Start earning with AI arbitrage!

Click below to begin your journey to $10K monthly income! 💎
        """
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="💳 Make Deposit", callback_data="deposit")],
            [InlineKeyboardButton(text="📊 View Services", callback_data="services")],
            [InlineKeyboardButton(text="📈 Live Arbitrage", callback_data="arbitrage_live")],
            [InlineKeyboardButton(text="🤖 AI Demo", callback_data="ai_demo")]
        ])
        
        await message.answer(welcome_text, parse_mode="Markdown", reply_markup=keyboard)
    
    async def send_dashboard(self, message: types.Message):
        """Send customer dashboard"""
        user_id = message.from_user.id
        customer = self.token_reseller.customers[user_id]
        
        dashboard_text = f"""
📊 **Your Dashboard**

💰 **Account Status:**
• Balance: ${customer.balance:.2f}
• Tier: {customer.tier.title()}
• Total Spent: ${customer.total_spent:.2f}
• API Calls This Month: {customer.api_calls_this_month}

📈 **Today's Performance:**
• Arbitrage Profit: ${self.arbitrage_engine.daily_profit:.2f}
• Active Opportunities: {len(self.arbitrage_engine.opportunities)}

🎯 **Monthly Progress:**
• Revenue: ${self.arbitrage_engine.monthly_profit:.2f} / $10,000
• Target: {(self.arbitrage_engine.monthly_profit/10000)*100:.1f}% complete
        """
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="💳 Deposit Funds", callback_data="deposit")],
            [InlineKeyboardButton(text="🤖 Use AI Service", callback_data="ai_service")],
            [InlineKeyboardButton(text="📈 Start Arbitrage", callback_data="start_arbitrage")],
            [InlineKeyboardButton(text="⚙️ Settings", callback_data="settings")]
        ])
        
        await message.answer(dashboard_text, parse_mode="Markdown", reply_markup=keyboard)
    
    async def arbitrage_command(self, message: types.Message):
        """Handle /arbitrage command"""
        # Get latest opportunities
        market_data = await self.arbitrage_engine.get_market_data()
        opportunities = await self.arbitrage_engine.detect_arbitrage_opportunities(market_data)
        
        if opportunities:
            text = "📈 **Live Arbitrage Opportunities:**\n\n"
            
            for i, opp in enumerate(opportunities[:5], 1):
                text += f"""
**{i}. {opp.token}**
• Buy: {opp.exchange_a} @ ${opp.price_a:.6f}
• Sell: {opp.exchange_b} @ ${opp.price_b:.6f}
• Profit: {opp.profit_percentage:.2%} (${opp.estimated_profit:.2f})
• Confidence: {opp.confidence_score:.1f}/10

                """
            
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🚀 Execute Top Opportunity", callback_data="execute_arbitrage_0")],
                [InlineKeyboardButton(text="📊 View All Opportunities", callback_data="view_all_opportunities")],
                [InlineKeyboardButton(text="⚡ Auto-Trade (Premium)", callback_data="auto_trade")]
            ])
            
            await message.answer(text, parse_mode="Markdown", reply_markup=keyboard)
        else:
            await message.answer("🔍 No profitable arbitrage opportunities found at the moment. Check back in a few minutes!")
    
    async def ai_command(self, message: types.Message):
        """Handle /ai command"""
        args = message.text.split(' ', 2)
        
        if len(args) < 3:
            await message.answer("""
🤖 **AI Service Usage:**

`/ai <model> <prompt>`

**Available Models:**
• gpt-4 - Most capable, highest cost
• gpt-3.5-turbo - Fast and affordable  
• claude-3-sonnet - Great for analysis
• claude-3-haiku - Fastest responses

**Example:**
`/ai gpt-4 Explain blockchain technology`

**Pricing (with markup):**
• Basic Tier: 30% markup
• Premium Tier: 20% markup
• Enterprise Tier: 15% markup
            """, parse_mode="Markdown")
            return
        
        model = args[1]
        prompt = args[2]
        user_id = message.from_user.id
        
        # Process AI request
        result = await self.token_reseller.process_ai_request(user_id, model, prompt)
        
        if result.get('success'):
            response_text = f"""
🤖 **AI Response ({model}):**

{result['response']}

💰 **Cost:** ${result['cost']:.4f}
💳 **Remaining Balance:** ${result['remaining_balance']:.2f}
            """
            await message.answer(response_text, parse_mode="Markdown")
        else:
            await message.answer(f"❌ Error: {result['error']}")
    
    async def handle_callback(self, callback: types.CallbackQuery, state: FSMContext):
        """Handle callback queries"""
        data = callback.data
        user_id = callback.from_user.id
        
        if data == "deposit":
            await self.handle_deposit_callback(callback)
        elif data == "services":
            await self.handle_services_callback(callback)
        elif data == "arbitrage_live":
            await self.handle_arbitrage_live_callback(callback)
        elif data.startswith("execute_arbitrage_"):
            await self.handle_execute_arbitrage_callback(callback, data)
        elif data == "auto_trade":
            await self.handle_auto_trade_callback(callback)
        
        await callback.answer()
    
    async def handle_deposit_callback(self, callback: types.CallbackQuery):
        """Handle deposit callback"""
        deposit_text = """
💳 **Make a Deposit**

**Supported Cryptocurrencies:**
• Bitcoin (BTC)
• Ethereum (ETH) 
• USDT (TRC20/ERC20)
• Litecoin (LTC)
• Solana (SOL)

**Deposit Addresses:**
Generate unique addresses for each deposit to ensure proper tracking.

**Minimum Deposits:**
• $50 for Basic tier access
• $500 for Premium tier access
• $2000 for Enterprise tier access

Choose your deposit method:
        """
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="₿ Bitcoin (BTC)", callback_data="deposit_btc")],
            [InlineKeyboardButton(text="⟠ Ethereum (ETH)", callback_data="deposit_eth")],
            [InlineKeyboardButton(text="💰 USDT", callback_data="deposit_usdt")],
            [InlineKeyboardButton(text="🔙 Back to Dashboard", callback_data="dashboard")]
        ])
        
        await callback.message.edit_text(deposit_text, parse_mode="Markdown", reply_markup=keyboard)
    
    async def handle_services_callback(self, callback: types.CallbackQuery):
        """Handle services callback"""
        services_text = """
📊 **Our Premium Services**

🎯 **AI Token Arbitrage**
• Automated cross-exchange trading
• 15-25% monthly returns target
• Real-time opportunity detection
• Risk management included

🤖 **Premium AI API Access**
• GPT-4, Claude 3.5, Gemini Pro
• Competitive markup rates
• Priority processing
• Custom integrations

📈 **Service Tiers:**

**Basic ($30/month):**
• 30% AI API markup
• Manual arbitrage signals
• Email support

**Premium ($100/month):**
• 20% AI API markup  
• Semi-automated trading
• Priority support
• Advanced analytics

**Enterprise ($300/month):**
• 15% AI API markup
• Full auto-trading
• Dedicated account manager
• Custom integrations
        """
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🚀 Choose Basic", callback_data="tier_basic")],
            [InlineKeyboardButton(text="⭐ Choose Premium", callback_data="tier_premium")],
            [InlineKeyboardButton(text="💎 Choose Enterprise", callback_data="tier_enterprise")],
            [InlineKeyboardButton(text="🔙 Back", callback_data="dashboard")]
        ])
        
        await callback.message.edit_text(services_text, parse_mode="Markdown", reply_markup=keyboard)
    
    async def start_polling(self):
        """Start the bot polling"""
        await self.dp.start_polling(self.bot)

class ArbitrageAgent:
    """Main arbitrage agent orchestrator"""
    
    def __init__(self, config_path: str):
        # Load configuration
        with open(config_path, 'r') as f:
            config_data = json.load(f)
        self.config = Config(**config_data)
        
        # Initialize components
        self.arbitrage_engine = ArbitrageEngine(self.config)
        self.token_reseller = AITokenReseller(self.config)
        self.telegram_bot = TelegramSalesBot(
            self.config, 
            self.arbitrage_engine, 
            self.token_reseller
        )
        
        # Performance tracking
        self.start_time = datetime.now()
        self.total_revenue = 0.0
        
    async def initialize(self):
        """Initialize all components"""
        await self.arbitrage_engine.initialize()
        await self.token_reseller.initialize()
        
        logging.info("🚀 AI Arbitrage Agent initialized successfully!")
        logging.info(f"📊 Target: ${self.config.monthly_revenue_target}/month")
        
    async def run_arbitrage_loop(self):
        """Main arbitrage detection and execution loop"""
        while True:
            try:
                # Get market data
                market_data = await self.arbitrage_engine.get_market_data()
                
                # Detect opportunities
                opportunities = await self.arbitrage_engine.detect_arbitrage_opportunities(market_data)
                
                # Execute top opportunities
                for opp in opportunities[:3]:  # Execute top 3
                    if opp.confidence_score > 7.0:  # Only high-confidence trades
                        result = await self.arbitrage_engine.execute_arbitrage(opp)
                        if result['success']:
                            self.total_revenue += result['profit']
                            logging.info(f"💰 Arbitrage profit: ${result['profit']:.2f}")
                
                # Update opportunities for display
                self.arbitrage_engine.opportunities = opportunities
                
                # Check daily/monthly targets
                await self.check_revenue_targets()
                
                # Wait before next iteration
                await asyncio.sleep(60)  # Check every minute
                
            except Exception as e:
                logging.error(f"Arbitrage loop error: {e}")
                await asyncio.sleep(30)  # Shorter wait on error
    
    async def check_revenue_targets(self):
        """Check if revenue targets are being met"""
        days_in_month = (datetime.now() - self.start_time).days + 1
        expected_daily_revenue = self.config.monthly_revenue_target / 30
        expected_total = expected_daily_revenue * days_in_month
        
        if self.total_revenue < expected_total * 0.8:  # 80% of target
            logging.warning(f"⚠️ Revenue below target: ${self.total_revenue:.2f} vs ${expected_total:.2f}")
            # Could trigger marketing campaigns or strategy adjustments
    
    async def run(self):
        """Main entry point"""
        try:
            await self.initialize()
            
            # Start concurrent tasks
            tasks = [
                asyncio.create_task(self.run_arbitrage_loop()),
                asyncio.create_task(self.telegram_bot.start_polling())
            ]
            
            logging.info("🎯 AI Arbitrage Agent running - Target: $10K/month")
            
            # Run forever
            await asyncio.gather(*tasks)
            
        except KeyboardInterrupt:
            logging.info("👋 Shutting down AI Arbitrage Agent...")
        except Exception as e:
            logging.error(f"❌ Fatal error: {e}")
        finally:
            # Cleanup
            if self.arbitrage_engine.session:
                await self.arbitrage_engine.session.close()
            if self.token_reseller.session:
                await self.token_reseller.session.close()

async def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='AI Token Arbitrage Agent')
    parser.add_argument('--config', required=True, help='Path to config file')
    parser.add_argument('--log-level', default='INFO', help='Logging level')
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=getattr(logging, args.log_level.upper()),
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Create and run agent
    agent = ArbitrageAgent(args.config)
    await agent.run()

if __name__ == "__main__":
    asyncio.run(main())
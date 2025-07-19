import asyncio
import logging
import traceback
from datetime import datetime
from aiogram import types, F, Router
from aiogram.filters import Command
from aiogram.types import ErrorEvent, Message, BufferedInputFile, User
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

import config
from config import SUPPORT_LINK
from bot import dp, main, redis, bot
from enums.bot_entity import BotEntity
from middleware.database import DBSessionMiddleware
from middleware.throttling_middleware import ThrottlingMiddleware
from models.user import UserDTO
from multibot import main as main_multibot
from handlers.user.cart import cart_router
from handlers.admin.admin import admin_router
from handlers.user.all_categories import all_categories_router
from handlers.user.my_profile import my_profile_router
from services.notification import NotificationService
from services.user import UserService
from services.geo_targeting import GeoTargetingService
from services.agentic_marketing import AgenticMarketingOrchestrator
from services.minimal_crypto_payment import MinimalCryptoPaymentService
from utils.custom_filters import IsUserExistFilter
from utils.localizator import Localizator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize specialized services for restricted countries
geo_service = GeoTargetingService()
marketing_orchestrator = AgenticMarketingOrchestrator()
crypto_payment_service = MinimalCryptoPaymentService()

# Main router for restricted countries bot
restricted_router = Router()


@restricted_router.message(Command(commands=["start", "help"]))
async def start_restricted(message: types.Message, session: AsyncSession | Session):
    """Enhanced start command with geo-targeting and regional pricing"""
    user = message.from_user
    telegram_id = user.id
    
    # Detect user's region for targeted experience
    detected_region = await geo_service.detect_user_region(user, session)
    logger.info(f"User {telegram_id} detected as region: {detected_region}")
    
    # Create or update user
    await UserService.create_if_not_exist(UserDTO(
        telegram_username=user.username,
        telegram_id=telegram_id
    ), session)
    
    # Send region-specific welcome message
    welcome_message = await _create_regional_welcome_message(detected_region, user)
    
    # Create region-appropriate keyboard
    keyboard = await _create_regional_keyboard(detected_region, telegram_id)
    
    start_markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2, keyboard=keyboard)
    await message.answer(welcome_message, reply_markup=start_markup)
    
    # Log user interaction for behavioral analysis
    await _log_user_interaction(telegram_id, 'start_command', {
        'region': detected_region,
        'language': user.language_code,
        'timestamp': datetime.now().isoformat()
    })


@restricted_router.message(F.text == "🚀 Quick Start", IsUserExistFilter())
async def quick_start_restricted(message: types.Message, session: AsyncSession | Session):
    """Quick start flow for restricted country users"""
    user = message.from_user
    telegram_id = user.id
    
    # Detect region
    detected_region = await geo_service.detect_user_region(user, session)
    
    # Get region-specific payment methods
    supported_cryptos = await crypto_payment_service.get_supported_cryptos_for_region(detected_region)
    
    # Create quick start message
    quick_start_msg = await _create_quick_start_message(detected_region, supported_cryptos)
    
    # Create quick start keyboard
    kb_builder = InlineKeyboardBuilder()
    
    # Add token package buttons with regional pricing
    packages = await _get_regional_token_packages(detected_region)
    for package in packages:
        kb_builder.button(
            text=f"💎 {package['name']} - ${package['price']:.2f}",
            callback_data=f"quick_buy:{package['id']}"
        )
    
    # Add help button
    kb_builder.button(text="❓ Need Help?", callback_data="quick_help")
    kb_builder.adjust(1)
    
    await message.answer(quick_start_msg, reply_markup=kb_builder.as_markup())


@restricted_router.message(F.text == "💰 Regional Pricing", IsUserExistFilter())
async def show_regional_pricing(message: types.Message, session: AsyncSession | Session):
    """Show region-specific pricing with justification"""
    user = message.from_user
    detected_region = await geo_service.detect_user_region(user, session)
    
    # Get regional pricing information
    pricing_info = await geo_service.apply_regional_pricing(10.0, detected_region)  # Base $10 example
    
    pricing_message = await _create_pricing_explanation_message(detected_region, pricing_info)
    
    # Create pricing comparison keyboard
    kb_builder = InlineKeyboardBuilder()
    kb_builder.button(text="📊 Compare Plans", callback_data="compare_plans")
    kb_builder.button(text="🎯 Why These Prices?", callback_data="pricing_explanation")
    kb_builder.button(text="💳 Payment Methods", callback_data="payment_methods")
    kb_builder.adjust(1)
    
    await message.answer(pricing_message, reply_markup=kb_builder.as_markup())


@restricted_router.message(F.text == "🔐 Privacy & Security", IsUserExistFilter())
async def show_privacy_features(message: types.Message, session: AsyncSession | Session):
    """Show privacy and security features for restricted regions"""
    user = message.from_user
    detected_region = await geo_service.detect_user_region(user, session)
    
    privacy_message = await _create_privacy_message(detected_region)
    
    kb_builder = InlineKeyboardBuilder()
    kb_builder.button(text="🛡️ Security Features", callback_data="security_features")
    kb_builder.button(text="🔒 Anonymous Usage", callback_data="anonymous_usage")
    kb_builder.button(text="💼 Data Protection", callback_data="data_protection")
    kb_builder.adjust(1)
    
    await message.answer(privacy_message, reply_markup=kb_builder.as_markup())


@restricted_router.callback_query(F.data.startswith("quick_buy:"))
async def handle_quick_buy(callback: types.CallbackQuery, session: AsyncSession | Session):
    """Handle quick buy for token packages"""
    package_id = callback.data.split(":")[1]
    user = callback.from_user
    
    # Detect region for pricing
    detected_region = await geo_service.detect_user_region(user, session)
    
    # Get package details with regional pricing
    package = await _get_package_details(package_id, detected_region)
    
    if not package:
        await callback.answer("Package not found", show_alert=True)
        return
    
    # Get supported payment methods for region
    payment_methods = await crypto_payment_service.get_supported_cryptos_for_region(detected_region)
    
    # Create payment method selection
    kb_builder = InlineKeyboardBuilder()
    for crypto_data in payment_methods:
        crypto = crypto_data['crypto']
        crypto_info = crypto_data['info']
        kb_builder.button(
            text=f"💳 Pay with {crypto_info['name']}",
            callback_data=f"pay:{package_id}:{crypto}"
        )
    
    kb_builder.button(text="❌ Cancel", callback_data="cancel_purchase")
    kb_builder.adjust(1)
    
    purchase_message = f"""🎯 **{package['name']}**

💎 Tokens: {package['tokens']:,}
💰 Price: ${package['price']:.2f}
🌍 Region: {detected_region.title()}

Choose your payment method:"""
    
    await callback.message.edit_text(purchase_message, reply_markup=kb_builder.as_markup())


@restricted_router.callback_query(F.data.startswith("pay:"))
async def handle_payment_selection(callback: types.CallbackQuery, session: AsyncSession | Session):
    """Handle payment method selection"""
    _, package_id, crypto = callback.data.split(":")
    user = callback.from_user
    
    try:
        # Get package details
        detected_region = await geo_service.detect_user_region(user, session)
        package = await _get_package_details(package_id, detected_region)
        
        if not package:
            await callback.answer("Package not found", show_alert=True)
            return
        
        # Create payment request
        payment_request = await crypto_payment_service.create_payment_request(
            user_id=user.id,
            amount_usd=package['price'],
            crypto=crypto,
            session=session
        )
        
        # Create payment message
        payment_message = await _create_payment_message(payment_request, package)
        
        # Create payment monitoring keyboard
        kb_builder = InlineKeyboardBuilder()
        kb_builder.button(text="✅ I've Sent Payment", callback_data=f"confirm_payment:{payment_request['payment_id']}")
        kb_builder.button(text="📋 Copy Address", callback_data=f"copy_address:{payment_request['address']}")
        kb_builder.button(text="❓ Payment Help", callback_data="payment_help")
        kb_builder.button(text="❌ Cancel", callback_data="cancel_purchase")
        kb_builder.adjust(2, 1, 1)
        
        await callback.message.edit_text(payment_message, reply_markup=kb_builder.as_markup())
        
    except Exception as e:
        logger.error(f"Error creating payment request: {e}")
        await callback.answer("Error creating payment. Please try again.", show_alert=True)


@restricted_router.message(F.text == Localizator.get_text(BotEntity.USER, "faq"), IsUserExistFilter())
async def faq_restricted(message: types.Message, session: AsyncSession | Session):
    """Enhanced FAQ with region-specific information"""
    user = message.from_user
    detected_region = await geo_service.detect_user_region(user, session)
    
    faq_message = await _create_regional_faq(detected_region)
    await message.answer(faq_message)


@restricted_router.error(F.update.message.as_("message"))
async def error_handler_restricted(event: ErrorEvent, message: Message):
    """Enhanced error handler with region tracking"""
    await message.answer("Oops, something went wrong! Our team has been notified.")
    
    traceback_str = traceback.format_exc()
    admin_notification = (
        f"Critical error in restricted countries bot\n\n"
        f"Error: {event.exception}\n"
        f"User: {message.from_user.id}\n"
        f"Message: {message.text}\n\n"
        f"Stack trace:\n{traceback_str}"
    )
    
    if len(admin_notification) > 4096:
        byte_array = bytearray(admin_notification, 'utf-8')
        admin_notification = BufferedInputFile(byte_array, "exception.txt")
    
    await NotificationService.send_to_admins(admin_notification, None)


# Helper Functions

async def _create_regional_welcome_message(region: str, user: User) -> str:
    """Create region-specific welcome message"""
    regional_messages = {
        'ru': f"""🤖 Добро пожаловать в Claude AI Bot, {user.first_name}!

🚫 **Claude заблокирован в России?** Не проблема!
✅ Получите полный доступ к Claude AI через наш бот
🔒 Полная анонимность и безопасность
💰 Оплата криптовалютой (USDT TRC20, Bitcoin)
⚡ Мгновенный доступ без VPN

💎 **Начните с базового пакета:** 1000 токенов за $25
🎁 **Бонус новичкам:** Скидка 20% на первую покупку

🚀 Нажмите "Quick Start" для быстрого начала!""",

        'zh-hans': f"""🤖 欢迎使用Claude AI机器人，{user.first_name}！

🚫 **无法访问Claude？** 我们来解决！
✅ 通过我们的机器人获得Claude AI完整访问权限
🔒 完全匿名和安全
💰 加密货币支付（USDT TRC20，比特币）
⚡ 无需翻墙即时访问

💎 **从基础包开始：** 1000个代币仅需$30
🎁 **新用户优惠：** 首次购买享受25%折扣

🚀 点击"Quick Start"快速开始！""",

        'fa': f"""🤖 به ربات Claude AI خوش آمدید، {user.first_name}!

🚫 **Claude مسدود است؟** ما حل داریم!
✅ دسترسی کامل به Claude AI از طریق ربات ما
🔒 کاملاً ناشناس و امن
💰 پرداخت با ارز دیجیتال (USDT TRC20، بیت کوین)
⚡ دسترسی فوری بدون فیلترشکن

💎 **شروع با پکیج پایه:** 1000 توکن فقط $28
🎁 **تخفیف کاربران جدید:** 22% تخفیف خرید اول

🚀 روی "Quick Start" کلیک کنید!""",

        'default': f"""🤖 Welcome to Claude AI Bot, {user.first_name}!

🚫 **Claude blocked in your region?** We've got you covered!
✅ Get full Claude AI access through our bot
🔒 Complete privacy and security
💰 Cryptocurrency payments (USDT TRC20, Bitcoin)
⚡ Instant access without VPN

💎 **Start with Basic Package:** 1000 tokens for $20
🎁 **New User Bonus:** 15% off first purchase

🚀 Click "Quick Start" to begin!"""
    }
    
    return regional_messages.get(region, regional_messages['default'])


async def _create_regional_keyboard(region: str, telegram_id: int) -> list:
    """Create region-appropriate keyboard"""
    # Base buttons
    all_categories_button = types.KeyboardButton(text=Localizator.get_text(BotEntity.USER, "all_categories"))
    my_profile_button = types.KeyboardButton(text=Localizator.get_text(BotEntity.USER, "my_profile"))
    cart_button = types.KeyboardButton(text=Localizator.get_text(BotEntity.USER, "cart"))
    
    # Region-specific buttons
    quick_start_button = types.KeyboardButton(text="🚀 Quick Start")
    regional_pricing_button = types.KeyboardButton(text="💰 Regional Pricing")
    privacy_button = types.KeyboardButton(text="🔐 Privacy & Security")
    help_button = types.KeyboardButton(text=Localizator.get_text(BotEntity.USER, "help"))
    
    # Build keyboard based on region
    keyboard = [
        [quick_start_button, regional_pricing_button],
        [all_categories_button, my_profile_button],
        [privacy_button, cart_button],
        [help_button]
    ]
    
    # Add admin menu for admins
    if telegram_id in config.ADMIN_ID_LIST:
        admin_menu_button = types.KeyboardButton(text=Localizator.get_text(BotEntity.ADMIN, "menu"))
        keyboard.append([admin_menu_button])
    
    return keyboard


async def _get_regional_token_packages(region: str) -> list:
    """Get token packages with regional pricing"""
    base_packages = [
        {'id': 'starter', 'name': 'Starter', 'tokens': 1000, 'base_price': 10.0},
        {'id': 'standard', 'name': 'Standard', 'tokens': 5000, 'base_price': 45.0},
        {'id': 'premium', 'name': 'Premium', 'tokens': 15000, 'base_price': 120.0},
        {'id': 'enterprise', 'name': 'Enterprise', 'tokens': 50000, 'base_price': 350.0}
    ]
    
    packages = []
    for package in base_packages:
        pricing = await geo_service.apply_regional_pricing(package['base_price'], region)
        packages.append({
            'id': package['id'],
            'name': package['name'],
            'tokens': package['tokens'],
            'price': pricing['regional_price'],
            'base_price': package['base_price'],
            'discount': round((1 - pricing['regional_price'] / (package['base_price'] * 2)) * 100, 1) if region != 'default' else 0
        })
    
    return packages


async def _get_package_details(package_id: str, region: str) -> dict:
    """Get detailed package information"""
    packages = await _get_regional_token_packages(region)
    return next((p for p in packages if p['id'] == package_id), None)


async def _create_payment_message(payment_request: dict, package: dict) -> str:
    """Create payment instruction message"""
    crypto_info = payment_request['crypto_info']
    instructions = payment_request['instructions']
    
    message = f"""💳 **Payment Instructions**

📦 **Package:** {package['name']}
💎 **Tokens:** {package['tokens']:,}
💰 **Amount:** ${payment_request['amount_usd']:.2f}

🪙 **{crypto_info['name']} Payment:**
💰 **Amount:** {payment_request['amount_crypto']:.6f} {crypto_info['symbol']}
📍 **Address:** `{payment_request['address']}`

📋 **Instructions:**
"""
    
    for step in instructions['steps']:
        message += f"{step}\n"
    
    message += "\n⚠️ **Important:**\n"
    for warning in instructions['warnings']:
        message += f"{warning}\n"
    
    message += f"\n⏰ **Expires:** {payment_request['expires_at'][:19]}"
    
    return message


async def _log_user_interaction(user_id: int, interaction_type: str, metadata: dict):
    """Log user interaction for behavioral analysis"""
    logger.info(f"User interaction: {user_id} - {interaction_type} - {metadata}")
    # In production, this would store in user_interactions table


async def start_background_services():
    """Start all background services for restricted countries bot"""
    logger.info("🌍 Starting background services for restricted countries bot...")
    
    # Start services in background
    background_tasks = [
        asyncio.create_task(marketing_orchestrator.start_marketing_orchestration()),
        asyncio.create_task(crypto_payment_service.start_payment_monitoring())
    ]
    
    # Don't await here - let them run in background
    for task in background_tasks:
        task.add_done_callback(lambda t: logger.error(f"Background task completed: {t.exception()}") if t.exception() else None)


# Setup middleware and routers
throttling_middleware = ThrottlingMiddleware(redis)
users_routers = Router()
users_routers.include_routers(
    all_categories_router,
    my_profile_router,
    cart_router
)
users_routers.message.middleware(throttling_middleware)
users_routers.callback_query.middleware(throttling_middleware)

restricted_router.include_router(admin_router)
restricted_router.include_routers(users_routers)
restricted_router.message.middleware(DBSessionMiddleware())
restricted_router.callback_query.middleware(DBSessionMiddleware())


def main_restricted():
    """Main function for restricted countries bot"""
    logger.info("🚀 Starting Restricted Countries Claude AI Bot...")
    
    if config.MULTIBOT:
        main_multibot(restricted_router)
    else:
        # Start background services
        asyncio.create_task(start_background_services())
        
        # Include main router
        dp.include_router(restricted_router)
        
        # Start the bot
        main()


if __name__ == '__main__':
    main_restricted()
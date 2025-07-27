import asyncio
import logging
from aiogram import types, F, Router
from aiogram.filters import Command
from aiogram.types import ErrorEvent, Message, BufferedInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

import config
from config import SUPPORT_LINK
from bot_agentic import dp, bot, handle_user_interaction, get_agentic_analytics, redis_client
from enums.bot_entity import BotEntity
from middleware.database import DBSessionMiddleware
from middleware.throttling_middleware import ThrottlingMiddleware
from models.user import UserDTO
from multibot import main as main_multibot
from handlers.user.cart import cart_router
from handlers.admin.admin import admin_router
from handlers.user.all_categories import all_categories_router
from handlers.user.my_profile import my_profile_router
from handlers.user.conversational_ai import conversational_ai_router
from handlers.user.ai_tokens import ai_tokens_router
from services.notification import NotificationService
from services.user import UserService
from utils.custom_filters import IsUserExistFilter
from utils.localizator import Localizator

logging.basicConfig(level=logging.INFO)
main_router = Router()


@main_router.message(Command(commands=["start", "help"]))
async def start(message: types.message, session: AsyncSession | Session):
    all_categories_button = types.KeyboardButton(text=Localizator.get_text(BotEntity.USER, "all_categories"))
    my_profile_button = types.KeyboardButton(text=Localizator.get_text(BotEntity.USER, "my_profile"))
    faq_button = types.KeyboardButton(text=Localizator.get_text(BotEntity.USER, "faq"))
    help_button = types.KeyboardButton(text=Localizator.get_text(BotEntity.USER, "help"))
    admin_menu_button = types.KeyboardButton(text=Localizator.get_text(BotEntity.ADMIN, "menu"))
    cart_button = types.KeyboardButton(text=Localizator.get_text(BotEntity.USER, "cart"))
    ai_tokens_button = types.KeyboardButton(text=Localizator.get_text(BotEntity.USER, "ai_tokens"))
    
    # Add agentic features button if enabled
    if config.AGENTIC_MODE:
        agentic_button = types.KeyboardButton(text="🤖 Agentic Features")
    
    telegram_id = message.from_user.id
    await UserService.create_if_not_exist(UserDTO(
        telegram_username=message.from_user.username,
        telegram_id=telegram_id
    ), session)
    
    # Log user interaction for agentic analysis
    await handle_user_interaction(telegram_id, "start", {
        "username": message.from_user.username,
        "first_name": message.from_user.first_name,
        "last_name": message.from_user.last_name
    })
    
    keyboard = [[all_categories_button, my_profile_button], [faq_button, help_button], [cart_button, ai_tokens_button]]
    if telegram_id in config.ADMIN_ID_LIST:
        keyboard.append([admin_menu_button])
    if config.AGENTIC_MODE:
        keyboard.append([agentic_button])
    
    start_markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2, keyboard=keyboard)
    await message.answer(Localizator.get_text(BotEntity.COMMON, "start_message"), reply_markup=start_markup)


@main_router.message(F.text == Localizator.get_text(BotEntity.USER, "faq"), IsUserExistFilter())
async def faq(message: types.message):
    await handle_user_interaction(message.from_user.id, "faq")
    await message.answer(Localizator.get_text(BotEntity.USER, "faq_string"))


@main_router.message(F.text == Localizator.get_text(BotEntity.USER, "help"), IsUserExistFilter())
async def support(message: types.message):
    await handle_user_interaction(message.from_user.id, "help")
    admin_keyboard_builder = InlineKeyboardBuilder()
    admin_keyboard_builder.button(text=Localizator.get_text(BotEntity.USER, "help_button"), url=SUPPORT_LINK)
    await message.answer(Localizator.get_text(BotEntity.USER, "help_string"),
                         reply_markup=admin_keyboard_builder.as_markup())


@main_router.message(F.text == "🤖 Agentic Features", IsUserExistFilter())
async def agentic_features(message: types.message):
    """Show agentic features menu"""
    if not config.AGENTIC_MODE:
        await message.answer("Agentic features are not enabled.")
        return
    
    await handle_user_interaction(message.from_user.id, "agentic_features")
    
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="📊 Agentic Analytics", callback_data="agentic_analytics")
    keyboard.button(text="🎯 Sales Opportunities", callback_data="sales_opportunities")
    keyboard.button(text="💰 Smart Pricing", callback_data="smart_pricing")
    keyboard.button(text="📦 Auto Inventory", callback_data="auto_inventory")
    keyboard.adjust(2)
    
    await message.answer(
        "🤖 **Agentic Features Dashboard**\n\n"
        "Welcome to the intelligent Claude token resale system!\n\n"
        "• **Smart Lead Generation**: Automatically identifies high-value prospects\n"
        "• **Dynamic Pricing**: Real-time price optimization based on market conditions\n"
        "• **Predictive Inventory**: Automated restocking based on demand patterns\n"
        "• **Proactive Outreach**: Intelligent customer engagement campaigns\n\n"
        "Select a feature to explore:",
        reply_markup=keyboard.as_markup()
    )


@main_router.callback_query(F.data == "agentic_analytics")
async def show_agentic_analytics(callback: types.CallbackQuery):
    """Show agentic analytics"""
    if not config.AGENTIC_MODE:
        await callback.answer("Agentic features are not enabled.")
        return
    
    await handle_user_interaction(callback.from_user.id, "view_analytics")
    
    analytics = await get_agentic_analytics()
    
    if analytics.get('agentic_mode'):
        message = (
            "📊 **Agentic Analytics Report**\n\n"
            f"🎯 **Sales Opportunities**: {analytics.get('opportunities_found', 0)} found\n"
            f"💳 **Payment Success Rate**: {analytics.get('payment_success_rate', 0):.1%}\n"
            f"💰 **Total Payments**: {analytics.get('total_payments', 0)}\n"
            f"🏦 **Account Balance**: ${analytics.get('account_balance', 0):.2f}\n\n"
            "🤖 **System Status**: Active and learning"
        )
    else:
        message = "Agentic mode is not enabled."
    
    await callback.message.edit_text(message)


@main_router.callback_query(F.data == "sales_opportunities")
async def show_sales_opportunities(callback: types.CallbackQuery):
    """Show sales opportunities"""
    if not config.AGENTIC_MODE:
        await callback.answer("Agentic features are not enabled.")
        return
    
    await handle_user_interaction(callback.from_user.id, "view_opportunities")
    
    # This would typically fetch real opportunities from the database
    message = (
        "🎯 **Sales Opportunities**\n\n"
        "The agentic system is continuously analyzing user behavior to identify:\n\n"
        "• **High-engagement users** who haven't purchased yet\n"
        "• **Cart abandoners** who need follow-up\n"
        "• **Returning customers** ready for cross-selling\n"
        "• **At-risk customers** who need retention campaigns\n\n"
        "🤖 **Active monitoring**: 24/7 lead generation and scoring"
    )
    
    await callback.message.edit_text(message)


@main_router.callback_query(F.data == "smart_pricing")
async def show_smart_pricing(callback: types.CallbackQuery):
    """Show smart pricing information"""
    if not config.AGENTIC_MODE:
        await callback.answer("Agentic features are not enabled.")
        return
    
    await handle_user_interaction(callback.from_user.id, "view_pricing")
    
    message = (
        "💰 **Smart Pricing System**\n\n"
        "The agentic system continuously optimizes pricing based on:\n\n"
        "• **Market Conditions**: Real-time competitor analysis\n"
        "• **Demand Patterns**: Usage trends and seasonal factors\n"
        "• **Cost Fluctuations**: OpenRouter pricing changes\n"
        "• **User Behavior**: Willingness to pay analysis\n\n"
        "🤖 **Dynamic Adjustment**: Prices update automatically"
    )
    
    await callback.message.edit_text(message)


@main_router.callback_query(F.data == "auto_inventory")
async def show_auto_inventory(callback: types.CallbackQuery):
    """Show auto inventory information"""
    if not config.AGENTIC_MODE:
        await callback.answer("Agentic features are not enabled.")
        return
    
    await handle_user_interaction(callback.from_user.id, "view_inventory")
    
    message = (
        "📦 **Auto Inventory Management**\n\n"
        "The agentic system automatically manages inventory:\n\n"
        "• **Demand Prediction**: ML-based usage forecasting\n"
        "• **Smart Restocking**: Automatic token procurement\n"
        "• **Cost Optimization**: Best-price token sourcing\n"
        "• **Risk Management**: Buffer stock maintenance\n\n"
        "🤖 **Zero Downtime**: Always available tokens"
    )
    
    await callback.message.edit_text(message)


@main_router.error(F.update.message.as_("message"))
async def error_handler(event: ErrorEvent, message: Message):
    await message.answer("Oops, something went wrong!")
    traceback_str = traceback.format_exc()
    admin_notification = (
        f"Critical error caused by {event.exception}\n\n"
        f"Stack trace:\n{traceback_str}"
    )
    if len(admin_notification) > 4096:
        byte_array = bytearray(admin_notification, 'utf-8')
        admin_notification = BufferedInputFile(byte_array, "exception.txt")
    await NotificationService.send_to_admins(admin_notification, None)


# Enhanced user interaction tracking
@main_router.message(F.text == Localizator.get_text(BotEntity.USER, "all_categories"), IsUserExistFilter())
async def all_categories_enhanced(message: types.message, session: AsyncSession | Session):
    await handle_user_interaction(message.from_user.id, "browse_categories")
    await all_categories_text_message(message, session)


@main_router.message(F.text == Localizator.get_text(BotEntity.USER, "my_profile"), IsUserExistFilter())
async def my_profile_enhanced(message: types.message, session: AsyncSession | Session):
    await handle_user_interaction(message.from_user.id, "view_profile")
    # Call the original handler
    from handlers.user.my_profile import my_profile_text_message
    await my_profile_text_message(message, session)


@main_router.message(F.text == Localizator.get_text(BotEntity.USER, "cart"), IsUserExistFilter())
async def cart_enhanced(message: types.message, session: AsyncSession | Session):
    await handle_user_interaction(message.from_user.id, "view_cart")
    # Call the original handler
    from handlers.user.cart import cart_text_message
    await cart_text_message(message, session)


@main_router.message(F.text == Localizator.get_text(BotEntity.USER, "ai_tokens"), IsUserExistFilter())
async def ai_tokens_enhanced(message: types.message, session: AsyncSession | Session):
    await handle_user_interaction(message.from_user.id, "view_ai_tokens")
    # Call the original handler
    from handlers.user.ai_tokens import ai_tokens_text_message
    await ai_tokens_text_message(message, session)


# Setup routers
throttling_middleware = ThrottlingMiddleware(redis_client)
users_routers = Router()
users_routers.include_routers(
    all_categories_router,
    my_profile_router,
    cart_router,
    ai_tokens_router
)
users_routers.message.middleware(throttling_middleware)
users_routers.callback_query.middleware(throttling_middleware)

# Include conversational AI router with high priority
if config.CONVERSATIONAL_AI_ENABLED:
    main_router.include_router(conversational_ai_router)

main_router.include_router(admin_router)
main_router.include_routers(users_routers)
main_router.message.middleware(DBSessionMiddleware())
main_router.callback_query.middleware(DBSessionMiddleware())


async def main():
    """Main function to start the agentic bot"""
    logging.info("Starting Agentic Claude Token Resale Bot...")
    
    if config.AGENTIC_MODE:
        logging.info("🤖 Agentic mode enabled - autonomous operations active")
    else:
        logging.info("📱 Standard mode - agentic features disabled")
    
    # Include the main router
    dp.include_router(main_router)
    
    # Start the bot
    await dp.start_polling(bot)


if __name__ == '__main__':
    if config.MULTIBOT:
        main_multibot(main_router)
    else:
        asyncio.run(main())
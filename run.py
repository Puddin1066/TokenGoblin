import traceback
from aiogram import types, F, Router
from aiogram.filters import Command
from aiogram.types import ErrorEvent, Message, BufferedInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

import config
from config import SUPPORT_LINK
import logging
from bot import dp, main, redis
from enums.bot_entity import BotEntity
from middleware.database import DBSessionMiddleware
from middleware.throttling_middleware import ThrottlingMiddleware
from models.user import UserDTO
from multibot import main as main_multibot
from handlers.user.token_purchase import TokenPurchaseHandler, TokenPurchaseStates
from handlers.admin.admin import admin_router
from services.notification import NotificationService
from services.user import UserService
from services.token_resale import TokenResaleService
from utils.custom_filters import IsUserExistFilter
from utils.localizator import Localizator

logging.basicConfig(level=logging.INFO)
main_router = Router()


@main_router.message(Command(commands=["start", "help"]))
async def start(message: types.message, session: AsyncSession | Session):
    buy_tokens_button = types.KeyboardButton(text="🪙 Buy Tokens")
    my_orders_button = types.KeyboardButton(text="📊 My Orders")
    faq_button = types.KeyboardButton(text=Localizator.get_text(BotEntity.USER, "faq"))
    help_button = types.KeyboardButton(text=Localizator.get_text(BotEntity.USER, "help"))
    admin_menu_button = types.KeyboardButton(text=Localizator.get_text(BotEntity.ADMIN, "menu"))
    
    telegram_id = message.from_user.id
    await UserService.create_if_not_exist(UserDTO(
        telegram_username=message.from_user.username,
        telegram_id=telegram_id
    ), session)
    
    keyboard = [[buy_tokens_button, my_orders_button], [faq_button, help_button]]
    if telegram_id in config.ADMIN_ID_LIST:
        keyboard.append([admin_menu_button])
    
    start_markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2, keyboard=keyboard)
    
    welcome_text = "🪙 **Welcome to Token Resale Platform!**\n\n"
    welcome_text += "✅ Buy popular tokens instantly\n"
    welcome_text += "✅ Direct delivery to your wallet\n"
    welcome_text += "✅ Real-time market prices\n"
    welcome_text += "✅ Secure & fast transactions\n\n"
    welcome_text += "Use the buttons below to get started!"
    
    await message.answer(welcome_text, reply_markup=start_markup, parse_mode="Markdown")


# Token Purchase Handlers
@main_router.message(F.text == "🪙 Buy Tokens")
async def buy_tokens(message: types.Message):
    await TokenPurchaseHandler.show_token_menu(message, None)

@main_router.message(F.text == "📊 My Orders")
async def my_orders(message: types.Message):
    await TokenPurchaseHandler.show_transaction_history(message)

@main_router.callback_query(F.data.startswith("select_token:"))
async def handle_token_selection(callback: types.CallbackQuery):
    await TokenPurchaseHandler.select_token(callback, None)

@main_router.callback_query(F.data == "confirm_order")
async def handle_order_confirmation(callback: types.CallbackQuery):
    await TokenPurchaseHandler.confirm_order(callback, None)

@main_router.callback_query(F.data == "cancel_purchase")
async def handle_purchase_cancellation(callback: types.CallbackQuery):
    await TokenPurchaseHandler.cancel_purchase(callback, None)

@main_router.message(F.text == Localizator.get_text(BotEntity.USER, "faq"), IsUserExistFilter())
async def faq(message: types.message):
    await message.answer(Localizator.get_text(BotEntity.USER, "faq_string"))


@main_router.message(F.text == Localizator.get_text(BotEntity.USER, "help"), IsUserExistFilter())
async def support(message: types.message):
    admin_keyboard_builder = InlineKeyboardBuilder()

    admin_keyboard_builder.button(text=Localizator.get_text(BotEntity.USER, "help_button"), url=SUPPORT_LINK)
    await message.answer(Localizator.get_text(BotEntity.USER, "help_string"),
                         reply_markup=admin_keyboard_builder.as_markup())


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


throttling_middleware = ThrottlingMiddleware(redis)

# Register middleware and routers for simplified token resale platform
main_router.include_router(admin_router)
main_router.message.middleware(throttling_middleware)
main_router.callback_query.middleware(throttling_middleware)
main_router.message.middleware(DBSessionMiddleware())
main_router.callback_query.middleware(DBSessionMiddleware())

if __name__ == '__main__':
    if config.MULTIBOT:
        main_multibot(main_router)
    else:
        dp.include_router(main_router)
        main()

import logging
from typing import Optional
from urllib.parse import unquote_plus

from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext

from bot.config import config
from bot.database import get_db
from bot.models import User, Campaign, DatabaseHelper
from bot.utils.localization import get_localized_text
from bot.utils.keyboards import get_main_keyboard, get_payment_keyboard
from bot.services.campaign_service import CampaignService
from bot.services.webhook_service import WebhookService

logger = logging.getLogger(__name__)
router = Router()


@router.message(CommandStart())
async def start_command(message: Message, state: FSMContext):
    """
    Handle /start command with deep link support
    Format: /start campaignID|email|abstract_snippet
    """
    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name
    
    # Parse deep link parameters
    campaign_id = None
    email = None
    abstract_snippet = None
    
    if message.text and len(message.text.split()) > 1:
        try:
            payload = message.text.split(maxsplit=1)[1]
            # Decode URL-encoded payload
            payload = unquote_plus(payload)
            
            # Parse payload: campaignID|email|abstract_snippet
            parts = payload.split('|')
            if len(parts) >= 3:
                campaign_id = parts[0].strip()
                email = parts[1].strip()
                abstract_snippet = parts[2].strip()
                
                logger.info(f"Deep link accessed: campaign={campaign_id}, email={email}")
        except Exception as e:
            logger.error(f"Error parsing deep link payload: {e}")
    
    # Get or create user
    with get_db() as db:
        user = DatabaseHelper.get_user_by_telegram_id(db, user_id)
        
        if not user:
            # Create new user
            user = DatabaseHelper.create_user(
                db, 
                telegram_id=user_id,
                username=username,
                first_name=first_name,
                last_name=last_name,
                email=email,
                campaign_id=campaign_id,
                abstract_snippet=abstract_snippet
            )
            
            # Track campaign registration
            if campaign_id:
                await CampaignService.track_registration(campaign_id)
                await WebhookService.send_event("user_registered", {
                    "user_id": user.id,
                    "campaign_id": campaign_id,
                    "email": email
                })
        else:
            # Update existing user with campaign data if provided
            if campaign_id and not user.campaign_id:
                user.campaign_id = campaign_id
                user.email = email or user.email
                user.abstract_snippet = abstract_snippet
                db.commit()
    
    # Update user activity
    user.last_activity = message.date
    db.commit()
    
    # Generate welcome message
    welcome_message = await generate_welcome_message(user, campaign_id, abstract_snippet)
    
    # Send welcome message with keyboard
    keyboard = get_main_keyboard(user.language_code or "en")
    await message.answer(welcome_message, reply_markup=keyboard)


async def generate_welcome_message(user: User, campaign_id: Optional[str], abstract_snippet: Optional[str]) -> str:
    """Generate personalized welcome message"""
    lang = user.language_code or "en"
    
    if abstract_snippet:
        # Personalized message with research context
        greeting = get_localized_text("welcome_with_research", lang)
        
        # Format the message with research context
        message = f"""🧠 {greeting}

{get_localized_text("research_context", lang)}
> "{abstract_snippet}"

{get_localized_text("claude_benefit", lang)}

💡 {get_localized_text("token_explanation", lang)}

🚀 {get_localized_text("get_started", lang)}"""
    else:
        # Standard welcome message
        greeting = get_localized_text("welcome_standard", lang)
        message = f"""🧠 {greeting}

{get_localized_text("claude_intro", lang)}

💡 {get_localized_text("token_explanation", lang)}

🚀 {get_localized_text("get_started", lang)}"""
    
    return message


@router.message(Command("help"))
async def help_command(message: Message):
    """Handle /help command"""
    user_id = message.from_user.id
    
    with get_db() as db:
        user = DatabaseHelper.get_user_by_telegram_id(db, user_id)
        lang = user.language_code if user else "en"
    
    help_text = get_localized_text("help_message", lang)
    await message.answer(help_text)


@router.message(Command("balance"))
async def balance_command(message: Message):
    """Handle /balance command"""
    user_id = message.from_user.id
    
    with get_db() as db:
        user = DatabaseHelper.get_user_by_telegram_id(db, user_id)
        
        if not user:
            await message.answer(get_localized_text("user_not_found", "en"))
            return
        
        lang = user.language_code or "en"
        balance_text = get_localized_text("balance_info", lang).format(
            balance=user.token_balance,
            total_purchased=user.total_tokens_purchased,
            total_used=user.total_tokens_used
        )
        
        # Add purchase button if balance is low
        if user.token_balance < 1000:
            keyboard = get_payment_keyboard(lang)
            await message.answer(balance_text, reply_markup=keyboard)
        else:
            await message.answer(balance_text)


@router.message(Command("usage"))
async def usage_command(message: Message):
    """Handle /usage command"""
    user_id = message.from_user.id
    
    with get_db() as db:
        user = DatabaseHelper.get_user_by_telegram_id(db, user_id)
        
        if not user:
            await message.answer(get_localized_text("user_not_found", "en"))
            return
        
        lang = user.language_code or "en"
        
        # Get recent usage
        recent_usage = db.query(TokenUsage).filter(
            TokenUsage.user_id == user.id
        ).order_by(TokenUsage.created_at.desc()).limit(10).all()
        
        if not recent_usage:
            await message.answer(get_localized_text("no_usage_history", lang))
            return
        
        usage_text = get_localized_text("usage_history", lang) + "\n\n"
        
        for usage in recent_usage:
            usage_text += f"• {usage.created_at.strftime('%Y-%m-%d %H:%M')} - {usage.tokens_used} tokens\n"
            if usage.description:
                usage_text += f"  {usage.description}\n"
        
        await message.answer(usage_text)


@router.message(Command("support"))
async def support_command(message: Message):
    """Handle /support command"""
    user_id = message.from_user.id
    
    with get_db() as db:
        user = DatabaseHelper.get_user_by_telegram_id(db, user_id)
        lang = user.language_code if user else "en"
    
    support_text = get_localized_text("support_message", lang).format(
        support_link=config.SUPPORT_LINK
    )
    
    await message.answer(support_text)


@router.message(F.text == "🔄 Refresh")
async def refresh_command(message: Message):
    """Handle refresh button"""
    # Same as balance command
    await balance_command(message)


@router.message(F.text == "💰 Buy Tokens")
async def buy_tokens_command(message: Message):
    """Handle buy tokens button"""
    user_id = message.from_user.id
    
    with get_db() as db:
        user = DatabaseHelper.get_user_by_telegram_id(db, user_id)
        
        if not user:
            await message.answer(get_localized_text("user_not_found", "en"))
            return
        
        lang = user.language_code or "en"
        
        # Show token packages
        keyboard = get_payment_keyboard(lang)
        pricing_text = get_localized_text("token_pricing", lang).format(
            price_per_1k=config.TOKEN_PRICE_PER_1K,
            currency=config.CURRENCY
        )
        
        await message.answer(pricing_text, reply_markup=keyboard)


@router.message(F.text == "ℹ️ About")
async def about_command(message: Message):
    """Handle about button"""
    user_id = message.from_user.id
    
    with get_db() as db:
        user = DatabaseHelper.get_user_by_telegram_id(db, user_id)
        lang = user.language_code if user else "en"
    
    about_text = get_localized_text("about_message", lang)
    await message.answer(about_text)


# Error handler for start router
@router.error()
async def start_error_handler(exception_handler):
    """Handle errors in start router"""
    logger.error(f"Error in start handler: {exception_handler.exception}")
    return True
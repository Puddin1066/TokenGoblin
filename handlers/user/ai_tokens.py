from aiogram import types, Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from callbacks import AITokenCallback
from enums.bot_entity import BotEntity
from services.ai_token_service import AITokenService
from utils.custom_filters import IsUserExistFilter
from utils.localizator import Localizator

ai_tokens_router = Router()
ai_token_service = AITokenService()


@ai_tokens_router.message(F.text == Localizator.get_text(BotEntity.USER, "ai_tokens"), IsUserExistFilter())
async def ai_tokens_text_message(message: Message, session: AsyncSession | Session):
    await show_ai_token_packages(message=message, session=session)


async def show_ai_token_packages(**kwargs):
    """Show available AI token packages"""
    message = kwargs.get("message") or kwargs.get("callback")
    session = kwargs.get("session")
    
    try:
        # Get available packages
        packages = await ai_token_service.get_available_token_packages()
        
        kb_builder = InlineKeyboardBuilder()
        msg = "🤖 **AI Token Packages**\n\n"
        msg += "Choose a package to get started with Claude AI:\n\n"
        
        for i, package in enumerate(packages):
            if package.get('available', False):
                msg += f"**{package['name']}** - {package['tokens']:,} tokens\n"
                msg += f"💵 ${package['usd_price']:.2f} ({package['crypto_price']:.4f} {package['crypto_type']})\n"
                msg += f"📝 {package['description']}\n\n"
                
                kb_builder.button(
                    text=f"Buy {package['name']} - ${package['usd_price']:.2f}",
                    callback_data=AITokenCallback.create(1, package_id=i, tokens=package['tokens'])
                )
            else:
                msg += f"**{package['name']}** - {package['tokens']:,} tokens\n"
                msg += f"❌ {package.get('error', 'Not available')}\n\n"
        
        kb_builder.button(
            text="Custom Amount",
            callback_data=AITokenCallback.create(2, custom=True)
        )
        
        kb_builder.button(
            text="Back to Main Menu",
            callback_data=AITokenCallback.create(0, back=True)
        )
        
        kb_builder.adjust(1)
        
        if isinstance(message, Message):
            await message.answer(msg, reply_markup=kb_builder.as_markup(), parse_mode="Markdown")
        elif isinstance(message, CallbackQuery):
            await message.message.edit_text(msg, reply_markup=kb_builder.as_markup(), parse_mode="Markdown")
            
    except Exception as e:
        error_msg = "❌ Error loading token packages. Please try again later."
        if isinstance(message, Message):
            await message.answer(error_msg)
        elif isinstance(message, CallbackQuery):
            await message.message.edit_text(error_msg)


async def show_custom_amount_input(**kwargs):
    """Show custom amount input interface"""
    callback = kwargs.get("callback")
    
    msg = "🔢 **Custom Token Amount**\n\n"
    msg += "Enter the number of AI tokens you want to purchase:\n\n"
    msg += "**Requirements:**\n"
    msg += "• Minimum: 100 tokens\n"
    msg += "• Maximum: Based on $20 USD limit\n"
    msg += "• Payment in USDT or BTC\n\n"
    msg += "Type your desired token count:"
    
    kb_builder = InlineKeyboardBuilder()
    kb_builder.button(
        text="Back to Packages",
        callback_data=AITokenCallback.create(0, back=True)
    )
    
    await callback.message.edit_text(msg, reply_markup=kb_builder.as_markup(), parse_mode="Markdown")


async def process_custom_amount(**kwargs):
    """Process custom token amount input"""
    message = kwargs.get("message")
    session = kwargs.get("session")
    
    try:
        # Parse token count
        token_count = int(message.text.strip())
        
        # Validate the order
        is_valid, error_msg = await ai_token_service.validate_token_order(token_count)
        
        if not is_valid:
            await message.answer(f"❌ {error_msg}\n\nPlease try a different amount.")
            return
        
        # Calculate pricing
        pricing = await ai_token_service.calculate_token_order_price(token_count, 'USDT_TRC20')
        
        # Show pricing confirmation
        msg = f"💰 **Order Summary**\n\n"
        msg += f"**Tokens:** {token_count:,}\n"
        msg += f"**Base Cost:** ${pricing['base_usd_cost']:.2f}\n"
        msg += f"**Markup (20%):** ${pricing['markup_amount']:.2f}\n"
        msg += f"**Total:** ${pricing['total_usd_cost']:.2f}\n"
        msg += f"**Payment:** {pricing['crypto_amount']:.4f} {pricing['crypto_type']}\n\n"
        msg += "Proceed with payment?"
        
        kb_builder = InlineKeyboardBuilder()
        kb_builder.button(
            text="Pay Now",
            callback_data=AITokenCallback.create(3, tokens=token_count, confirm=True)
        )
        kb_builder.button(
            text="Cancel",
            callback_data=AITokenCallback.create(0, back=True)
        )
        
        await message.answer(msg, reply_markup=kb_builder.as_markup(), parse_mode="Markdown")
        
    except ValueError:
        await message.answer("❌ Please enter a valid number of tokens.")
    except Exception as e:
        await message.answer(f"❌ Error processing request: {str(e)}")


async def create_token_order(**kwargs):
    """Create a new token order and show payment details"""
    callback = kwargs.get("callback")
    session = kwargs.get("session")
    
    try:
        unpacked_cb = AITokenCallback.unpack(callback.data)
        token_count = unpacked_cb.tokens
        user_id = callback.from_user.id
        
        # Create the order
        order_result = await ai_token_service.create_token_order(
            user_id=user_id,
            token_count=token_count,
            crypto_type='USDT_TRC20'
        )
        
        order_data = order_result['order']
        payment_data = order_result['payment']
        pricing_data = order_result['pricing']
        
        # Show payment instructions
        msg = f"💳 **Payment Instructions**\n\n"
        msg += f"**Order ID:** `{order_data['order_id']}`\n"
        msg += f"**Tokens:** {token_count:,}\n"
        msg += f"**Amount:** {pricing_data['crypto_amount']:.4f} {pricing_data['crypto_type']}\n"
        msg += f"**Address:** `{payment_data['address']}`\n\n"
        msg += "**Instructions:**\n"
        msg += "1. Send exactly {pricing_data['crypto_amount']:.4f} {pricing_data['crypto_type']}\n"
        msg += "2. Use the address above\n"
        msg += "3. Wait for confirmation (usually 1-3 minutes)\n"
        msg += "4. You'll receive your AI tokens automatically\n\n"
        msg += "⚠️ **Important:**\n"
        msg += "• Send the exact amount\n"
        msg += "• Use the correct network (TRC20 for USDT)\n"
        msg += "• Payment expires in 24 hours"
        
        kb_builder = InlineKeyboardBuilder()
        kb_builder.button(
            text="Copy Address",
            callback_data=AITokenCallback.create(4, action="copy_address", address=payment_data['address'])
        )
        kb_builder.button(
            text="Check Payment Status",
            callback_data=AITokenCallback.create(4, action="check_status", order_id=order_data['order_id'])
        )
        kb_builder.button(
            text="Back to Packages",
            callback_data=AITokenCallback.create(0, back=True)
        )
        
        await callback.message.edit_text(msg, reply_markup=kb_builder.as_markup(), parse_mode="Markdown")
        
    except Exception as e:
        error_msg = f"❌ Error creating order: {str(e)}"
        await callback.message.edit_text(error_msg)


async def handle_payment_action(**kwargs):
    """Handle payment-related actions (copy address, check status)"""
    callback = kwargs.get("callback")
    
    unpacked_cb = AITokenCallback.unpack(callback.data)
    action = unpacked_cb.action
    
    if action == "copy_address":
        address = unpacked_cb.address
        await callback.answer(f"Address copied: {address}")
        
    elif action == "check_status":
        order_id = unpacked_cb.order_id
        # In production, this would check the actual payment status
        await callback.answer("Payment status: Pending. Please wait 1-3 minutes for confirmation.")


async def show_order_history(**kwargs):
    """Show user's order history"""
    callback = kwargs.get("callback")
    session = kwargs.get("session")
    
    # In production, this would fetch from database
    msg = "📋 **Order History**\n\n"
    msg += "No orders found.\n\n"
    msg += "Your completed orders will appear here."
    
    kb_builder = InlineKeyboardBuilder()
    kb_builder.button(
        text="Back to Packages",
        callback_data=AITokenCallback.create(0, back=True)
    )
    
    await callback.message.edit_text(msg, reply_markup=kb_builder.as_markup(), parse_mode="Markdown")


@ai_tokens_router.callback_query(AITokenCallback.filter(), IsUserExistFilter())
async def navigate_ai_tokens(callback: CallbackQuery, callback_data: AITokenCallback, session: AsyncSession | Session):
    current_level = callback_data.level
    
    levels = {
        0: show_ai_token_packages,
        1: create_token_order,
        2: show_custom_amount_input,
        3: create_token_order,
        4: handle_payment_action,
        5: show_order_history
    }
    
    current_level_function = levels.get(current_level)
    
    if current_level_function:
        kwargs = {
            "callback": callback,
            "session": session,
        }
        await current_level_function(**kwargs)
    else:
        await callback.answer("Invalid action")


@ai_tokens_router.message(lambda message: message.text and message.text.isdigit())
async def handle_custom_amount_input(message: Message, session: AsyncSession | Session):
    """Handle custom amount input from user"""
    await process_custom_amount(message=message, session=session) 
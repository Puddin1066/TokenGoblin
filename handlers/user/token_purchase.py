from aiogram import types
from aiogram.types import CallbackQuery, Message, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from services.token_resale import TokenResaleService, PaymentMethod
from db import get_db_session, session_commit
from repositories.transaction import TransactionRepository
from utils.localizator import Localizator


class TokenPurchaseStates(StatesGroup):
    selecting_token = State()
    entering_amount = State()
    entering_address = State()
    confirming_order = State()


class TokenPurchaseHandler:
    
    @staticmethod
    async def show_token_menu(message: Message, state: FSMContext):
        """Show available tokens for purchase"""
        await state.clear()
        
        try:
            tokens = await TokenResaleService.get_supported_tokens()
            
            kb_builder = InlineKeyboardBuilder()
            
            for token in tokens:
                kb_builder.button(
                    text=f"{token['symbol']} - ${token['price_usd']:.2f}",
                    callback_data=f"select_token:{token['symbol']}"
                )
            
            kb_builder.adjust(1)
            
            text = "🪙 **Token Purchase Platform**\n\n"
            text += "Select a token to purchase:\n"
            text += "✅ Instant delivery to your wallet\n"
            text += "✅ Real-time market prices\n"
            text += "✅ 2% service fee + gas costs\n\n"
            
            for token in tokens:
                text += f"**{token['symbol']}**: ${token['price_usd']:.2f}\n"
            
            await message.answer(text, reply_markup=kb_builder.as_markup(), parse_mode="Markdown")
            
        except Exception as e:
            await message.answer(f"❌ Error loading tokens: {str(e)}")
    
    @staticmethod
    async def select_token(callback: CallbackQuery, state: FSMContext):
        """Handle token selection"""
        token_symbol = callback.data.split(":")[1]
        
        await state.update_data(token_symbol=token_symbol)
        await state.set_state(TokenPurchaseStates.entering_amount)
        
        kb_builder = InlineKeyboardBuilder()
        kb_builder.button(text="❌ Cancel", callback_data="cancel_purchase")
        
        try:
            price = await TokenResaleService._get_token_price(token_symbol)
            
            text = f"💰 **Purchase {token_symbol}**\n\n"
            text += f"Current price: **${price:.2f}**\n\n"
            text += "Enter the amount you want to spend (in USD):\n"
            text += "Example: 100 (for $100 worth of tokens)\n\n"
            text += "⚠️ Minimum: $10\n"
            text += "⚠️ Maximum: $10,000"
            
            await callback.message.edit_text(
                text, 
                reply_markup=kb_builder.as_markup(),
                parse_mode="Markdown"
            )
            
        except Exception as e:
            await callback.answer(f"❌ Error: {str(e)}", show_alert=True)
    
    @staticmethod
    async def enter_amount(message: Message, state: FSMContext):
        """Handle amount input"""
        try:
            amount = float(message.text)
            
            if amount < 10:
                await message.answer("❌ Minimum purchase amount is $10")
                return
            
            if amount > 10000:
                await message.answer("❌ Maximum purchase amount is $10,000")
                return
            
            await state.update_data(payment_amount=amount, payment_currency="USD")
            await state.set_state(TokenPurchaseStates.entering_address)
            
            data = await state.get_data()
            token_symbol = data['token_symbol']
            
            kb_builder = InlineKeyboardBuilder()
            kb_builder.button(text="❌ Cancel", callback_data="cancel_purchase")
            
            text = f"📍 **Wallet Address**\n\n"
            text += f"Enter your **{token_symbol}** wallet address where you want to receive the tokens:\n\n"
            text += "⚠️ Make sure the address is correct!\n"
            text += "⚠️ We cannot recover tokens sent to wrong addresses"
            
            await message.answer(text, reply_markup=kb_builder.as_markup(), parse_mode="Markdown")
            
        except ValueError:
            await message.answer("❌ Please enter a valid number")
    
    @staticmethod
    async def enter_address(message: Message, state: FSMContext):
        """Handle wallet address input"""
        address = message.text.strip()
        
        data = await state.get_data()
        token_symbol = data['token_symbol']
        
        # Validate address format
        if not TokenResaleService._validate_address(token_symbol, address):
            await message.answer(f"❌ Invalid {token_symbol} address format. Please try again.")
            return
        
        await state.update_data(recipient_address=address)
        await state.set_state(TokenPurchaseStates.confirming_order)
        
        # Calculate order details
        try:
            payment_amount = data['payment_amount']
            token_amount, fees = await TokenResaleService._calculate_token_amount(
                payment_amount, "USD", token_symbol
            )
            
            await state.update_data(token_amount=token_amount, fees=fees)
            
            kb_builder = InlineKeyboardBuilder()
            kb_builder.row(
                InlineKeyboardButton(text="✅ Confirm Order", callback_data="confirm_order"),
                InlineKeyboardButton(text="❌ Cancel", callback_data="cancel_purchase")
            )
            
            text = f"📋 **Order Summary**\n\n"
            text += f"**Token**: {token_symbol}\n"
            text += f"**Payment**: ${payment_amount:.2f} USD\n"
            text += f"**Token Amount**: {token_amount:.6f} {token_symbol}\n"
            text += f"**Service Fee**: ${fees:.2f}\n"
            text += f"**Recipient**: `{address}`\n\n"
            text += "✅ Confirm to proceed with payment"
            
            await message.answer(text, reply_markup=kb_builder.as_markup(), parse_mode="Markdown")
            
        except Exception as e:
            await message.answer(f"❌ Error calculating order: {str(e)}")
    
    @staticmethod
    async def confirm_order(callback: CallbackQuery, state: FSMContext):
        """Create the order and show payment instructions"""
        data = await state.get_data()
        
        async with get_db_session() as session:
            try:
                # Create transaction
                transaction = await TokenResaleService.create_token_order(
                    user_telegram_id=callback.from_user.id,
                    payment_method=PaymentMethod.FIAT,  # Default to fiat for now
                    payment_amount=data['payment_amount'],
                    payment_currency=data['payment_currency'],
                    token_symbol=data['token_symbol'],
                    recipient_address=data['recipient_address'],
                    session=session
                )
                
                await session_commit(session)
                
                kb_builder = InlineKeyboardBuilder()
                kb_builder.button(text="💳 Pay with Card", callback_data=f"pay_fiat:{transaction.id}")
                kb_builder.button(text="₿ Pay with Crypto", callback_data=f"pay_crypto:{transaction.id}")
                kb_builder.button(text="📊 Check Status", callback_data=f"check_status:{transaction.id}")
                kb_builder.adjust(2, 1)
                
                text = f"✅ **Order Created!**\n\n"
                text += f"**Order ID**: `{transaction.id}`\n"
                text += f"**Amount**: ${data['payment_amount']:.2f} USD\n"
                text += f"**Tokens**: {data['token_amount']:.6f} {data['token_symbol']}\n\n"
                text += "Choose your payment method:"
                
                await callback.message.edit_text(
                    text,
                    reply_markup=kb_builder.as_markup(),
                    parse_mode="Markdown"
                )
                
                await state.clear()
                
            except Exception as e:
                await callback.answer(f"❌ Error creating order: {str(e)}", show_alert=True)
    
    @staticmethod
    async def cancel_purchase(callback: CallbackQuery, state: FSMContext):
        """Cancel the purchase process"""
        await state.clear()
        
        text = "❌ Purchase cancelled.\n\n"
        text += "Use /buy to start a new purchase."
        
        await callback.message.edit_text(text)
    
    @staticmethod
    async def show_transaction_history(message: Message):
        """Show user's transaction history"""
        async with get_db_session() as session:
            try:
                transactions = await TransactionRepository.get_by_user(
                    message.from_user.id, 
                    session,
                    limit=5
                )
                
                if not transactions:
                    await message.answer("📝 No transaction history found.")
                    return
                
                text = "📊 **Your Recent Transactions**\n\n"
                
                for tx in transactions:
                    status_emoji = {
                        "pending_payment": "⏳",
                        "processing": "⚙️", 
                        "completed": "✅",
                        "failed": "❌",
                        "refunded": "🔄"
                    }
                    
                    emoji = status_emoji.get(tx.status.value, "❓")
                    
                    text += f"{emoji} **Order #{tx.id}**\n"
                    text += f"   {tx.token_amount:.6f} {tx.token_symbol}\n"
                    text += f"   ${tx.payment_amount:.2f} → Status: {tx.status.value}\n"
                    
                    if tx.tx_hash:
                        text += f"   TX: `{tx.tx_hash[:16]}...`\n"
                    
                    text += f"   {tx.created_at.strftime('%Y-%m-%d %H:%M')}\n\n"
                
                await message.answer(text, parse_mode="Markdown")
                
            except Exception as e:
                await message.answer(f"❌ Error loading history: {str(e)}")


# Callback handlers mapping
token_purchase_handlers = {
    "show_tokens": TokenPurchaseHandler.show_token_menu,
    "select_token": TokenPurchaseHandler.select_token,
    "confirm_order": TokenPurchaseHandler.confirm_order,
    "cancel_purchase": TokenPurchaseHandler.cancel_purchase,
}
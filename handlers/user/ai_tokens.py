from aiogram import Router, F, types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from callbacks import AITokenCallback, TokenManagementCallback
from enums.bot_entity import BotEntity
from middleware.database import DBSessionMiddleware
from middleware.throttling_middleware import ThrottlingMiddleware
from services.ai_token_service import AITokenService
from services.user import UserService
from utils.custom_filters import IsUserExistFilter
from utils.localizator import Localizator
from bot import redis
import config

ai_tokens_router = Router()
throttling_middleware = ThrottlingMiddleware(redis)
ai_tokens_router.message.middleware(throttling_middleware)
ai_tokens_router.callback_query.middleware(throttling_middleware)
ai_tokens_router.message.middleware(DBSessionMiddleware())
ai_tokens_router.callback_query.middleware(DBSessionMiddleware())

token_service = AITokenService()


@ai_tokens_router.message(F.text == "🤖 AI Tokens", IsUserExistFilter())
async def ai_tokens_menu(message: types.Message, session: AsyncSession | Session):
    """Main AI tokens menu"""
    keyboard_builder = InlineKeyboardBuilder()
    
    keyboard_builder.button(
        text="🛒 Browse Token Packages",
        callback_data=AITokenCallback.create(level=1, action="browse").pack()
    )
    keyboard_builder.button(
        text="📊 My Token Allocations", 
        callback_data=TokenManagementCallback.create(level=1, action="view").pack()
    )
    keyboard_builder.button(
        text="📈 Popular Models",
        callback_data=AITokenCallback.create(level=1, action="popular").pack()
    )
    keyboard_builder.button(
        text="💡 How It Works",
        callback_data=AITokenCallback.create(level=1, action="help").pack()
    )
    
    keyboard_builder.adjust(2, 1, 1)
    
    text = """
🤖 **AI Token Arbitrage Marketplace**

Welcome to the global AI token marketplace! Here you can purchase AI tokens for popular models at competitive prices.

✨ **What we offer:**
• Access to restricted AI models
• Competitive pricing with transparent markup
• Instant token delivery
• Global access regardless of location

🌍 **Serving customers worldwide** - especially in regions with limited AI access.

Choose an option below to get started:
"""
    
    await message.answer(text, reply_markup=keyboard_builder.as_markup())


@ai_tokens_router.callback_query(AITokenCallback.filter(F.action == "browse"))
async def browse_packages(callback: types.CallbackQuery, callback_data: AITokenCallback, 
                          session: AsyncSession | Session):
    """Browse available token packages"""
    
    packages = await token_service.get_available_packages(session)
    
    if not packages:
        await callback.message.edit_text(
            "🚫 No token packages available at the moment.\n\n"
            "Please check back later or contact support."
        )
        return
    
    keyboard_builder = InlineKeyboardBuilder()
    
    # Paginate packages
    page = callback_data.page
    items_per_page = config.PAGE_ENTRIES
    start_idx = page * items_per_page
    end_idx = start_idx + items_per_page
    page_packages = packages[start_idx:end_idx]
    
    for package in page_packages:
        button_text = f"🧠 {package['model_access'][:20]} - {package['token_count']:,} tokens (${package['price']:.3f})"
        keyboard_builder.button(
            text=button_text,
            callback_data=AITokenCallback.create(
                level=2, package_id=package["id"], action="details"
            ).pack()
        )
    
    # Pagination controls
    if page > 0:
        keyboard_builder.button(
            text="⬅️ Previous",
            callback_data=AITokenCallback.create(
                level=1, action="browse", page=page-1
            ).pack()
        )
    
    if end_idx < len(packages):
        keyboard_builder.button(
            text="Next ➡️",
            callback_data=AITokenCallback.create(
                level=1, action="browse", page=page+1
            ).pack()
        )
    
    keyboard_builder.button(
        text="🔙 Back to Menu",
        callback_data=AITokenCallback.create(level=0).pack()
    )
    
    keyboard_builder.adjust(1)
    
    text = f"""
🛒 **Available Token Packages** (Page {page + 1})

Select a package to view details and purchase:

📊 Showing {len(page_packages)} of {len(packages)} packages
"""
    
    await callback.message.edit_text(text, reply_markup=keyboard_builder.as_markup())


@ai_tokens_router.callback_query(AITokenCallback.filter(F.action == "details"))
async def package_details(callback: types.CallbackQuery, callback_data: AITokenCallback,
                          session: AsyncSession | Session):
    """Show detailed information about a token package"""
    
    packages = await token_service.get_available_packages(session)
    package = next((p for p in packages if p["id"] == callback_data.package_id), None)
    
    if not package:
        await callback.answer("Package not found", show_alert=True)
        return
    
    keyboard_builder = InlineKeyboardBuilder()
    
    keyboard_builder.button(
        text="💳 Purchase Package",
        callback_data=AITokenCallback.create(
            level=3, package_id=package["id"], action="purchase", confirmation=False
        ).pack()
    )
    keyboard_builder.button(
        text="🔙 Back to Browse",
        callback_data=AITokenCallback.create(level=1, action="browse").pack()
    )
    
    keyboard_builder.adjust(1)
    
    # Calculate value proposition
    daily_limit_text = f"\n📊 **Daily Limit:** {package['daily_limit']:,} tokens" if package['daily_limit'] else ""
    profit_margin = package['profit_margin']
    
    text = f"""
🧠 **{package['model_access']}**

📦 **Package Details:**
• **Tokens:** {package['token_count']:,}
• **Price:** ${package['price']:.4f} USD
• **Expires:** {package['expiry_days']} days{daily_limit_text}

📝 **Description:**
{package['description']}

🏷️ **Category:** {package['category']} > {package['subcategory']}

💰 **Pricing:**
• **Our Price:** ${package['price']:.4f}
• **Market Advantage:** Instant global access
• **Value:** Perfect for regions with AI restrictions

🔥 **Why Choose Us:**
✅ Instant delivery
✅ Global access 
✅ Competitive rates
✅ Reliable service
✅ 24/7 support

Ready to purchase?
"""
    
    await callback.message.edit_text(text, reply_markup=keyboard_builder.as_markup())


@ai_tokens_router.callback_query(AITokenCallback.filter(F.action == "purchase"))
async def purchase_package(callback: types.CallbackQuery, callback_data: AITokenCallback,
                           session: AsyncSession | Session):
    """Handle token package purchase"""
    
    user_id = callback.from_user.id
    
    if not callback_data.confirmation:
        # Show confirmation
        packages = await token_service.get_available_packages(session)
        package = next((p for p in packages if p["id"] == callback_data.package_id), None)
        
        if not package:
            await callback.answer("Package not found", show_alert=True)
            return
        
        # Check user balance
        user = await UserService.get_by_telegram_id(user_id, session)
        if not user or user.balance < package['price']:
            await callback.answer(
                f"Insufficient balance! You need ${package['price']:.4f} but have ${user.balance if user else 0:.4f}",
                show_alert=True
            )
            return
        
        keyboard_builder = InlineKeyboardBuilder()
        keyboard_builder.button(
            text="✅ Confirm Purchase",
            callback_data=AITokenCallback.create(
                level=3, package_id=package["id"], action="purchase", confirmation=True
            ).pack()
        )
        keyboard_builder.button(
            text="❌ Cancel",
            callback_data=AITokenCallback.create(
                level=2, package_id=package["id"], action="details"
            ).pack()
        )
        
        text = f"""
🛒 **Confirm Purchase**

**Package:** {package['model_access']}
**Tokens:** {package['token_count']:,}
**Price:** ${package['price']:.4f}
**Your Balance:** ${user.balance:.4f}
**After Purchase:** ${user.balance - package['price']:.4f}

⚠️ **This purchase is final.** You will receive:
1. A unique API key for token access
2. Instant activation 
3. {package['expiry_days']} days of validity

Proceed with purchase?
"""
        
        await callback.message.edit_text(text, reply_markup=keyboard_builder.as_markup())
        return
    
    # Process purchase
    await callback.message.edit_text("🔄 Processing your purchase...")
    
    # Get user for balance deduction
    user = await UserService.get_by_telegram_id(user_id, session)
    if not user:
        await callback.message.edit_text("❌ Error: User not found. Please restart the bot.")
        return
    
    # Attempt purchase
    result = await token_service.purchase_token_package(
        package_id=callback_data.package_id,
        user_id=user.id,
        session=session
    )
    
    if result["success"]:
        # Deduct balance
        packages = await token_service.get_available_packages(session)
        package = next((p for p in packages if p["id"] == callback_data.package_id), None)
        
        await UserService.change_balance(user_id, -package['price'], session)
        
        # Send success message
        keyboard_builder = InlineKeyboardBuilder()
        keyboard_builder.button(
            text="📊 View My Tokens",
            callback_data=TokenManagementCallback.create(level=1, action="view").pack()
        )
        keyboard_builder.button(
            text="🛒 Buy More",
            callback_data=AITokenCallback.create(level=1, action="browse").pack()
        )
        
        success_text = f"""
✅ **Purchase Successful!**

{result['delivery_info']}

🎉 **Next Steps:**
1. Save your API key securely
2. Start using AI tokens immediately
3. Monitor usage in "My Tokens"

Thank you for your business! 🚀
"""
        
        await callback.message.edit_text(success_text, reply_markup=keyboard_builder.as_markup())
        
    else:
        await callback.message.edit_text(f"❌ Purchase failed: {result['error']}")


@ai_tokens_router.callback_query(TokenManagementCallback.filter(F.action == "view"))
async def view_allocations(callback: types.CallbackQuery, callback_data: TokenManagementCallback,
                           session: AsyncSession | Session):
    """View user's token allocations"""
    
    user_id = callback.from_user.id
    user = await UserService.get_by_telegram_id(user_id, session)
    
    if not user:
        await callback.answer("User not found", show_alert=True)
        return
    
    allocations = await token_service.get_user_allocations(user.id, session)
    
    if not allocations:
        text = """
📊 **My Token Allocations**

🚫 You don't have any active token allocations yet.

🛒 Start by purchasing a token package to get access to AI models!
"""
        keyboard_builder = InlineKeyboardBuilder()
        keyboard_builder.button(
            text="🛒 Browse Packages",
            callback_data=AITokenCallback.create(level=1, action="browse").pack()
        )
        
        await callback.message.edit_text(text, reply_markup=keyboard_builder.as_markup())
        return
    
    # Show allocations
    text = "📊 **My Token Allocations**\n\n"
    
    for idx, allocation in enumerate(allocations, 1):
        status_emoji = "🟢" if allocation['is_active'] else "🔴"
        usage_percent = ((allocation['total_tokens'] - allocation['remaining_tokens']) / allocation['total_tokens']) * 100
        
        text += f"""
{status_emoji} **Allocation #{idx}**
🧠 **Model:** {allocation['model_access']}
🎯 **Remaining:** {allocation['remaining_tokens']:,} / {allocation['total_tokens']:,} ({usage_percent:.1f}% used)
⏰ **Expires:** {allocation['expires_at'].strftime('%Y-%m-%d %H:%M')}
🔑 **API Key:** {allocation['api_key']}
📊 **Requests:** {allocation['total_requests']}
"""
        
        if allocation['last_used']:
            text += f"🕐 **Last Used:** {allocation['last_used'].strftime('%Y-%m-%d %H:%M')}\n"
        
        text += "\n"
    
    keyboard_builder = InlineKeyboardBuilder()
    keyboard_builder.button(
        text="🛒 Buy More Tokens",
        callback_data=AITokenCallback.create(level=1, action="browse").pack()
    )
    keyboard_builder.button(
        text="🔙 Back to Menu",
        callback_data=AITokenCallback.create(level=0).pack()
    )
    
    await callback.message.edit_text(text, reply_markup=keyboard_builder.as_markup())


@ai_tokens_router.callback_query(AITokenCallback.filter(F.action == "help"))
async def how_it_works(callback: types.CallbackQuery):
    """Explain how the AI token arbitrage system works"""
    
    text = """
💡 **How AI Token Arbitrage Works**

🌍 **The Problem:**
Many regions have limited or no access to advanced AI models due to geographic restrictions, regulations, or payment barriers.

💰 **Our Solution:**
We purchase AI tokens in bulk from providers like OpenRouter and resell them to customers worldwide at fair prices.

🔄 **The Process:**
1. **We Buy:** Bulk purchase tokens at wholesale rates
2. **You Buy:** Purchase token packages through our bot
3. **Instant Access:** Get API keys for immediate use
4. **Global Access:** Use AI models regardless of location

💳 **Payment Methods:**
• Cryptocurrency (Bitcoin, Ethereum, etc.)
• Multiple stablecoins supported
• Instant processing

🛡️ **Benefits:**
✅ **Bypass Restrictions:** Access AI models from anywhere
✅ **Competitive Pricing:** Fair markup on wholesale rates  
✅ **Instant Delivery:** Get access in seconds
✅ **No KYC Required:** Anonymous purchases
✅ **24/7 Support:** Always here to help

🔑 **Usage:**
Your API keys work with standard OpenRouter endpoints. Simply replace your API key with ours and start using AI models immediately.

📊 **Transparent Pricing:**
We maintain competitive markups while ensuring sustainable operations and customer support.

Questions? Contact our support team anytime! 🚀
"""
    
    keyboard_builder = InlineKeyboardBuilder()
    keyboard_builder.button(
        text="🛒 Start Buying",
        callback_data=AITokenCallback.create(level=1, action="browse").pack()
    )
    keyboard_builder.button(
        text="🔙 Back to Menu", 
        callback_data=AITokenCallback.create(level=0).pack()
    )
    
    await callback.message.edit_text(text, reply_markup=keyboard_builder.as_markup())


@ai_tokens_router.callback_query(AITokenCallback.filter(F.level == 0))
async def back_to_main_menu(callback: types.CallbackQuery):
    """Return to main AI tokens menu"""
    await ai_tokens_menu(callback.message, None)
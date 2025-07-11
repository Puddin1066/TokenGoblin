from aiogram import Router, F, types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
import json

from callbacks import AdminMenuCallback
from enums.bot_entity import BotEntity
from middleware.database import DBSessionMiddleware
from middleware.throttling_middleware import ThrottlingMiddleware
from services.ai_token_service import AITokenService
from services.openrouter_api import TokenArbitrageEngine
from repositories.category import CategoryRepository
from repositories.subcategory import SubcategoryRepository
from utils.custom_filters import IsAdminFilter
from utils.localizator import Localizator
from bot import redis
import config

ai_token_admin_router = Router()
throttling_middleware = ThrottlingMiddleware(redis)
ai_token_admin_router.message.middleware(throttling_middleware)
ai_token_admin_router.callback_query.middleware(throttling_middleware)
ai_token_admin_router.message.middleware(DBSessionMiddleware())
ai_token_admin_router.callback_query.middleware(DBSessionMiddleware())

token_service = AITokenService()
arbitrage_engine = TokenArbitrageEngine()


@ai_token_admin_router.callback_query(AdminMenuCallback.filter(F.action == "ai_tokens"))
async def ai_token_admin_menu(callback: types.CallbackQuery, session: AsyncSession | Session):
    """Main AI token admin menu"""
    
    keyboard_builder = InlineKeyboardBuilder()
    
    keyboard_builder.button(
        text="📊 Arbitrage Stats",
        callback_data=AdminMenuCallback.create(level=2, action="ai_stats").pack()
    )
    keyboard_builder.button(
        text="📦 Manage Packages",
        callback_data=AdminMenuCallback.create(level=2, action="ai_packages").pack()
    )
    keyboard_builder.button(
        text="🤖 Popular Models",
        callback_data=AdminMenuCallback.create(level=2, action="ai_models").pack()
    )
    keyboard_builder.button(
        text="🏭 Bulk Create",
        callback_data=AdminMenuCallback.create(level=2, action="ai_bulk").pack()
    )
    keyboard_builder.button(
        text="🧹 Cleanup Expired",
        callback_data=AdminMenuCallback.create(level=2, action="ai_cleanup").pack()
    )
    keyboard_builder.button(
        text="🔙 Back to Admin",
        callback_data=AdminMenuCallback.create(level=0).pack()
    )
    
    keyboard_builder.adjust(2, 2, 1, 1)
    
    # Get quick stats
    stats_7d = await token_service.get_arbitrage_stats(7, session)
    
    text = f"""
🤖 **AI Token Arbitrage Admin**

📊 **7-Day Performance:**
• **Packages Sold:** {stats_7d['total_packages_sold']}
• **Total Profit:** ${stats_7d['total_profit']:.4f}
• **Avg Profit/Package:** ${stats_7d['average_profit_per_package']:.4f}

⚡ **Management Options:**
"""
    
    await callback.message.edit_text(text, reply_markup=keyboard_builder.as_markup())


@ai_token_admin_router.callback_query(AdminMenuCallback.filter(F.action == "ai_stats"))
async def arbitrage_stats(callback: types.CallbackQuery, session: AsyncSession | Session):
    """Show detailed arbitrage statistics"""
    
    # Get stats for different periods
    stats_1d = await token_service.get_arbitrage_stats(1, session)
    stats_7d = await token_service.get_arbitrage_stats(7, session)
    stats_30d = await token_service.get_arbitrage_stats(30, session)
    
    keyboard_builder = InlineKeyboardBuilder()
    keyboard_builder.button(
        text="🔄 Refresh",
        callback_data=AdminMenuCallback.create(level=2, action="ai_stats").pack()
    )
    keyboard_builder.button(
        text="🔙 Back",
        callback_data=AdminMenuCallback.create(level=1, action="ai_tokens").pack()
    )
    
    text = f"""
📊 **AI Token Arbitrage Statistics**

**📅 Last 24 Hours:**
• Packages: {stats_1d['total_packages_sold']}
• Profit: ${stats_1d['total_profit']:.4f}
• Avg/Package: ${stats_1d['average_profit_per_package']:.4f}

**📅 Last 7 Days:**
• Packages: {stats_7d['total_packages_sold']}
• Profit: ${stats_7d['total_profit']:.4f}
• Avg/Package: ${stats_7d['average_profit_per_package']:.4f}

**📅 Last 30 Days:**
• Packages: {stats_30d['total_packages_sold']}
• Profit: ${stats_30d['total_profit']:.4f}
• Avg/Package: ${stats_30d['average_profit_per_package']:.4f}

💡 **Performance Metrics:**
• Daily Growth: {((stats_7d['total_profit'] / 7) - stats_1d['total_profit']) / max(stats_1d['total_profit'], 0.01) * 100:.1f}%
• Weekly Growth: {((stats_30d['total_profit'] / 30 * 7) - stats_7d['total_profit']) / max(stats_7d['total_profit'], 0.01) * 100:.1f}%

🎯 **Efficiency:**
• Current Markup: {config.TOKEN_MARKUP_PERCENTAGE}%
• Min Profit: ${config.MIN_PROFIT_MARGIN}
"""
    
    await callback.message.edit_text(text, reply_markup=keyboard_builder.as_markup())


@ai_token_admin_router.callback_query(AdminMenuCallback.filter(F.action == "ai_packages"))
async def manage_packages(callback: types.CallbackQuery, session: AsyncSession | Session):
    """Manage token packages"""
    
    packages = await token_service.get_available_packages(session)
    
    keyboard_builder = InlineKeyboardBuilder()
    keyboard_builder.button(
        text="➕ Create Package",
        callback_data=AdminMenuCallback.create(level=3, action="ai_create").pack()
    )
    keyboard_builder.button(
        text="🔄 Refresh List",
        callback_data=AdminMenuCallback.create(level=2, action="ai_packages").pack()
    )
    keyboard_builder.button(
        text="🔙 Back",
        callback_data=AdminMenuCallback.create(level=1, action="ai_tokens").pack()
    )
    
    text = f"""
📦 **Token Package Management**

**📋 Current Packages:** {len(packages)}

"""
    
    for i, package in enumerate(packages[:10], 1):  # Show first 10
        profit = package['profit_margin']
        margin_pct = (profit / package['price']) * 100
        
        text += f"""
**{i}.** {package['model_access'][:25]}
   • Tokens: {package['token_count']:,}
   • Price: ${package['price']:.4f}
   • Profit: ${profit:.4f} ({margin_pct:.1f}%)
   • Category: {package['category']}

"""
    
    if len(packages) > 10:
        text += f"\n... and {len(packages) - 10} more packages"
    
    await callback.message.edit_text(text, reply_markup=keyboard_builder.as_markup())


@ai_token_admin_router.callback_query(AdminMenuCallback.filter(F.action == "ai_models"))
async def popular_models(callback: types.CallbackQuery):
    """Show popular AI models for arbitrage"""
    
    models = await arbitrage_engine.get_popular_models()
    
    keyboard_builder = InlineKeyboardBuilder()
    keyboard_builder.button(
        text="🔄 Refresh",
        callback_data=AdminMenuCallback.create(level=2, action="ai_models").pack()
    )
    keyboard_builder.button(
        text="🔙 Back",
        callback_data=AdminMenuCallback.create(level=1, action="ai_tokens").pack()
    )
    
    text = "🤖 **Popular AI Models for Arbitrage**\n\n"
    
    for i, model in enumerate(models[:8], 1):
        pricing = model.get('pricing', {})
        prompt_cost = pricing.get('prompt', 'N/A')
        completion_cost = pricing.get('completion', 'N/A')
        
        text += f"""
**{i}.** {model.get('name', model.get('id', 'Unknown'))[:30]}
   • ID: `{model.get('id', 'unknown')}`
   • Prompt: ${prompt_cost} per token
   • Completion: ${completion_cost} per token
   • Context: {model.get('context_length', 'Unknown')}

"""
    
    text += """
💡 **Usage:**
Send `/create_package <model_id> <tokens> <description>` to create a package for any model.

Example: `/create_package gpt-4 100000 GPT-4 Access Package`
"""
    
    await callback.message.edit_text(text, reply_markup=keyboard_builder.as_markup())


@ai_token_admin_router.callback_query(AdminMenuCallback.filter(F.action == "ai_bulk"))
async def bulk_create_prompt(callback: types.CallbackQuery):
    """Prompt for bulk package creation"""
    
    text = """
🏭 **Bulk Package Creation**

Send a JSON file with package definitions in this format:

```json
[
  {
    "model": "gpt-4",
    "tokens": 100000,
    "description": "GPT-4 Access - 100k tokens",
    "category_id": 1,
    "subcategory_id": 1
  },
  {
    "model": "claude-3-sonnet",
    "tokens": 200000, 
    "description": "Claude 3 Sonnet - 200k tokens",
    "category_id": 1,
    "subcategory_id": 2
  }
]
```

**Required fields:**
• `model`: OpenRouter model ID
• `tokens`: Number of tokens in package
• `description`: Package description
• `category_id`: Category ID (create categories first)
• `subcategory_id`: Subcategory ID

Send the JSON file now:
"""
    
    keyboard_builder = InlineKeyboardBuilder()
    keyboard_builder.button(
        text="❌ Cancel",
        callback_data=AdminMenuCallback.create(level=1, action="ai_tokens").pack()
    )
    
    await callback.message.edit_text(text, reply_markup=keyboard_builder.as_markup())


@ai_token_admin_router.message(F.document, IsAdminFilter())
async def process_bulk_create(message: types.Message, session: AsyncSession | Session):
    """Process bulk package creation from JSON file"""
    
    if not message.document.file_name.endswith('.json'):
        await message.answer("❌ Please send a JSON file.")
        return
    
    try:
        # Download and parse file
        file = await message.bot.get_file(message.document.file_id)
        file_content = await message.bot.download_file(file.file_path)
        
        # Parse JSON
        packages_data = json.loads(file_content.read().decode('utf-8'))
        
        if not isinstance(packages_data, list):
            await message.answer("❌ JSON must contain a list of packages.")
            return
        
        await message.answer("🔄 Processing bulk creation...")
        
        # Create packages
        result = await token_service.create_bulk_packages(packages_data, session)
        
        # Format response
        success_count = result['total_created']
        total_count = len(packages_data)
        
        response = f"""
✅ **Bulk Creation Complete**

📊 **Results:**
• Created: {success_count}/{total_count} packages
• Success Rate: {(success_count/total_count)*100:.1f}%

📋 **Details:**
"""
        
        for item in result['results'][:10]:  # Show first 10
            status_emoji = "✅" if item['status'] == 'created' else "❌"
            response += f"\n{status_emoji} {item['model']}"
            if 'error' in item:
                response += f" - {item['error']}"
        
        if len(result['results']) > 10:
            response += f"\n... and {len(result['results']) - 10} more"
        
        await message.answer(response)
        
    except json.JSONDecodeError:
        await message.answer("❌ Invalid JSON format. Please check your file.")
    except Exception as e:
        await message.answer(f"❌ Error processing file: {str(e)}")


@ai_token_admin_router.callback_query(AdminMenuCallback.filter(F.action == "ai_cleanup"))
async def cleanup_expired(callback: types.CallbackQuery, session: AsyncSession | Session):
    """Clean up expired token allocations"""
    
    await callback.message.edit_text("🧹 Cleaning up expired allocations...")
    
    try:
        count = await token_service.cleanup_expired_allocations(session)
        
        text = f"""
✅ **Cleanup Complete**

🧹 **Expired Allocations Cleaned:** {count}

This removes inactive allocations that have expired to keep the database clean and improve performance.

Last cleanup: {callback.message.date.strftime('%Y-%m-%d %H:%M UTC')}
"""
        
        keyboard_builder = InlineKeyboardBuilder()
        keyboard_builder.button(
            text="🔄 Run Again",
            callback_data=AdminMenuCallback.create(level=2, action="ai_cleanup").pack()
        )
        keyboard_builder.button(
            text="🔙 Back",
            callback_data=AdminMenuCallback.create(level=1, action="ai_tokens").pack()
        )
        
        await callback.message.edit_text(text, reply_markup=keyboard_builder.as_markup())
        
    except Exception as e:
        await callback.message.edit_text(f"❌ Cleanup failed: {str(e)}")


@ai_token_admin_router.message(F.text.startswith("/create_package"), IsAdminFilter())
async def create_single_package(message: types.Message, session: AsyncSession | Session):
    """Create a single token package via command"""
    
    try:
        parts = message.text.split(" ", 3)
        if len(parts) < 4:
            await message.answer(
                "❌ Usage: `/create_package <model_id> <tokens> <description>`\n\n"
                "Example: `/create_package gpt-4 100000 GPT-4 Access Package`"
            )
            return
        
        _, model_id, tokens_str, description = parts
        tokens = int(tokens_str)
        
        # Get or create default categories
        category = await CategoryRepository.get_or_create("AI Models", session)
        subcategory = await SubcategoryRepository.get_or_create("Premium Access", session)
        
        # Create package
        package_data = {
            "model": model_id,
            "tokens": tokens,
            "description": description,
            "category_id": category.id,
            "subcategory_id": subcategory.id
        }
        
        result = await token_service.create_bulk_packages([package_data], session)
        
        if result['total_created'] > 0:
            await message.answer(f"✅ Created package for {model_id} with {tokens:,} tokens!")
        else:
            error = result['results'][0].get('error', 'Unknown error')
            await message.answer(f"❌ Failed to create package: {error}")
            
    except ValueError:
        await message.answer("❌ Invalid token count. Please use a number.")
    except Exception as e:
        await message.answer(f"❌ Error: {str(e)}")


@ai_token_admin_router.message(F.text.startswith("/token_stats"), IsAdminFilter())
async def token_stats_command(message: types.Message, session: AsyncSession | Session):
    """Quick token stats command"""
    
    stats = await token_service.get_arbitrage_stats(7, session)
    balance = await arbitrage_engine.openrouter.get_account_balance()
    
    text = f"""
📊 **Quick Token Stats**

**🏦 OpenRouter Balance:** ${balance:.4f}

**📈 7-Day Performance:**
• Packages Sold: {stats['total_packages_sold']}
• Total Profit: ${stats['total_profit']:.4f}
• Avg Profit: ${stats['average_profit_per_package']:.4f}

**⚙️ Config:**
• Markup: {config.TOKEN_MARKUP_PERCENTAGE}%
• Min Profit: ${config.MIN_PROFIT_MARGIN}
• Bulk Threshold: {config.BULK_DISCOUNT_THRESHOLD:,} tokens
"""
    
    await message.answer(text)
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from models.transaction import TransactionStatus
from repositories.transaction import TransactionRepository
from services.token_resale import TokenResaleService
from utils.localizator import Localizator


class SimplifiedAdminService:
    """Simplified admin service for token resale platform"""
    
    @staticmethod
    async def get_main_menu() -> tuple[str, InlineKeyboardBuilder]:
        """Get simplified admin main menu"""
        kb_builder = InlineKeyboardBuilder()
        
        kb_builder.button(text="📊 Transaction Stats", callback_data="admin:stats")
        kb_builder.button(text="⏳ Pending Orders", callback_data="admin:pending")
        kb_builder.button(text="💰 Platform Balance", callback_data="admin:balance")
        kb_builder.button(text="🔄 Refresh Prices", callback_data="admin:refresh_prices")
        kb_builder.button(text="📈 Daily Summary", callback_data="admin:daily_summary")
        
        kb_builder.adjust(2)
        
        text = "🛠 **Admin Panel - Token Resale Platform**\n\n"
        text += "Select an option to manage the platform:"
        
        return text, kb_builder
    
    @staticmethod
    async def get_transaction_stats(session: AsyncSession | Session) -> str:
        """Get transaction statistics"""
        try:
            # Get all transactions grouped by status
            pending_txs = await TransactionRepository.get_pending_transactions(session)
            
            # Simple stats - in production would use proper SQL aggregation
            total_pending = len([tx for tx in pending_txs if tx.status == TransactionStatus.PENDING_PAYMENT])
            total_processing = len([tx for tx in pending_txs if tx.status == TransactionStatus.PROCESSING])
            
            text = "📊 **Transaction Statistics**\n\n"
            text += f"⏳ **Pending Payment**: {total_pending}\n"
            text += f"⚙️ **Processing**: {total_processing}\n\n"
            
            if pending_txs:
                text += "**Recent Pending Orders:**\n"
                for tx in pending_txs[:5]:  # Show last 5
                    text += f"• Order #{tx.id}: {tx.token_amount:.4f} {tx.token_symbol} (${tx.payment_amount:.2f})\n"
            
            return text
            
        except Exception as e:
            return f"❌ Error loading stats: {str(e)}"
    
    @staticmethod
    async def get_pending_orders(session: AsyncSession | Session) -> str:
        """Get detailed pending orders"""
        try:
            pending_txs = await TransactionRepository.get_pending_transactions(session)
            
            if not pending_txs:
                return "✅ **No pending orders!**\n\nAll transactions are up to date."
            
            text = "⏳ **Pending Orders**\n\n"
            
            for tx in pending_txs[:10]:  # Show up to 10 pending
                status_emoji = "⏳" if tx.status == TransactionStatus.PENDING_PAYMENT else "⚙️"
                
                text += f"{status_emoji} **Order #{tx.id}**\n"
                text += f"   User: {tx.user_telegram_id}\n"
                text += f"   Token: {tx.token_amount:.6f} {tx.token_symbol}\n"
                text += f"   Payment: ${tx.payment_amount:.2f} {tx.payment_currency}\n"
                text += f"   Address: `{tx.recipient_address[:20]}...`\n"
                text += f"   Created: {tx.created_at.strftime('%Y-%m-%d %H:%M')}\n\n"
            
            return text
            
        except Exception as e:
            return f"❌ Error loading pending orders: {str(e)}"
    
    @staticmethod
    async def get_platform_balance() -> str:
        """Get platform token balances and wallet info"""
        try:
            # In production, this would check actual wallet balances
            # For now, show supported tokens and their current prices
            
            tokens = await TokenResaleService.get_supported_tokens()
            
            text = "💰 **Platform Balance & Prices**\n\n"
            text += "**Supported Tokens:**\n"
            
            total_value_usd = 0
            
            for token in tokens:
                # Mock balance - in production would check actual wallet
                mock_balance = 100.0  # Simulate some token balance
                value_usd = mock_balance * token['price_usd']
                total_value_usd += value_usd
                
                text += f"**{token['symbol']}**\n"
                text += f"   Balance: {mock_balance:.4f}\n"
                text += f"   Price: ${token['price_usd']:.2f}\n"
                text += f"   Value: ${value_usd:.2f}\n\n"
            
            text += f"🏦 **Total Portfolio Value**: ${total_value_usd:.2f}\n\n"
            text += "💡 *Note: Integrate with actual wallet APIs for real balances*"
            
            return text
            
        except Exception as e:
            return f"❌ Error loading balance: {str(e)}"
    
    @staticmethod
    async def refresh_token_prices() -> str:
        """Refresh token prices and show updated rates"""
        try:
            tokens = await TokenResaleService.get_supported_tokens()
            
            text = "🔄 **Updated Token Prices**\n\n"
            
            for token in tokens:
                text += f"**{token['symbol']}**: ${token['price_usd']:.2f}\n"
            
            text += f"\n⏰ Last updated: just now"
            
            return text
            
        except Exception as e:
            return f"❌ Error refreshing prices: {str(e)}"
    
    @staticmethod
    async def get_daily_summary(session: AsyncSession | Session) -> str:
        """Get daily transaction summary"""
        try:
            # In production, would use proper date filtering
            # For demo, just show general activity
            
            pending_txs = await TransactionRepository.get_pending_transactions(session)
            
            text = "📈 **Daily Summary**\n\n"
            text += f"📋 **Total Pending Orders**: {len(pending_txs)}\n"
            
            # Calculate total pending value
            total_pending_value = sum(tx.payment_amount for tx in pending_txs)
            text += f"💰 **Pending Transaction Value**: ${total_pending_value:.2f}\n\n"
            
            # Token breakdown
            token_counts = {}
            for tx in pending_txs:
                token_counts[tx.token_symbol] = token_counts.get(tx.token_symbol, 0) + 1
            
            if token_counts:
                text += "**Most Requested Tokens:**\n"
                for token, count in sorted(token_counts.items(), key=lambda x: x[1], reverse=True):
                    text += f"   {token}: {count} orders\n"
            
            text += "\n💡 *Integrate with analytics for detailed reporting*"
            
            return text
            
        except Exception as e:
            return f"❌ Error loading daily summary: {str(e)}"
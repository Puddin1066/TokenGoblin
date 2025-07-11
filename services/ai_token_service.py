from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from db import session_commit
from models.ai_token import AITokenPackageDTO, AITokenAllocationDTO
from repositories.ai_token import AITokenPackageRepository, AITokenAllocationRepository
from services.openrouter_api import OpenRouterAPI, TokenArbitrageEngine
from services.notification import NotificationService
from utils.logging_config import get_logger, log_business_event, log_transaction, log_arbitrage_operation, log_performance, log_user_action
import config

logger = get_logger(__name__)


class AITokenService:
    """Main service for managing AI token arbitrage operations"""
    
    def __init__(self):
        self.openrouter = OpenRouterAPI()
        self.arbitrage_engine = TokenArbitrageEngine()
    
    @log_performance("get_available_packages")
    async def get_available_packages(self, session: AsyncSession | Session) -> List[Dict]:
        """Get all available token packages with formatted pricing"""
        packages = await AITokenPackageRepository.get_available_packages(session)
        
        formatted_packages = []
        for package in packages:
            formatted_packages.append({
                "id": package.id,
                "token_count": package.token_count,
                "model_access": package.model_access,
                "price": package.sell_price,
                "description": package.description,
                "category": package.category.name if package.category else "Unknown",
                "subcategory": package.subcategory.name if package.subcategory else "Unknown",
                "profit_margin": package.sell_price - package.cost_price,
                "expiry_days": package.expiry_days,
                "daily_limit": package.daily_limit
            })
        
        log_business_event("packages_retrieved", 
                          package_count=len(formatted_packages),
                          total_value=sum(p["price"] for p in formatted_packages))
        
        return formatted_packages
    
    @log_performance("purchase_token_package")
    async def purchase_token_package(self, package_id: int, user_id: int, 
                                     session: AsyncSession | Session) -> Dict:
        """Purchase a token package for a user"""
        
        logger.info(f"Processing token package purchase - Package ID: {package_id}, User ID: {user_id}")
        
        # Get package details
        package = await AITokenPackageRepository.get_by_id(package_id, session)
        if not package or not package.is_available:
            logger.warning(f"Package purchase failed - Package {package_id} not available")
            return {"success": False, "error": "Package not available"}
        
        log_user_action(user_id, "token_package_purchase_attempt", 
                       package_id=package_id, 
                       model=package.model_access,
                       tokens=package.token_count,
                       price=package.sell_price)
        
        # Create API key for user
        api_key = await self.openrouter.create_api_key(
            token_limit=package.token_count, 
            expiry_days=package.expiry_days
        )
        
        if not api_key:
            logger.error(f"Failed to create API key for user {user_id}, package {package_id}")
            return {"success": False, "error": "Failed to create API key"}
        
        # Create allocation
        expires_at = datetime.utcnow() + timedelta(days=package.expiry_days)
        allocation_dto = AITokenAllocationDTO(
            user_id=user_id,
            package_id=package_id,
            api_key=api_key,
            remaining_tokens=package.token_count,
            total_tokens=package.token_count,
            expires_at=expires_at
        )
        
        try:
            allocation = await AITokenAllocationRepository.create(allocation_dto, session)
            await session_commit(session)
            
            # Log successful transaction
            log_transaction("token_package_purchase", package.sell_price, user_id,
                           package_id=package_id,
                           model=package.model_access,
                           tokens=package.token_count,
                           api_key_prefix=api_key[:12])
            
            # Log arbitrage operation
            log_arbitrage_operation("package_sale", package.model_access, package.token_count,
                                   package.cost_price, package.sell_price,
                                   user_id=user_id,
                                   allocation_id=allocation.id)
            
            # Send delivery message to user
            delivery_info = await self._format_delivery_message(allocation)
            
            # Notify admins of sale
            await self._notify_admin_of_sale(package, user_id, allocation.api_key)
            
            log_business_event("token_package_sold",
                              package_id=package_id,
                              user_id=user_id,
                              model=package.model_access,
                              tokens=package.token_count,
                              revenue=package.sell_price,
                              profit=package.sell_price - package.cost_price)
            
            logger.info(f"Token package purchase completed successfully - User: {user_id}, Package: {package_id}")
            
            return {
                "success": True,
                "allocation_id": allocation.id,
                "api_key": api_key,
                "token_count": package.token_count,
                "expires_at": expires_at,
                "delivery_info": delivery_info
            }
            
        except Exception as e:
            logger.error(f"Error creating token allocation: {e}", exc_info=True)
            log_business_event("token_purchase_failed",
                              package_id=package_id,
                              user_id=user_id,
                              error=str(e))
            return {"success": False, "error": "Failed to create allocation"}
    
    async def validate_token_usage(self, api_key: str, requested_tokens: int, 
                                   session: AsyncSession | Session) -> Dict:
        """Validate if a token usage request is allowed"""
        
        allocation = await AITokenAllocationRepository.get_by_api_key(api_key, session)
        
        if not allocation:
            return {"valid": False, "error": "Invalid API key"}
        
        if not allocation.is_active:
            return {"valid": False, "error": "API key is inactive"}
        
        if allocation.expires_at <= datetime.utcnow():
            return {"valid": False, "error": "API key has expired"}
        
        if allocation.remaining_tokens < requested_tokens:
            return {"valid": False, "error": "Insufficient tokens"}
        
        # Check daily limit
        if allocation.package.daily_limit:
            now = datetime.utcnow()
            if now.date() > allocation.daily_reset_at.date():
                allocation.tokens_used_today = 0
            
            if allocation.tokens_used_today + requested_tokens > allocation.package.daily_limit:
                return {"valid": False, "error": "Daily limit exceeded"}
        
        return {
            "valid": True,
            "remaining_tokens": allocation.remaining_tokens,
            "model_access": allocation.package.model_access,
            "daily_remaining": (allocation.package.daily_limit - allocation.tokens_used_today) if allocation.package.daily_limit else None
        }
    
    async def consume_tokens(self, api_key: str, token_count: int, 
                             session: AsyncSession | Session) -> bool:
        """Consume tokens from an allocation"""
        
        success = await AITokenAllocationRepository.use_tokens(api_key, token_count, session)
        if success:
            await session_commit(session)
        
        return success
    
    async def get_user_allocations(self, user_id: int, session: AsyncSession | Session) -> List[Dict]:
        """Get all active allocations for a user"""
        
        allocations = await AITokenAllocationRepository.get_by_user(user_id, session)
        
        formatted_allocations = []
        for allocation in allocations:
            formatted_allocations.append({
                "id": allocation.id,
                "api_key": allocation.api_key[:12] + "...",  # Mask API key
                "model_access": allocation.package.model_access,
                "remaining_tokens": allocation.remaining_tokens,
                "total_tokens": allocation.total_tokens,
                "expires_at": allocation.expires_at,
                "is_active": allocation.is_active,
                "last_used": allocation.last_used,
                "total_requests": allocation.total_requests
            })
        
        return formatted_allocations
    
    async def create_bulk_packages(self, model_packages: List[Dict], 
                                   session: AsyncSession | Session) -> Dict:
        """Create multiple token packages for different models"""
        
        results = []
        total_created = 0
        
        for package_data in model_packages:
            try:
                result = await self.arbitrage_engine.create_token_package(
                    model_name=package_data["model"],
                    token_count=package_data["tokens"],
                    description=package_data["description"],
                    category_id=package_data["category_id"],
                    subcategory_id=package_data["subcategory_id"]
                )
                
                if result["success"]:
                    package_dto = AITokenPackageDTO(**result["package"])
                    await AITokenPackageRepository.create(package_dto, session)
                    total_created += 1
                    results.append({"model": package_data["model"], "status": "created"})
                else:
                    results.append({"model": package_data["model"], "status": "failed", "error": result["error"]})
                    
            except Exception as e:
                logger.error(f"Error creating package for {package_data['model']}: {e}")
                results.append({"model": package_data["model"], "status": "error", "error": str(e)})
        
        if total_created > 0:
            await session_commit(session)
        
        return {
            "total_created": total_created,
            "results": results
        }
    
    async def cleanup_expired_allocations(self, session: AsyncSession | Session) -> int:
        """Clean up expired allocations"""
        
        count = await AITokenAllocationRepository.cleanup_expired(session)
        if count > 0:
            await session_commit(session)
            logger.info(f"Cleaned up {count} expired token allocations")
        
        return count
    
    async def get_arbitrage_stats(self, days: int, session: AsyncSession | Session) -> Dict:
        """Get arbitrage performance statistics"""
        
        package_stats = await AITokenPackageRepository.get_profit_stats(days, session)
        
        return {
            "days": days,
            "total_packages_sold": package_stats["total_packages"],
            "total_profit": package_stats["total_profit"],
            "average_profit_per_package": package_stats["avg_profit"],
            "profit_margin_percentage": (package_stats["total_profit"] / (package_stats["total_packages"] * 10)) * 100 if package_stats["total_packages"] > 0 else 0
        }
    
    async def _format_delivery_message(self, allocation) -> str:
        """Format the delivery message for users"""
        
        message = f"""
🚀 **AI Token Package Delivered!**

🔑 **Your API Key:** `{allocation.api_key}`
🧠 **Model Access:** {allocation.package.model_access}
🎯 **Total Tokens:** {allocation.total_tokens:,}
⏰ **Expires:** {allocation.expires_at.strftime('%Y-%m-%d %H:%M UTC')}
"""
        
        if allocation.package.daily_limit:
            message += f"📊 **Daily Limit:** {allocation.package.daily_limit:,} tokens\n"
        
        message += f"""
📖 **Usage Instructions:**
1. Use this API key with OpenRouter-compatible endpoints
2. Your tokens will be automatically deducted from usage
3. Monitor your usage in the bot's "My Tokens" section

⚠️ **Important:** Keep your API key secure and don't share it!
"""
        
        return message
    
    async def _notify_admin_of_sale(self, package, user_id: int, api_key: str):
        """Notify admins of a successful token sale"""
        
        profit = package.sell_price - package.cost_price
        margin_percent = (profit / package.cost_price) * 100
        
        admin_message = f"""
💰 **New AI Token Sale!**

👤 **User ID:** {user_id}
🧠 **Model:** {package.model_access}
🎯 **Tokens:** {package.token_count:,}
💵 **Sale Price:** ${package.sell_price:.4f}
💰 **Profit:** ${profit:.4f} ({margin_percent:.1f}% margin)
🔑 **API Key:** {api_key[:12]}...

📊 **Package Details:**
- Cost Price: ${package.cost_price:.4f}
- Category: {package.category.name}
- Subcategory: {package.subcategory.name}
"""
        
        await NotificationService.send_to_admins(admin_message, None)
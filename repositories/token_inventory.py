from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from sqlalchemy import select, update, and_
from typing import List, Optional, Dict
from datetime import datetime, timedelta

from models.token_inventory import TokenInventory, TokenPurchase, TokenUsage, PricingHistory


class TokenInventoryRepository:
    
    @staticmethod
    async def get_by_model_id(model_id: str, session: AsyncSession | Session) -> Optional[TokenInventory]:
        """Get token inventory by model ID"""
        result = await session.execute(select(TokenInventory).where(TokenInventory.model_id == model_id))
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_all_active(session: AsyncSession | Session) -> List[TokenInventory]:
        """Get all active token inventories"""
        result = await session.execute(select(TokenInventory).where(TokenInventory.is_active == True))
        return result.scalars().all()
    
    @staticmethod
    async def create(inventory: TokenInventory, session: AsyncSession | Session) -> TokenInventory:
        """Create new token inventory"""
        session.add(inventory)
        await session.commit()
        await session.refresh(inventory)
        return inventory
    
    @staticmethod
    async def update(inventory: TokenInventory, session: AsyncSession | Session) -> TokenInventory:
        """Update token inventory"""
        inventory.updated_at = datetime.now()
        await session.commit()
        await session.refresh(inventory)
        return inventory
    
    @staticmethod
    async def reserve_tokens(model_id: str, tokens_to_reserve: int, session: AsyncSession | Session) -> bool:
        """Reserve tokens for a purchase"""
        inventory = await TokenInventoryRepository.get_by_model_id(model_id, session)
        if inventory and inventory.tokens_available >= tokens_to_reserve:
            inventory.tokens_available -= tokens_to_reserve
            inventory.tokens_reserved += tokens_to_reserve
            await TokenInventoryRepository.update(inventory, session)
            return True
        return False
    
    @staticmethod
    async def release_tokens(model_id: str, tokens_to_release: int, session: AsyncSession | Session) -> bool:
        """Release reserved tokens"""
        inventory = await TokenInventoryRepository.get_by_model_id(model_id, session)
        if inventory and inventory.tokens_reserved >= tokens_to_release:
            inventory.tokens_reserved -= tokens_to_release
            inventory.tokens_available += tokens_to_release
            await TokenInventoryRepository.update(inventory, session)
            return True
        return False
    
    @staticmethod
    async def consume_tokens(model_id: str, tokens_to_consume: int, session: AsyncSession | Session) -> bool:
        """Consume reserved tokens"""
        inventory = await TokenInventoryRepository.get_by_model_id(model_id, session)
        if inventory and inventory.tokens_reserved >= tokens_to_consume:
            inventory.tokens_reserved -= tokens_to_consume
            await TokenInventoryRepository.update(inventory, session)
            return True
        return False
    
    @staticmethod
    async def add_tokens(model_id: str, tokens_to_add: int, cost_per_token: float, session: AsyncSession | Session) -> bool:
        """Add tokens to inventory"""
        inventory = await TokenInventoryRepository.get_by_model_id(model_id, session)
        if inventory:
            inventory.tokens_available += tokens_to_add
            inventory.cost_per_token = cost_per_token
            inventory.last_restock_date = datetime.now()
            await TokenInventoryRepository.update(inventory, session)
            return True
        return False
    
    @staticmethod
    async def get_low_inventory_models(threshold: int = 1000, session: AsyncSession | Session) -> List[TokenInventory]:
        """Get models with low inventory"""
        result = await session.execute(
            select(TokenInventory).where(
                and_(
                    TokenInventory.is_active == True,
                    TokenInventory.tokens_available < threshold
                )
            )
        )
        return result.scalars().all()


class TokenPurchaseRepository:
    
    @staticmethod
    async def create(purchase: TokenPurchase, session: AsyncSession | Session) -> TokenPurchase:
        """Create new token purchase record"""
        session.add(purchase)
        await session.commit()
        await session.refresh(purchase)
        return purchase
    
    @staticmethod
    async def get_by_id(purchase_id: int, session: AsyncSession | Session) -> Optional[TokenPurchase]:
        """Get token purchase by ID"""
        result = await session.execute(select(TokenPurchase).where(TokenPurchase.id == purchase_id))
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_recent_purchases(days: int = 30, session: AsyncSession | Session) -> List[TokenPurchase]:
        """Get recent token purchases"""
        cutoff_date = datetime.now() - timedelta(days=days)
        result = await session.execute(
            select(TokenPurchase).where(TokenPurchase.purchase_timestamp >= cutoff_date)
        )
        return result.scalars().all()
    
    @staticmethod
    async def update_status(purchase_id: int, status: str, session: AsyncSession | Session) -> bool:
        """Update purchase status"""
        result = await session.execute(
            update(TokenPurchase).where(TokenPurchase.id == purchase_id).values(status=status)
        )
        await session.commit()
        return result.rowcount > 0


class TokenUsageRepository:
    
    @staticmethod
    async def create(usage: TokenUsage, session: AsyncSession | Session) -> TokenUsage:
        """Create new token usage record"""
        session.add(usage)
        await session.commit()
        await session.refresh(usage)
        return usage
    
    @staticmethod
    async def get_user_usage(user_id: int, days: int = 30, session: AsyncSession | Session) -> List[TokenUsage]:
        """Get user's token usage"""
        cutoff_date = datetime.now() - timedelta(days=days)
        result = await session.execute(
            select(TokenUsage).where(
                and_(
                    TokenUsage.user_id == user_id,
                    TokenUsage.created_at >= cutoff_date
                )
            )
        )
        return result.scalars().all()
    
    @staticmethod
    async def get_total_usage_by_model(model_id: str, days: int = 30, session: AsyncSession | Session) -> int:
        """Get total token usage for a model"""
        cutoff_date = datetime.now() - timedelta(days=days)
        result = await session.execute(
            select(TokenUsage.tokens_used).where(
                and_(
                    TokenUsage.model_id == model_id,
                    TokenUsage.created_at >= cutoff_date
                )
            )
        )
        return sum(row[0] for row in result.fetchall())


class PricingHistoryRepository:
    
    @staticmethod
    async def create(pricing: PricingHistory, session: AsyncSession | Session) -> PricingHistory:
        """Create new pricing history record"""
        session.add(pricing)
        await session.commit()
        await session.refresh(pricing)
        return pricing
    
    @staticmethod
    async def get_recent_pricing(model_id: str, days: int = 7, session: AsyncSession | Session) -> List[PricingHistory]:
        """Get recent pricing history for a model"""
        cutoff_date = datetime.now() - timedelta(days=days)
        result = await session.execute(
            select(PricingHistory).where(
                and_(
                    PricingHistory.model_id == model_id,
                    PricingHistory.created_at >= cutoff_date
                )
            ).order_by(PricingHistory.created_at.desc())
        )
        return result.scalars().all()
    
    @staticmethod
    async def get_average_price(model_id: str, days: int = 7, session: AsyncSession | Session) -> float:
        """Get average price for a model over specified days"""
        cutoff_date = datetime.now() - timedelta(days=days)
        result = await session.execute(
            select(PricingHistory.price_usd).where(
                and_(
                    PricingHistory.model_id == model_id,
                    PricingHistory.created_at >= cutoff_date
                )
            )
        )
        prices = [row[0] for row in result.fetchall()]
        return sum(prices) / len(prices) if prices else 0.0
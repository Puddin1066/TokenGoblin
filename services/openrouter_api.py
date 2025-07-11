import aiohttp
import asyncio
import secrets
import string
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

import config

logger = logging.getLogger(__name__)


class OpenRouterAPI:
    """Service for interacting with OpenRouter API"""
    
    def __init__(self):
        self.api_key = config.OPENROUTER_API_KEY
        self.base_url = config.OPENROUTER_BASE_URL
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://your-arbitrage-bot.com",  # Replace with your domain
            "X-Title": "AI Token Arbitrage Bot"
        }
    
    async def get_models(self) -> List[Dict]:
        """Get available AI models and their pricing"""
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(
                    f"{self.base_url}/models",
                    headers=self.headers
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("data", [])
                    else:
                        logger.error(f"Failed to get models: {response.status}")
                        return []
            except Exception as e:
                logger.error(f"Error getting models: {e}")
                return []
    
    async def get_account_balance(self) -> float:
        """Get current account balance"""
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(
                    f"{self.base_url}/account/balance",
                    headers=self.headers
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return float(data.get("balance", 0))
                    else:
                        logger.error(f"Failed to get balance: {response.status}")
                        return 0.0
            except Exception as e:
                logger.error(f"Error getting balance: {e}")
                return 0.0
    
    async def create_api_key(self, token_limit: int, expiry_days: int = 30) -> Optional[str]:
        """Create a new API key with token limit"""
        api_key = self._generate_api_key()
        
        # In a real implementation, you'd store this mapping in your database
        # For now, we'll generate a unique key and track it internally
        return api_key
    
    def _generate_api_key(self) -> str:
        """Generate a unique API key"""
        prefix = "sk-arb"
        random_part = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32))
        return f"{prefix}-{random_part}"
    
    async def purchase_tokens(self, model_name: str, token_count: int) -> Dict:
        """
        Purchase tokens for a specific model
        This is a simplified version - in practice you might need to prepay credits
        """
        models = await self.get_models()
        target_model = None
        
        for model in models:
            if model.get("id") == model_name:
                target_model = model
                break
        
        if not target_model:
            return {"success": False, "error": "Model not found"}
        
        # Calculate cost based on model pricing
        pricing = target_model.get("pricing", {})
        prompt_cost = float(pricing.get("prompt", "0"))
        completion_cost = float(pricing.get("completion", "0"))
        
        # Estimate cost (using average of prompt + completion for simplicity)
        avg_cost_per_token = (prompt_cost + completion_cost) / 2
        total_cost = avg_cost_per_token * token_count
        
        return {
            "success": True,
            "cost": total_cost,
            "model": model_name,
            "tokens": token_count,
            "transaction_id": f"txn_{secrets.token_hex(8)}"
        }


class TokenArbitrageEngine:
    """Engine for calculating arbitrage pricing and managing token packages"""
    
    def __init__(self):
        self.openrouter = OpenRouterAPI()
        self.markup_percentage = config.TOKEN_MARKUP_PERCENTAGE
        self.min_profit = config.MIN_PROFIT_MARGIN
        self.bulk_threshold = config.BULK_DISCOUNT_THRESHOLD
        self.bulk_discount = config.BULK_DISCOUNT_PERCENTAGE
    
    def calculate_sell_price(self, cost_price: float, token_count: int) -> float:
        """Calculate selling price with markup and bulk discounts"""
        base_price = cost_price * (1 + self.markup_percentage / 100)
        
        # Apply bulk discount if applicable
        if token_count >= self.bulk_threshold:
            base_price *= (1 - self.bulk_discount / 100)
        
        # Ensure minimum profit margin
        min_price = cost_price + self.min_profit
        return max(base_price, min_price)
    
    async def create_token_package(self, model_name: str, token_count: int, 
                                   description: str, category_id: int, 
                                   subcategory_id: int) -> Dict:
        """Create a new token package with calculated pricing"""
        
        # Get cost from OpenRouter
        purchase_result = await self.openrouter.purchase_tokens(model_name, token_count)
        
        if not purchase_result.get("success"):
            return {"success": False, "error": purchase_result.get("error")}
        
        cost_price = purchase_result["cost"]
        sell_price = self.calculate_sell_price(cost_price, token_count)
        
        package_data = {
            "token_count": token_count,
            "model_access": model_name,
            "cost_price": cost_price,
            "sell_price": sell_price,
            "description": description,
            "category_id": category_id,
            "subcategory_id": subcategory_id,
            "is_available": True,
            "profit_margin": sell_price - cost_price,
            "markup_percentage": ((sell_price - cost_price) / cost_price) * 100
        }
        
        return {"success": True, "package": package_data}
    
    async def get_popular_models(self) -> List[Dict]:
        """Get popular AI models for arbitrage"""
        models = await self.openrouter.get_models()
        
        # Filter for popular/profitable models
        popular_models = []
        for model in models:
            if any(keyword in model.get("id", "").lower() 
                   for keyword in ["gpt", "claude", "llama", "gemini"]):
                popular_models.append({
                    "id": model.get("id"),
                    "name": model.get("name"),
                    "pricing": model.get("pricing"),
                    "context_length": model.get("context_length")
                })
        
        return popular_models[:10]  # Return top 10
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
import asyncio
import json

from models.user import UserDTO
from models.item import ItemDTO
from services.notification import NotificationService
from services.user import UserService
from services.item import ItemService
from utils.localizator import Localizator
from enums.bot_entity import BotEntity


class AgenticSalesService:
    """Agentic sales service that handles intelligent lead generation, proactive outreach, and dynamic pricing"""
    
    def __init__(self):
        self.lead_scoring_weights = {
            'browse_frequency': 0.3,
            'cart_abandonment': 0.25,
            'session_duration': 0.2,
            'previous_purchases': 0.15,
            'engagement_level': 0.1
        }
    
    async def identify_sales_opportunities(self, session: AsyncSession | Session) -> List[Dict]:
        """Identify users who are likely to make purchases based on behavior patterns"""
        opportunities = []
        
        # Get users who browsed but didn't purchase in last 24 hours
        recent_browsers = await self._get_recent_browsers(session)
        
        # Get users with abandoned carts
        cart_abandoners = await self._get_cart_abandoners(session)
        
        # Get users with high engagement but no recent purchases
        engaged_users = await self._get_highly_engaged_users(session)
        
        # Score and rank opportunities
        for user in recent_browsers + cart_abandoners + engaged_users:
            score = await self._calculate_lead_score(user, session)
            if score > 0.7:  # High probability of conversion
                opportunities.append({
                    'user': user,
                    'score': score,
                    'reason': await self._get_opportunity_reason(user, session),
                    'recommended_products': await self._get_recommended_products(user, session)
                })
        
        return sorted(opportunities, key=lambda x: x['score'], reverse=True)
    
    async def execute_proactive_outreach(self, opportunities: List[Dict], session: AsyncSession | Session):
        """Execute proactive sales outreach to identified opportunities"""
        for opportunity in opportunities:
            user = opportunity['user']
            reason = opportunity['reason']
            products = opportunity['recommended_products']
            
            # Create personalized message
            message = await self._create_personalized_message(user, reason, products)
            
            # Send proactive message
            await self._send_proactive_message(user, message, session)
            
            # Schedule follow-up if no response
            await self._schedule_follow_up(user, session)
    
    async def optimize_pricing_dynamically(self, session: AsyncSession | Session):
        """Dynamically adjust pricing based on demand, competition, and inventory"""
        # Get current market conditions
        market_data = await self._get_market_conditions(session)
        
        # Get inventory levels
        inventory_data = await self._get_inventory_status(session)
        
        # Calculate optimal pricing
        pricing_adjustments = await self._calculate_pricing_adjustments(market_data, inventory_data)
        
        # Apply pricing changes
        await self._apply_pricing_changes(pricing_adjustments, session)
    
    async def predict_and_restock_inventory(self, session: AsyncSession | Session):
        """Predict demand and automatically restock inventory"""
        # Analyze historical sales data
        sales_trends = await self._analyze_sales_trends(session)
        
        # Predict future demand
        demand_predictions = await self._predict_demand(sales_trends)
        
        # Identify items needing restock
        restock_items = await self._identify_restock_needs(demand_predictions, session)
        
        # Automatically procure tokens for high-demand items
        await self._auto_procure_tokens(restock_items, session)
    
    async def execute_cross_selling_campaigns(self, session: AsyncSession | Session):
        """Execute intelligent cross-selling based on user behavior"""
        # Get users who recently made purchases
        recent_buyers = await self._get_recent_buyers(session)
        
        for buyer in recent_buyers:
            # Analyze purchase patterns
            purchase_pattern = await self._analyze_purchase_pattern(buyer, session)
            
            # Find complementary products
            complementary_products = await self._find_complementary_products(purchase_pattern, session)
            
            # Send personalized cross-sell offers
            await self._send_cross_sell_offer(buyer, complementary_products, session)
    
    async def manage_retention_campaigns(self, session: AsyncSession | Session):
        """Manage automated retention campaigns for existing customers"""
        # Identify at-risk customers (no activity in 7+ days)
        at_risk_customers = await self._identify_at_risk_customers(session)
        
        # Identify VIP customers for special treatment
        vip_customers = await self._identify_vip_customers(session)
        
        # Execute retention campaigns
        await self._execute_retention_campaigns(at_risk_customers, vip_customers, session)
    
    # Private helper methods
    async def _get_recent_browsers(self, session: AsyncSession | Session) -> List[UserDTO]:
        """Get users who browsed categories but didn't purchase in last 24 hours"""
        # Implementation would query user activity logs
        # For now, return empty list as placeholder
        return []
    
    async def _get_cart_abandoners(self, session: AsyncSession | Session) -> List[UserDTO]:
        """Get users who added items to cart but didn't complete purchase"""
        # Implementation would query cart abandonment data
        return []
    
    async def _get_highly_engaged_users(self, session: AsyncSession | Session) -> List[UserDTO]:
        """Get users with high engagement but no recent purchases"""
        # Implementation would analyze user engagement metrics
        return []
    
    async def _calculate_lead_score(self, user: UserDTO, session: AsyncSession | Session) -> float:
        """Calculate lead score based on multiple factors"""
        score = 0.0
        
        # Browse frequency score
        browse_score = await self._get_browse_frequency_score(user, session)
        score += browse_score * self.lead_scoring_weights['browse_frequency']
        
        # Cart abandonment score
        cart_score = await self._get_cart_abandonment_score(user, session)
        score += cart_score * self.lead_scoring_weights['cart_abandonment']
        
        # Session duration score
        session_score = await self._get_session_duration_score(user, session)
        score += session_score * self.lead_scoring_weights['session_duration']
        
        # Previous purchases score
        purchase_score = await self._get_previous_purchases_score(user, session)
        score += purchase_score * self.lead_scoring_weights['previous_purchases']
        
        # Engagement level score
        engagement_score = await self._get_engagement_score(user, session)
        score += engagement_score * self.lead_scoring_weights['engagement_level']
        
        return min(score, 1.0)  # Cap at 1.0
    
    async def _get_opportunity_reason(self, user: UserDTO, session: AsyncSession | Session) -> str:
        """Get the reason why this user is a sales opportunity"""
        # Implementation would analyze user behavior patterns
        return "High engagement with recent browsing activity"
    
    async def _get_recommended_products(self, user: UserDTO, session: AsyncSession | Session) -> List[ItemDTO]:
        """Get recommended products for this user based on behavior"""
        # Implementation would use collaborative filtering or ML recommendations
        return []
    
    async def _create_personalized_message(self, user: UserDTO, reason: str, products: List[ItemDTO]) -> str:
        """Create personalized sales message"""
        message = f"👋 Hi! I noticed you were interested in our Claude AI tokens.\n\n"
        message += f"🎯 {reason}\n\n"
        
        if products:
            message += "💡 Here are some recommendations for you:\n"
            for product in products[:3]:  # Limit to 3 recommendations
                message += f"• {product.description} - ${product.price}\n"
        
        message += "\n🚀 Ready to get started? Click 'Browse Tokens' to explore!"
        return message
    
    async def _send_proactive_message(self, user: UserDTO, message: str, session: AsyncSession | Session):
        """Send proactive sales message to user"""
        # Implementation would send message via Telegram API
        # For now, just log the action
        print(f"Sending proactive message to user {user.telegram_id}: {message}")
    
    async def _schedule_follow_up(self, user: UserDTO, session: AsyncSession | Session):
        """Schedule follow-up message if no response received"""
        # Implementation would schedule delayed message
        pass
    
    async def _get_market_conditions(self, session: AsyncSession | Session) -> Dict:
        """Get current market conditions for pricing optimization"""
        # Implementation would fetch market data from APIs
        return {
            'competitor_prices': {},
            'demand_trends': {},
            'supply_availability': {}
        }
    
    async def _get_inventory_status(self, session: AsyncSession | Session) -> Dict:
        """Get current inventory status"""
        # Implementation would query inventory levels
        return {}
    
    async def _calculate_pricing_adjustments(self, market_data: Dict, inventory_data: Dict) -> List[Dict]:
        """Calculate optimal pricing adjustments"""
        # Implementation would use pricing algorithms
        return []
    
    async def _apply_pricing_changes(self, adjustments: List[Dict], session: AsyncSession | Session):
        """Apply calculated pricing changes"""
        # Implementation would update item prices in database
        pass
    
    async def _analyze_sales_trends(self, session: AsyncSession | Session) -> Dict:
        """Analyze historical sales trends"""
        # Implementation would analyze sales data
        return {}
    
    async def _predict_demand(self, sales_trends: Dict) -> Dict:
        """Predict future demand based on trends"""
        # Implementation would use ML models for demand prediction
        return {}
    
    async def _identify_restock_needs(self, demand_predictions: Dict, session: AsyncSession | Session) -> List[Dict]:
        """Identify items that need restocking"""
        # Implementation would compare predicted demand with current inventory
        return []
    
    async def _auto_procure_tokens(self, restock_items: List[Dict], session: AsyncSession | Session):
        """Automatically procure tokens for high-demand items"""
        # Implementation would call OpenRouter API to purchase tokens
        pass
    
    async def _get_recent_buyers(self, session: AsyncSession | Session) -> List[UserDTO]:
        """Get users who made purchases in the last 7 days"""
        # Implementation would query recent purchase data
        return []
    
    async def _analyze_purchase_pattern(self, user: UserDTO, session: AsyncSession | Session) -> Dict:
        """Analyze user's purchase patterns"""
        # Implementation would analyze user's purchase history
        return {}
    
    async def _find_complementary_products(self, purchase_pattern: Dict, session: AsyncSession | Session) -> List[ItemDTO]:
        """Find complementary products based on purchase pattern"""
        # Implementation would use recommendation algorithms
        return []
    
    async def _send_cross_sell_offer(self, user: UserDTO, products: List[ItemDTO], session: AsyncSession | Session):
        """Send cross-sell offer to user"""
        # Implementation would send personalized cross-sell message
        pass
    
    async def _identify_at_risk_customers(self, session: AsyncSession | Session) -> List[UserDTO]:
        """Identify customers at risk of churning"""
        # Implementation would analyze user activity patterns
        return []
    
    async def _identify_vip_customers(self, session: AsyncSession | Session) -> List[UserDTO]:
        """Identify VIP customers for special treatment"""
        # Implementation would analyze customer value and loyalty
        return []
    
    async def _execute_retention_campaigns(self, at_risk: List[UserDTO], vip: List[UserDTO], session: AsyncSession | Session):
        """Execute retention campaigns for different customer segments"""
        # Implementation would send targeted retention messages
        pass
    
    # Scoring helper methods (placeholders)
    async def _get_browse_frequency_score(self, user: UserDTO, session: AsyncSession | Session) -> float:
        return 0.5
    
    async def _get_cart_abandonment_score(self, user: UserDTO, session: AsyncSession | Session) -> float:
        return 0.3
    
    async def _get_session_duration_score(self, user: UserDTO, session: AsyncSession | Session) -> float:
        return 0.4
    
    async def _get_previous_purchases_score(self, user: UserDTO, session: AsyncSession | Session) -> float:
        return 0.6
    
    async def _get_engagement_score(self, user: UserDTO, session: AsyncSession | Session) -> float:
        return 0.7
import aiohttp
import logging
from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta
from decimal import Decimal

import config
from services.openrouter_service import OpenRouterService
from services.minimal_crypto_payment import MinimalCryptoPaymentService

logger = logging.getLogger(__name__)


class AITokenService:
    """Service for handling AI token orders with USD pricing and crypto payments"""
    
    def __init__(self):
        self.openrouter_service = OpenRouterService(config.OPENROUTER_API_KEY)
        self.crypto_payment_service = MinimalCryptoPaymentService()
        
        # Configuration
        self.max_usd_order_value = 20.0  # $20 cap per order
        self.markup_percentage = 0.20  # 20% markup
        self.default_model = 'anthropic/claude-3-sonnet'  # Default AI model
        
        # Supported cryptocurrencies for payment
        self.supported_cryptos = ['USDT_TRC20', 'BTC']
        
        # Exchange rate cache
        self.rate_cache = {}
        self.rate_cache_expiry = {}
    
    async def calculate_token_order_price(self, token_count: int, crypto_type: str = 'USDT_TRC20') -> Dict:
        """
        Calculate the crypto price for a token order
        
        Args:
            token_count: Number of AI tokens requested
            crypto_type: Type of cryptocurrency for payment
            
        Returns:
            Dict with pricing details and crypto amount
        """
        try:
            # 1. Get OpenRouter pricing for the requested tokens
            pricing = await self.openrouter_service.get_model_pricing(self.default_model)
            
            # 2. Calculate USD cost for the tokens
            input_cost_per_token = pricing['input_price_per_1k_tokens'] / 1000
            output_cost_per_token = pricing['output_price_per_1k_tokens'] / 1000
            avg_cost_per_token = (input_cost_per_token + output_cost_per_token) / 2
            
            base_usd_cost = token_count * avg_cost_per_token
            
            # 3. Apply markup
            markup_amount = base_usd_cost * self.markup_percentage
            total_usd_cost = base_usd_cost + markup_amount
            
            # 4. Check $20 cap
            if total_usd_cost > self.max_usd_order_value:
                raise ValueError(f"Order value ${total_usd_cost:.2f} exceeds $20 limit")
            
            # 5. Get current crypto exchange rate
            crypto_rate = await self._get_exchange_rate(crypto_type)
            crypto_amount = total_usd_cost / crypto_rate
            
            return {
                'token_count': token_count,
                'model_id': self.default_model,
                'base_usd_cost': base_usd_cost,
                'markup_amount': markup_amount,
                'total_usd_cost': total_usd_cost,
                'crypto_type': crypto_type,
                'crypto_amount': crypto_amount,
                'exchange_rate': crypto_rate,
                'pricing_info': pricing,
                'calculated_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error calculating token order price: {e}")
            raise
    
    async def create_token_order(self, user_id: int, token_count: int, crypto_type: str = 'USDT_TRC20') -> Dict:
        """
        Create a new AI token order with payment request
        
        Args:
            user_id: Telegram user ID
            token_count: Number of AI tokens requested
            crypto_type: Type of cryptocurrency for payment
            
        Returns:
            Dict with order details and payment information
        """
        try:
            # 1. Calculate pricing
            pricing = await self.calculate_token_order_price(token_count, crypto_type)
            
            # 2. Create payment request
            payment_request = await self.crypto_payment_service.create_payment_request(
                user_id=user_id,
                amount_usd=pricing['total_usd_cost'],
                crypto=crypto_type,
                session=None  # Will be handled by the calling function
            )
            
            # 3. Create order record
            order_data = {
                'order_id': f"ai_order_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{user_id}",
                'user_id': user_id,
                'token_count': token_count,
                'model_id': pricing['model_id'],
                'base_usd_cost': pricing['base_usd_cost'],
                'markup_amount': pricing['markup_amount'],
                'total_usd_cost': pricing['total_usd_cost'],
                'crypto_type': crypto_type,
                'crypto_amount': pricing['crypto_amount'],
                'payment_id': payment_request['payment_id'],
                'status': 'pending',
                'created_at': datetime.now().isoformat()
            }
            
            return {
                'order': order_data,
                'payment': payment_request,
                'pricing': pricing
            }
            
        except Exception as e:
            logger.error(f"Error creating token order: {e}")
            raise
    
    async def process_payment_confirmation(self, payment_id: str, order_id: str) -> Dict:
        """
        Process payment confirmation and purchase tokens from OpenRouter
        
        Args:
            payment_id: Payment ID from crypto payment service
            order_id: Order ID to process
            
        Returns:
            Dict with purchase result and delivery information
        """
        try:
            # 1. Get order details (in production, this would query the database)
            # For now, we'll assume the order details are passed or stored
            order_details = await self._get_order_details(order_id)
            
            if not order_details:
                raise ValueError(f"Order {order_id} not found")
            
            # 2. Purchase tokens from OpenRouter
            purchase_result = await self.openrouter_service.purchase_tokens(
                model_id=order_details['model_id'],
                token_amount=order_details['token_count'],
                budget=order_details['total_usd_cost']
            )
            
            # 3. Update order status
            await self._update_order_status(order_id, 'completed', purchase_result)
            
            # 4. Generate delivery information
            delivery_info = await self._generate_delivery_info(purchase_result, order_details)
            
            return {
                'order_id': order_id,
                'payment_id': payment_id,
                'purchase_result': purchase_result,
                'delivery_info': delivery_info,
                'processed_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error processing payment confirmation: {e}")
            raise
    
    async def get_available_token_packages(self) -> list[Dict]:
        """
        Get available token packages for users to choose from
        
        Returns:
            List of token packages with pricing
        """
        try:
            # Get current pricing
            pricing = await self.openrouter_service.get_model_pricing(self.default_model)
            
            # Define token packages
            packages = [
                {'name': 'Starter', 'tokens': 1000, 'description': 'Perfect for small projects'},
                {'name': 'Standard', 'tokens': 5000, 'description': 'Most popular choice'},
                {'name': 'Professional', 'tokens': 10000, 'description': 'For heavy usage'},
                {'name': 'Enterprise', 'tokens': 20000, 'description': 'Maximum allowed per order'}
            ]
            
            # Calculate pricing for each package
            for package in packages:
                try:
                    pricing_info = await self.calculate_token_order_price(
                        package['tokens'], 
                        'USDT_TRC20'
                    )
                    package['usd_price'] = pricing_info['total_usd_cost']
                    package['crypto_price'] = pricing_info['crypto_amount']
                    package['crypto_type'] = 'USDT_TRC20'
                except ValueError as e:
                    # Package exceeds $20 limit
                    package['available'] = False
                    package['error'] = str(e)
                else:
                    package['available'] = True
            
            return packages
            
        except Exception as e:
            logger.error(f"Error getting token packages: {e}")
            return []
    
    async def validate_token_order(self, token_count: int) -> Tuple[bool, str]:
        """
        Validate if a token order is allowed
        
        Args:
            token_count: Number of tokens requested
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            # Check minimum tokens
            if token_count < 100:
                return False, "Minimum order is 100 tokens"
            
            # Check maximum tokens (based on $20 limit)
            max_tokens = await self._calculate_max_tokens_for_budget(self.max_usd_order_value)
            if token_count > max_tokens:
                return False, f"Maximum order is {max_tokens} tokens (due to $20 limit)"
            
            return True, ""
            
        except Exception as e:
            logger.error(f"Error validating token order: {e}")
            return False, "Error validating order"
    
    async def _get_exchange_rate(self, crypto_type: str) -> float:
        """Get current exchange rate for cryptocurrency"""
        # Check cache first
        cache_key = f"rate_{crypto_type}"
        if (cache_key in self.rate_cache and 
            cache_key in self.rate_cache_expiry and 
            datetime.now() < self.rate_cache_expiry[cache_key]):
            return self.rate_cache[cache_key]
        
        try:
            # Use CoinGecko API (free tier)
            crypto_id_map = {
                'USDT_TRC20': 'tether',
                'BTC': 'bitcoin'
            }
            
            crypto_id = crypto_id_map.get(crypto_type)
            if not crypto_id:
                raise ValueError(f"No rate mapping for {crypto_type}")
            
            url = "https://api.coingecko.com/api/v3/simple/price"
            params = {
                'ids': crypto_id,
                'vs_currencies': 'usd'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        rate = data[crypto_id]['usd']
                        
                        # Cache rate for 2 minutes
                        self.rate_cache[cache_key] = rate
                        self.rate_cache_expiry[cache_key] = datetime.now() + timedelta(minutes=2)
                        
                        logger.info(f"Updated {crypto_type} rate: ${rate:.4f}")
                        return rate
                    else:
                        logger.error(f"Failed to get exchange rate: HTTP {response.status}")
                        
        except Exception as e:
            logger.error(f"Error getting exchange rate for {crypto_type}: {e}")
        
        # Fallback rates
        fallback_rates = {
            'USDT_TRC20': 1.0,
            'BTC': 45000.0
        }
        
        return fallback_rates.get(crypto_type, 1.0)
    
    async def _calculate_max_tokens_for_budget(self, budget_usd: float) -> int:
        """Calculate maximum tokens possible within budget"""
        try:
            pricing = await self.openrouter_service.get_model_pricing(self.default_model)
            
            input_cost_per_token = pricing['input_price_per_1k_tokens'] / 1000
            output_cost_per_token = pricing['output_price_per_1k_tokens'] / 1000
            avg_cost_per_token = (input_cost_per_token + output_cost_per_token) / 2
            
            # Account for markup
            max_base_cost = budget_usd / (1 + self.markup_percentage)
            max_tokens = int(max_base_cost / avg_cost_per_token)
            
            return max_tokens
            
        except Exception as e:
            logger.error(f"Error calculating max tokens: {e}")
            return 1000  # Conservative fallback
    
    async def _get_order_details(self, order_id: str) -> Optional[Dict]:
        """Get order details from database (placeholder)"""
        # In production, this would query the database
        # For now, return None to indicate order not found
        return None
    
    async def _update_order_status(self, order_id: str, status: str, purchase_result: Dict):
        """Update order status in database (placeholder)"""
        logger.info(f"Order {order_id} status updated to {status}")
        # In production, this would update the database
    
    async def _generate_delivery_info(self, purchase_result: Dict, order_details: Dict) -> Dict:
        """Generate delivery information for the user"""
        return {
            'tokens_delivered': purchase_result['tokens_purchased'],
            'model_used': purchase_result['model_id'],
            'access_credentials': f"claude_{order_details['user_id']}_{datetime.now().strftime('%Y%m%d')}",
            'usage_instructions': "Use your access credentials to connect to Claude AI",
            'delivery_timestamp': datetime.now().isoformat()
        } 
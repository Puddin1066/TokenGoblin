import logging
from typing import Dict, Optional
from datetime import datetime

from services.ai_token_service import AITokenService
from services.notification import NotificationService

logger = logging.getLogger(__name__)


class AITokenPaymentProcessor:
    """Process payments for AI token orders and trigger OpenRouter purchases"""
    
    def __init__(self):
        self.ai_token_service = AITokenService()
    
    async def process_payment_confirmation(self, payment_data: Dict) -> Dict:
        """
        Process a confirmed payment for AI token orders
        
        Args:
            payment_data: Payment data from crypto payment service
            
        Returns:
            Dict with processing result
        """
        try:
            payment_id = payment_data.get('payment_id')
            user_id = payment_data.get('user_id')
            amount_usd = payment_data.get('amount_usd')
            crypto_type = payment_data.get('crypto_type')
            
            logger.info(f"Processing AI token payment: {payment_id} for user {user_id}")
            
            # 1. Find the corresponding order
            order_details = await self._find_order_by_payment_id(payment_id)
            
            if not order_details:
                logger.error(f"No order found for payment {payment_id}")
                return {
                    'success': False,
                    'error': 'No order found for payment',
                    'payment_id': payment_id
                }
            
            # 2. Validate payment amount matches order
            if abs(amount_usd - order_details['total_usd_cost']) > 0.01:  # Allow 1 cent tolerance
                logger.error(f"Payment amount mismatch: {amount_usd} vs {order_details['total_usd_cost']}")
                return {
                    'success': False,
                    'error': 'Payment amount does not match order',
                    'payment_id': payment_id
                }
            
            # 3. Process the token purchase from OpenRouter
            purchase_result = await self.ai_token_service.process_payment_confirmation(
                payment_id=payment_id,
                order_id=order_details['order_id']
            )
            
            if purchase_result.get('success', False):
                # 4. Send delivery notification to user
                await self._send_delivery_notification(
                    user_id=user_id,
                    order_details=order_details,
                    purchase_result=purchase_result
                )
                
                # 5. Send admin notification
                await self._send_admin_notification(
                    user_id=user_id,
                    order_details=order_details,
                    purchase_result=purchase_result
                )
                
                logger.info(f"Successfully processed AI token order: {order_details['order_id']}")
                
                return {
                    'success': True,
                    'order_id': order_details['order_id'],
                    'payment_id': payment_id,
                    'tokens_delivered': purchase_result.get('purchase_result', {}).get('tokens_purchased', 0),
                    'processed_at': datetime.now().isoformat()
                }
            else:
                logger.error(f"Failed to process token purchase: {purchase_result.get('error')}")
                return {
                    'success': False,
                    'error': purchase_result.get('error', 'Unknown error'),
                    'payment_id': payment_id
                }
                
        except Exception as e:
            logger.error(f"Error processing AI token payment: {e}")
            return {
                'success': False,
                'error': str(e),
                'payment_id': payment_data.get('payment_id')
            }
    
    async def _find_order_by_payment_id(self, payment_id: str) -> Optional[Dict]:
        """
        Find order details by payment ID
        
        Args:
            payment_id: Payment ID to search for
            
        Returns:
            Order details or None if not found
        """
        try:
            # In production, this would query the database
            # For now, we'll return a placeholder
            # This should be implemented to query the orders table
            
            # Placeholder implementation
            logger.info(f"Looking for order with payment_id: {payment_id}")
            
            # In production, this would be:
            # SELECT * FROM ai_token_orders WHERE payment_id = ? AND status = 'pending'
            
            return None  # Placeholder - implement database query
            
        except Exception as e:
            logger.error(f"Error finding order by payment ID: {e}")
            return None
    
    async def _send_delivery_notification(self, user_id: int, order_details: Dict, purchase_result: Dict):
        """Send delivery notification to user"""
        try:
            delivery_info = purchase_result.get('delivery_info', {})
            
            msg = f"🎉 **AI Tokens Delivered!**\n\n"
            msg += f"**Order ID:** `{order_details['order_id']}`\n"
            msg += f"**Tokens:** {delivery_info.get('tokens_delivered', 0):,}\n"
            msg += f"**Model:** {delivery_info.get('model_used', 'Claude 3 Sonnet')}\n"
            msg += f"**Access Credentials:** `{delivery_info.get('access_credentials', 'N/A')}`\n\n"
            msg += f"**Usage Instructions:**\n{delivery_info.get('usage_instructions', 'Use your credentials to access Claude AI')}\n\n"
            msg += f"✅ Your tokens are ready to use!"
            
            await NotificationService.send_to_user(msg, user_id)
            
        except Exception as e:
            logger.error(f"Error sending delivery notification: {e}")
    
    async def _send_admin_notification(self, user_id: int, order_details: Dict, purchase_result: Dict):
        """Send admin notification about completed order"""
        try:
            delivery_info = purchase_result.get('delivery_info', {})
            
            msg = f"💰 **AI Token Order Completed**\n\n"
            msg += f"**User ID:** {user_id}\n"
            msg += f"**Order ID:** `{order_details['order_id']}`\n"
            msg += f"**Tokens:** {delivery_info.get('tokens_delivered', 0):,}\n"
            msg += f"**Amount:** ${order_details['total_usd_cost']:.2f}\n"
            msg += f"**Crypto:** {order_details['crypto_amount']:.4f} {order_details['crypto_type']}\n"
            msg += f"**Model:** {delivery_info.get('model_used', 'Claude 3 Sonnet')}\n\n"
            msg += f"✅ Order successfully processed and delivered"
            
            await NotificationService.send_to_admins(msg, None)
            
        except Exception as e:
            logger.error(f"Error sending admin notification: {e}")
    
    async def handle_payment_expired(self, payment_id: str):
        """Handle expired payment for AI token orders"""
        try:
            logger.info(f"Payment expired: {payment_id}")
            
            # Find and update order status
            order_details = await self._find_order_by_payment_id(payment_id)
            
            if order_details:
                await self._update_order_status(order_details['order_id'], 'expired')
                
                # Send notification to user
                msg = f"⏰ **Payment Expired**\n\n"
                msg += f"Your payment for order `{order_details['order_id']}` has expired.\n\n"
                msg += f"Please place a new order if you still need AI tokens."
                
                await NotificationService.send_to_user(msg, order_details['user_id'])
            
        except Exception as e:
            logger.error(f"Error handling expired payment: {e}")
    
    async def _update_order_status(self, order_id: str, status: str):
        """Update order status in database"""
        try:
            logger.info(f"Updating order {order_id} status to {status}")
            # In production, this would update the database
            # UPDATE ai_token_orders SET status = ? WHERE order_id = ?
            
        except Exception as e:
            logger.error(f"Error updating order status: {e}")
    
    async def validate_payment_for_order(self, payment_id: str, amount_usd: float, crypto_type: str) -> bool:
        """
        Validate that a payment matches an existing order
        
        Args:
            payment_id: Payment ID
            amount_usd: Payment amount in USD
            crypto_type: Type of cryptocurrency
            
        Returns:
            True if payment is valid for an order
        """
        try:
            order_details = await self._find_order_by_payment_id(payment_id)
            
            if not order_details:
                return False
            
            # Check amount matches
            if abs(amount_usd - order_details['total_usd_cost']) > 0.01:
                return False
            
            # Check crypto type matches
            if crypto_type != order_details['crypto_type']:
                return False
            
            # Check order is still pending
            if order_details['status'] != 'pending':
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating payment for order: {e}")
            return False 
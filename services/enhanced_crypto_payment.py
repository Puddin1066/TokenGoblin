import asyncio
import aiohttp
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from decimal import Decimal
import json

import config


class EnhancedCryptoPaymentService:
    """Enhanced crypto payment service with multi-chain support and automated settlement"""
    
    def __init__(self):
        self.payment_processors = {
            'web3': Web3PaymentProcessor(),
            'krypto_express': KryptoExpressProcessor(),
            'coinbase_commerce': CoinbaseCommerceProcessor(),
            'stripe_crypto': StripeCryptoProcessor()
        }
        self.supported_chains = ['BTC', 'ETH', 'SOL', 'LTC', 'USDT_TRC20', 'USDT_ERC20', 'USDC_ERC20']
    
    async def create_payment_request(self, amount: float, currency: str, user_id: int) -> Dict:
        """Create a new payment request with multiple payment options"""
        payment_request = {
            'id': f"pay_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{user_id}",
            'amount': amount,
            'currency': currency,
            'user_id': user_id,
            'created_at': datetime.now().isoformat(),
            'status': 'pending',
            'payment_options': []
        }
        
        # Generate payment options for each supported chain
        for chain in self.supported_chains:
            try:
                payment_option = await self._create_payment_option(chain, amount, payment_request['id'])
                payment_request['payment_options'].append(payment_option)
            except Exception as e:
                print(f"Failed to create payment option for {chain}: {e}")
        
        return payment_request
    
    async def _create_payment_option(self, chain: str, amount: float, request_id: str) -> Dict:
        """Create payment option for a specific blockchain"""
        # Get current exchange rate
        exchange_rate = await self._get_exchange_rate(chain, 'USD')
        
        # Calculate crypto amount
        crypto_amount = amount / exchange_rate
        
        # Generate payment address
        payment_address = await self._generate_payment_address(chain)
        
        return {
            'chain': chain,
            'crypto_amount': crypto_amount,
            'usd_amount': amount,
            'payment_address': payment_address,
            'exchange_rate': exchange_rate,
            'expires_at': (datetime.now() + timedelta(hours=1)).isoformat()
        }
    
    async def monitor_payment_status(self, payment_request_id: str) -> Dict:
        """Monitor payment status across all payment options"""
        payment_status = {
            'request_id': payment_request_id,
            'status': 'pending',
            'confirmed_payments': [],
            'pending_payments': [],
            'failed_payments': []
        }
        
        # Check each payment option
        for processor_name, processor in self.payment_processors.items():
            try:
                status = await processor.check_payment_status(payment_request_id)
                if status['status'] == 'confirmed':
                    payment_status['confirmed_payments'].append(status)
                elif status['status'] == 'pending':
                    payment_status['pending_payments'].append(status)
                else:
                    payment_status['failed_payments'].append(status)
            except Exception as e:
                print(f"Error checking payment status with {processor_name}: {e}")
        
        # Update overall status
        if payment_status['confirmed_payments']:
            payment_status['status'] = 'confirmed'
        elif payment_status['failed_payments'] and not payment_status['pending_payments']:
            payment_status['status'] = 'failed'
        
        return payment_status
    
    async def process_automatic_settlement(self, payment_request_id: str) -> Dict:
        """Automatically process settlement when payment is confirmed"""
        payment_status = await self.monitor_payment_status(payment_request_id)
        
        if payment_status['status'] == 'confirmed':
            # Process settlement
            settlement_result = await self._process_settlement(payment_status)
            
            # Update user balance
            await self._update_user_balance(payment_status)
            
            # Send confirmation notifications
            await self._send_payment_confirmation(payment_status)
            
            return {
                'status': 'settled',
                'settlement_timestamp': datetime.now().isoformat(),
                'amount': settlement_result['amount'],
                'currency': settlement_result['currency']
            }
        
        return {'status': 'pending'}
    
    async def get_payment_analytics(self, days: int = 30) -> Dict:
        """Get payment analytics and insights"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        analytics = {
            'total_payments': 0,
            'total_volume_usd': 0,
            'success_rate': 0,
            'average_payment_amount': 0,
            'payment_methods_distribution': {},
            'daily_volume': [],
            'failed_payments': 0
        }
        
        # Aggregate data from all processors
        for processor_name, processor in self.payment_processors.items():
            try:
                processor_analytics = await processor.get_analytics(start_date, end_date)
                analytics['total_payments'] += processor_analytics.get('total_payments', 0)
                analytics['total_volume_usd'] += processor_analytics.get('total_volume_usd', 0)
                analytics['failed_payments'] += processor_analytics.get('failed_payments', 0)
                
                # Merge payment methods distribution
                for method, count in processor_analytics.get('payment_methods', {}).items():
                    analytics['payment_methods_distribution'][method] = \
                        analytics['payment_methods_distribution'].get(method, 0) + count
            except Exception as e:
                print(f"Error getting analytics from {processor_name}: {e}")
        
        # Calculate success rate
        if analytics['total_payments'] > 0:
            analytics['success_rate'] = (analytics['total_payments'] - analytics['failed_payments']) / analytics['total_payments']
        
        # Calculate average payment amount
        if analytics['total_payments'] > 0:
            analytics['average_payment_amount'] = analytics['total_volume_usd'] / analytics['total_payments']
        
        return analytics
    
    async def optimize_payment_routing(self, amount: float, user_location: str = None) -> Dict:
        """Optimize payment routing based on cost, speed, and user preferences"""
        routing_options = []
        
        for chain in self.supported_chains:
            try:
                # Get routing metrics
                cost = await self._get_payment_cost(chain, amount)
                speed = await self._get_payment_speed(chain)
                reliability = await self._get_payment_reliability(chain)
                
                # Calculate routing score
                score = self._calculate_routing_score(cost, speed, reliability, user_location)
                
                routing_options.append({
                    'chain': chain,
                    'cost': cost,
                    'speed': speed,
                    'reliability': reliability,
                    'score': score
                })
            except Exception as e:
                print(f"Error calculating routing for {chain}: {e}")
        
        # Sort by score and return top options
        routing_options.sort(key=lambda x: x['score'], reverse=True)
        
        return {
            'recommended_options': routing_options[:3],
            'all_options': routing_options
        }
    
    async def handle_payment_webhook(self, webhook_data: Dict) -> Dict:
        """Handle incoming payment webhooks from various processors"""
        webhook_result = {
            'processed': False,
            'payment_request_id': None,
            'status': 'unknown',
            'amount': 0,
            'currency': 'USD'
        }
        
        # Route webhook to appropriate processor
        for processor_name, processor in self.payment_processors.items():
            try:
                if processor.can_handle_webhook(webhook_data):
                    result = await processor.process_webhook(webhook_data)
                    webhook_result.update(result)
                    webhook_result['processed'] = True
                    break
            except Exception as e:
                print(f"Error processing webhook with {processor_name}: {e}")
        
        return webhook_result
    
    # Private helper methods
    async def _get_exchange_rate(self, from_currency: str, to_currency: str) -> float:
        """Get current exchange rate"""
        # Implementation would fetch from exchange APIs
        rates = {
            'BTC': 45000,
            'ETH': 3000,
            'SOL': 100,
            'LTC': 150,
            'USDT_TRC20': 1,
            'USDT_ERC20': 1,
            'USDC_ERC20': 1
        }
        return rates.get(from_currency, 1)
    
    async def _generate_payment_address(self, chain: str) -> str:
        """Generate payment address for specific chain"""
        # Implementation would generate addresses for each chain
        addresses = {
            'BTC': 'bc1q2kv89q8yvf068xxw3x65gzfag98l9wnrda3x56',
            'ETH': '0xB49D720DE2630fA4C813d5B4c025706E25cF74fe',
            'SOL': 'Avm7VAqPrwpHteXKfDTRFjpj6swEzjmj3a2KQvVDvugK',
            'LTC': 'ltc1q0tuvm5vqn9le5zmhvhtp7z9p2eu6yvv24ey686',
            'USDT_TRC20': 'THzRw8UpTsEYBEG5CCbsCVnJzopSHFHJm6',
            'USDT_ERC20': '0xB49D720DE2630fA4C813d5B4c025706E25cF74fe',
            'USDC_ERC20': '0xB49D720DE2630fA4C813d5B4c025706E25cF74fe'
        }
        return addresses.get(chain, '')
    
    async def _process_settlement(self, payment_status: Dict) -> Dict:
        """Process settlement for confirmed payments"""
        # Implementation would handle settlement logic
        return {
            'amount': sum(payment['amount'] for payment in payment_status['confirmed_payments']),
            'currency': 'USD'
        }
    
    async def _update_user_balance(self, payment_status: Dict):
        """Update user balance after payment confirmation"""
        # Implementation would update user balance in database
        pass
    
    async def _send_payment_confirmation(self, payment_status: Dict):
        """Send payment confirmation notifications"""
        # Implementation would send notifications
        pass
    
    async def _get_payment_cost(self, chain: str, amount: float) -> float:
        """Get payment cost for specific chain and amount"""
        # Implementation would calculate fees for each chain
        fee_rates = {
            'BTC': 0.0001,
            'ETH': 0.005,
            'SOL': 0.00025,
            'LTC': 0.0001,
            'USDT_TRC20': 0.001,
            'USDT_ERC20': 0.01,
            'USDC_ERC20': 0.01
        }
        return fee_rates.get(chain, 0) * amount
    
    async def _get_payment_speed(self, chain: str) -> float:
        """Get payment speed for specific chain (in minutes)"""
        # Implementation would return average confirmation times
        speeds = {
            'BTC': 10,
            'ETH': 2,
            'SOL': 1,
            'LTC': 5,
            'USDT_TRC20': 1,
            'USDT_ERC20': 2,
            'USDC_ERC20': 2
        }
        return speeds.get(chain, 5)
    
    async def _get_payment_reliability(self, chain: str) -> float:
        """Get payment reliability score for specific chain (0-1)"""
        # Implementation would return reliability scores
        reliability = {
            'BTC': 0.99,
            'ETH': 0.98,
            'SOL': 0.95,
            'LTC': 0.97,
            'USDT_TRC20': 0.96,
            'USDT_ERC20': 0.97,
            'USDC_ERC20': 0.98
        }
        return reliability.get(chain, 0.9)
    
    def _calculate_routing_score(self, cost: float, speed: float, reliability: float, user_location: str = None) -> float:
        """Calculate routing score based on multiple factors"""
        # Normalize factors (lower cost and speed are better)
        normalized_cost = 1 / (1 + cost)
        normalized_speed = 1 / (1 + speed)
        
        # Weighted score
        score = (normalized_cost * 0.4 + normalized_speed * 0.3 + reliability * 0.3)
        
        return score


class Web3PaymentProcessor:
    """Web3.py based payment processor for direct blockchain interactions"""
    
    def __init__(self):
        self.web3_connections = {}
    
    async def check_payment_status(self, payment_request_id: str) -> Dict:
        # Implementation would check blockchain for payment confirmation
        return {'status': 'pending', 'amount': 0}
    
    async def get_analytics(self, start_date: datetime, end_date: datetime) -> Dict:
        # Implementation would analyze blockchain transactions
        return {'total_payments': 0, 'total_volume_usd': 0, 'payment_methods': {}}
    
    def can_handle_webhook(self, webhook_data: Dict) -> bool:
        return 'web3' in webhook_data.get('source', '')
    
    async def process_webhook(self, webhook_data: Dict) -> Dict:
        # Implementation would process web3 webhooks
        return {'status': 'processed'}


class KryptoExpressProcessor:
    """KryptoExpress payment processor"""
    
    async def check_payment_status(self, payment_request_id: str) -> Dict:
        # Implementation would check KryptoExpress API
        return {'status': 'pending', 'amount': 0}
    
    async def get_analytics(self, start_date: datetime, end_date: datetime) -> Dict:
        # Implementation would analyze KryptoExpress data
        return {'total_payments': 0, 'total_volume_usd': 0, 'payment_methods': {}}
    
    def can_handle_webhook(self, webhook_data: Dict) -> bool:
        return 'krypto_express' in webhook_data.get('source', '')
    
    async def process_webhook(self, webhook_data: Dict) -> Dict:
        # Implementation would process KryptoExpress webhooks
        return {'status': 'processed'}


class CoinbaseCommerceProcessor:
    """Coinbase Commerce payment processor"""
    
    async def check_payment_status(self, payment_request_id: str) -> Dict:
        # Implementation would check Coinbase Commerce API
        return {'status': 'pending', 'amount': 0}
    
    async def get_analytics(self, start_date: datetime, end_date: datetime) -> Dict:
        # Implementation would analyze Coinbase Commerce data
        return {'total_payments': 0, 'total_volume_usd': 0, 'payment_methods': {}}
    
    def can_handle_webhook(self, webhook_data: Dict) -> bool:
        return 'coinbase_commerce' in webhook_data.get('source', '')
    
    async def process_webhook(self, webhook_data: Dict) -> Dict:
        # Implementation would process Coinbase Commerce webhooks
        return {'status': 'processed'}


class StripeCryptoProcessor:
    """Stripe Crypto payment processor"""
    
    async def check_payment_status(self, payment_request_id: str) -> Dict:
        # Implementation would check Stripe Crypto API
        return {'status': 'pending', 'amount': 0}
    
    async def get_analytics(self, start_date: datetime, end_date: datetime) -> Dict:
        # Implementation would analyze Stripe Crypto data
        return {'total_payments': 0, 'total_volume_usd': 0, 'payment_methods': {}}
    
    def can_handle_webhook(self, webhook_data: Dict) -> bool:
        return 'stripe_crypto' in webhook_data.get('source', '')
    
    async def process_webhook(self, webhook_data: Dict) -> Dict:
        # Implementation would process Stripe Crypto webhooks
        return {'status': 'processed'}
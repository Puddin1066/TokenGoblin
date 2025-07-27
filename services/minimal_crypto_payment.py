import asyncio
import aiohttp
import hashlib
import hmac
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from sqlalchemy import select, update, insert

import config
from models.payment import Payment, ProcessingPaymentDTO, TablePaymentDTO
from models.user import User
from services.notification import NotificationService

logger = logging.getLogger(__name__)


class MinimalCryptoPaymentService:
    """Minimal crypto payment processing for restricted countries"""
    
    def __init__(self):
        # Focus on two main cryptocurrencies for restricted regions
        self.supported_cryptos = {
            'USDT_TRC20': {
                'name': 'USDT (TRC20)',
                'symbol': 'USDT',
                'decimals': 6,
                'contract_address': 'TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t',
                'api_url': 'https://api.trongrid.io',
                'explorer': 'https://tronscan.org/#/transaction/',
                'min_amount': 1.0,
                'preferred_regions': ['zh-hans', 'ru']
            },
            'BTC': {
                'name': 'Bitcoin',
                'symbol': 'BTC',
                'decimals': 8,
                'api_url': 'https://api.blockcypher.com/v1/btc/main',
                'explorer': 'https://blockstream.info/tx/',
                'min_amount': 0.0001,
                'preferred_regions': ['fa', 'ar']
            }
        }
        
        # Exchange rate cache
        self.rate_cache = {}
        self.rate_cache_expiry = {}
        
        # Payment monitoring
        self.monitoring_active = False
    
    async def start_payment_monitoring(self):
        """Start background payment monitoring"""
        if self.monitoring_active:
            return
        
        self.monitoring_active = True
        logger.info("🔍 Starting minimal crypto payment monitoring...")
        
        # Start monitoring tasks for supported cryptocurrencies
        monitoring_tasks = [
            asyncio.create_task(self._monitor_usdt_payments()),
            asyncio.create_task(self._monitor_btc_payments()),
            asyncio.create_task(self._update_exchange_rates())
        ]
        
        await asyncio.gather(*monitoring_tasks)
    
    async def generate_payment_address(self, user_id: int, crypto: str, session: AsyncSession | Session) -> Dict:
        """Generate payment address for user"""
        if crypto not in self.supported_cryptos:
            raise ValueError(f"Unsupported cryptocurrency: {crypto}")
        
        crypto_info = self.supported_cryptos[crypto]
        
        if crypto == 'USDT_TRC20':
            address = await self._generate_tron_address(user_id)
        elif crypto == 'BTC':
            address = await self._generate_btc_address(user_id)
        else:
            raise ValueError(f"Address generation not implemented for {crypto}")
        
        # Store address mapping in database
        await self._store_user_address(user_id, address, crypto, session)
        
        return {
            'address': address,
            'crypto': crypto,
            'crypto_info': crypto_info,
            'user_id': user_id,
            'generated_at': datetime.now().isoformat()
        }
    
    async def _generate_tron_address(self, user_id: int) -> str:
        """Generate deterministic TRON address for user"""
        # Use deterministic generation based on master seed + user_id
        master_seed = config.MASTER_WALLET_SEED if hasattr(config, 'MASTER_WALLET_SEED') else 'default_seed_change_me'
        
        # Create deterministic seed for this user
        user_seed = hashlib.sha256(f"{master_seed}:tron:{user_id}".encode()).digest()
        
        # For MVP, we'll use a simpler approach
        # In production, this would use proper TRON cryptography libraries
        
        # Generate deterministic address based on user_id
        address_hash = hashlib.sha256(f"tron_address_{user_id}_{master_seed}".encode()).hexdigest()
        
        # Create valid TRON address format (starts with T, 34 characters)
        # This is a mock address for development - replace with real generation
        tron_address = f"T{address_hash[:33]}"
        
        logger.info(f"Generated TRON address for user {user_id}: {tron_address}")
        return tron_address
    
    async def _generate_btc_address(self, user_id: int) -> str:
        """Generate deterministic Bitcoin address for user"""
        master_seed = config.MASTER_WALLET_SEED if hasattr(config, 'MASTER_WALLET_SEED') else 'default_seed_change_me'
        
        # Create deterministic seed for this user
        user_seed = hashlib.sha256(f"{master_seed}:btc:{user_id}".encode()).digest()
        
        # Generate deterministic address based on user_id
        address_hash = hashlib.sha256(f"btc_address_{user_id}_{master_seed}".encode()).hexdigest()
        
        # Create valid Bitcoin address format (starts with bc1, bech32)
        # This is a mock address for development - replace with real generation
        btc_address = f"bc1q{address_hash[:32]}"
        
        logger.info(f"Generated BTC address for user {user_id}: {btc_address}")
        return btc_address
    
    async def _store_user_address(self, user_id: int, address: str, crypto: str, session: AsyncSession | Session):
        """Store user's payment address in database"""
        try:
            # This would store in a user_addresses table
            # For now, we'll log it
            logger.info(f"Storing address for user {user_id}: {crypto} -> {address}")
            
            # In production, create a user_addresses table and store:
            # INSERT INTO user_addresses (user_id, crypto, address, created_at)
            # VALUES (user_id, crypto, address, datetime.now())
            
        except Exception as e:
            logger.error(f"Error storing user address: {e}")
    
    async def create_payment_request(self, user_id: int, amount_usd: float, crypto: str, session: AsyncSession | Session) -> Dict:
        """Create a new payment request"""
        if crypto not in self.supported_cryptos:
            raise ValueError(f"Unsupported cryptocurrency: {crypto}")
        
        crypto_info = self.supported_cryptos[crypto]
        
        # Get current exchange rate
        crypto_rate = await self.get_exchange_rate(crypto)
        crypto_amount = amount_usd / crypto_rate
        
        # Check minimum amount
        if crypto_amount < crypto_info['min_amount']:
            raise ValueError(f"Amount too small. Minimum: {crypto_info['min_amount']} {crypto}")
        
        # Generate payment address
        address_info = await self.generate_payment_address(user_id, crypto, session)
        
        # Create payment record
        payment_data = {
            'user_id': user_id,
            'amount_usd': amount_usd,
            'amount_crypto': crypto_amount,
            'crypto': crypto,
            'address': address_info['address'],
            'status': 'pending',
            'expires_at': datetime.now() + timedelta(hours=24),
            'created_at': datetime.now()
        }
        
        # Store payment request
        payment_id = await self._store_payment_request(payment_data, session)
        
        return {
            'payment_id': payment_id,
            'address': address_info['address'],
            'amount_crypto': crypto_amount,
            'amount_usd': amount_usd,
            'crypto': crypto,
            'crypto_info': crypto_info,
            'expires_at': payment_data['expires_at'].isoformat(),
            'qr_data': f"{crypto.lower()}:{address_info['address']}?amount={crypto_amount}",
            'explorer_url': crypto_info['explorer'],
            'instructions': await self._get_payment_instructions(crypto, address_info['address'], crypto_amount)
        }
    
    async def _store_payment_request(self, payment_data: Dict, session: AsyncSession | Session) -> str:
        """Store payment request in database"""
        try:
            # Generate unique payment ID
            payment_id = hashlib.md5(f"{payment_data['user_id']}_{payment_data['created_at']}".encode()).hexdigest()[:16]
            
            # In production, store in payments table
            logger.info(f"Storing payment request {payment_id}: {payment_data}")
            
            return payment_id
            
        except Exception as e:
            logger.error(f"Error storing payment request: {e}")
            raise
    
    async def get_exchange_rate(self, crypto: str) -> float:
        """Get current exchange rate for cryptocurrency"""
        # Check cache first
        cache_key = f"rate_{crypto}"
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
            
            crypto_id = crypto_id_map.get(crypto)
            if not crypto_id:
                raise ValueError(f"No rate mapping for {crypto}")
            
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
                        
                        logger.info(f"Updated {crypto} rate: ${rate:.4f}")
                        return rate
                    else:
                        logger.error(f"Failed to get exchange rate: HTTP {response.status}")
                        
        except Exception as e:
            logger.error(f"Error getting exchange rate for {crypto}: {e}")
        
        # Fallback rates
        fallback_rates = {
            'USDT_TRC20': 1.0,
            'BTC': 45000.0
        }
        
        return fallback_rates.get(crypto, 1.0)
    
    async def _monitor_usdt_payments(self):
        """Monitor USDT TRC20 payments"""
        while self.monitoring_active:
            try:
                logger.info("🔍 Monitoring USDT TRC20 payments...")
                
                # Get pending USDT payments
                pending_payments = await self._get_pending_payments('USDT_TRC20')
                
                for payment in pending_payments:
                    await self._check_tron_payment(payment)
                
                # Check every 60 seconds
                await asyncio.sleep(60)
                
            except Exception as e:
                logger.error(f"Error monitoring USDT payments: {e}")
                await asyncio.sleep(120)  # Wait 2 minutes before retry
    
    async def _monitor_btc_payments(self):
        """Monitor Bitcoin payments"""
        while self.monitoring_active:
            try:
                logger.info("🔍 Monitoring Bitcoin payments...")
                
                # Get pending BTC payments
                pending_payments = await self._get_pending_payments('BTC')
                
                for payment in pending_payments:
                    await self._check_btc_payment(payment)
                
                # Check every 90 seconds (Bitcoin is slower)
                await asyncio.sleep(90)
                
            except Exception as e:
                logger.error(f"Error monitoring BTC payments: {e}")
                await asyncio.sleep(180)  # Wait 3 minutes before retry
    
    async def _update_exchange_rates(self):
        """Periodically update exchange rates"""
        while self.monitoring_active:
            try:
                logger.info("💱 Updating exchange rates...")
                
                for crypto in self.supported_cryptos.keys():
                    await self.get_exchange_rate(crypto)
                
                # Update every 5 minutes
                await asyncio.sleep(300)
                
            except Exception as e:
                logger.error(f"Error updating exchange rates: {e}")
                await asyncio.sleep(600)  # Wait 10 minutes before retry
    
    async def _get_pending_payments(self, crypto: str) -> List[Dict]:
        """Get pending payments for a cryptocurrency"""
        # This would query the payments table
        # For now, return empty list
        return []
    
    async def _check_tron_payment(self, payment: Dict):
        """Check TRON payment status"""
        try:
            address = payment['address']
            expected_amount = payment['amount_crypto']
            
            # Query TronGrid API for transactions
            url = f"https://api.trongrid.io/v1/accounts/{address}/transactions/trc20"
            params = {
                'contract_address': 'TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t',  # USDT TRC20
                'limit': 20
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        transactions = data.get('data', [])
                        
                        for tx in transactions:
                            # Check if transaction matches our payment
                            if await self._validate_tron_transaction(tx, payment):
                                await self._confirm_payment(payment, tx)
                                break
                    else:
                        logger.warning(f"TronGrid API error: {response.status}")
                        
        except Exception as e:
            logger.error(f"Error checking TRON payment: {e}")
    
    async def _check_btc_payment(self, payment: Dict):
        """Check Bitcoin payment status"""
        try:
            address = payment['address']
            
            # Query BlockCypher API for address transactions
            url = f"https://api.blockcypher.com/v1/btc/main/addrs/{address}/full"
            params = {'limit': 10}
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        transactions = data.get('txs', [])
                        
                        for tx in transactions:
                            # Check if transaction matches our payment
                            if await self._validate_btc_transaction(tx, payment):
                                await self._confirm_payment(payment, tx)
                                break
                    else:
                        logger.warning(f"BlockCypher API error: {response.status}")
                        
        except Exception as e:
            logger.error(f"Error checking BTC payment: {e}")
    
    async def _validate_tron_transaction(self, transaction: Dict, payment: Dict) -> bool:
        """Validate TRON transaction matches payment"""
        try:
            # Check transaction details
            tx_value = int(transaction.get('value', 0)) / 1_000_000  # USDT has 6 decimals
            tx_to = transaction.get('to', '')
            tx_confirmed = transaction.get('confirmed', False)
            
            # Validate amount (allow 1% tolerance)
            expected_amount = payment['amount_crypto']
            amount_tolerance = expected_amount * 0.01
            amount_valid = abs(tx_value - expected_amount) <= amount_tolerance
            
            # Validate recipient address
            address_valid = tx_to.lower() == payment['address'].lower()
            
            # Check if transaction is confirmed
            confirmed_valid = tx_confirmed
            
            return amount_valid and address_valid and confirmed_valid
            
        except Exception as e:
            logger.error(f"Error validating TRON transaction: {e}")
            return False
    
    async def _validate_btc_transaction(self, transaction: Dict, payment: Dict) -> bool:
        """Validate Bitcoin transaction matches payment"""
        try:
            # Check transaction outputs
            outputs = transaction.get('outputs', [])
            confirmations = transaction.get('confirmations', 0)
            
            for output in outputs:
                output_value = output.get('value', 0) / 100_000_000  # Satoshis to BTC
                output_addresses = output.get('addresses', [])
                
                # Check if this output is for our address
                if payment['address'] in output_addresses:
                    # Validate amount (allow 1% tolerance)
                    expected_amount = payment['amount_crypto']
                    amount_tolerance = expected_amount * 0.01
                    amount_valid = abs(output_value - expected_amount) <= amount_tolerance
                    
                    # Check confirmations (require at least 1)
                    confirmed_valid = confirmations >= 1
                    
                    return amount_valid and confirmed_valid
            
            return False
            
        except Exception as e:
            logger.error(f"Error validating BTC transaction: {e}")
            return False
    
    async def _confirm_payment(self, payment: Dict, transaction: Dict):
        """Confirm payment and update user balance"""
        try:
            payment_id = payment['payment_id']
            user_id = payment['user_id']
            amount_usd = payment['amount_usd']
            tx_hash = transaction.get('txid') or transaction.get('hash')
            
            logger.info(f"💰 Confirming payment {payment_id} for user {user_id}: ${amount_usd}")
            
            # Update payment status
            await self._update_payment_status(payment_id, 'confirmed', tx_hash)
            
            # Update user balance
            await self._credit_user_balance(user_id, amount_usd)
            
            # Send confirmation notification
            await self._send_payment_confirmation(user_id, amount_usd, payment['crypto'], tx_hash)
            
            # Notify admins
            await self._notify_admins_payment_received(user_id, amount_usd, payment['crypto'])
            
        except Exception as e:
            logger.error(f"Error confirming payment: {e}")
    
    async def _update_payment_status(self, payment_id: str, status: str, tx_hash: str):
        """Update payment status in database"""
        logger.info(f"Payment {payment_id} status updated to {status}, tx: {tx_hash}")
        # In production: UPDATE payments SET status = ?, tx_hash = ? WHERE id = ?
    
    async def _credit_user_balance(self, user_id: int, amount_usd: float):
        """Credit user's balance"""
        logger.info(f"Crediting user {user_id} balance: ${amount_usd}")
        # In production: UPDATE users SET balance = balance + ? WHERE telegram_id = ?
    
    async def _send_payment_confirmation(self, user_id: int, amount: float, crypto: str, tx_hash: str):
        """Send payment confirmation to user"""
        message = f"✅ Payment confirmed!\n\n"
        message += f"💰 Amount: ${amount:.2f}\n"
        message += f"🪙 Cryptocurrency: {crypto}\n"
        message += f"🔗 Transaction: {tx_hash[:16]}...\n\n"
        message += f"💎 Your balance has been updated!"
        
        await NotificationService.send_to_user(message, user_id)
    
    async def _notify_admins_payment_received(self, user_id: int, amount: float, crypto: str):
        """Notify admins of payment received"""
        message = f"💰 New payment received!\n\n"
        message += f"👤 User: {user_id}\n"
        message += f"💵 Amount: ${amount:.2f}\n"
        message += f"🪙 Crypto: {crypto}"
        
        await NotificationService.send_to_admins(message, None)
    
    async def _get_payment_instructions(self, crypto: str, address: str, amount: float) -> Dict:
        """Get payment instructions for cryptocurrency"""
        crypto_info = self.supported_cryptos[crypto]
        
        instructions = {
            'USDT_TRC20': {
                'title': 'USDT (TRC20) Payment Instructions',
                'steps': [
                    '1. Open your TRON wallet (TronLink, etc.)',
                    '2. Select USDT (TRC20) for transfer',
                    f'3. Send exactly {amount:.6f} USDT',
                    f'4. To address: {address}',
                    '5. Confirm transaction',
                    '6. Your balance will update in 1-5 minutes'
                ],
                'warnings': [
                    '⚠️ Only send USDT TRC20 (not ERC20!)',
                    '⚠️ Send exact amount or payment may fail',
                    '⚠️ Double-check the address'
                ]
            },
            'BTC': {
                'title': 'Bitcoin Payment Instructions', 
                'steps': [
                    '1. Open your Bitcoin wallet',
                    f'2. Send exactly {amount:.8f} BTC',
                    f'3. To address: {address}',
                    '4. Set appropriate fee for faster confirmation',
                    '5. Confirm transaction',
                    '6. Your balance will update after 1 confirmation'
                ],
                'warnings': [
                    '⚠️ Only send Bitcoin (BTC)',
                    '⚠️ Send exact amount or payment may fail',
                    '⚠️ Higher fees = faster confirmation'
                ]
            }
        }
        
        return instructions.get(crypto, {})
    
    async def get_supported_cryptos_for_region(self, region: str) -> List[Dict]:
        """Get recommended cryptocurrencies for region"""
        region_preferences = {
            'zh-hans': ['USDT_TRC20', 'BTC'],  # China prefers USDT TRC20
            'ru': ['USDT_TRC20', 'BTC'],       # Russia prefers USDT TRC20
            'fa': ['BTC', 'USDT_TRC20'],       # Iran prefers Bitcoin
            'ar': ['BTC', 'USDT_TRC20'],       # Middle East prefers Bitcoin
            'default': ['USDT_TRC20', 'BTC']
        }
        
        preferred_order = region_preferences.get(region, region_preferences['default'])
        
        result = []
        for crypto in preferred_order:
            if crypto in self.supported_cryptos:
                crypto_info = self.supported_cryptos[crypto].copy()
                crypto_info['current_rate'] = await self.get_exchange_rate(crypto)
                result.append({
                    'crypto': crypto,
                    'info': crypto_info
                })
        
        return result
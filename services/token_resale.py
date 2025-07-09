import asyncio
from enum import Enum
from typing import Optional
import aiohttp
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

import config
from enums.cryptocurrency import Cryptocurrency
from models.transaction import TransactionDTO, TransactionStatus
from repositories.transaction import TransactionRepository
from utils.localizator import Localizator


class PaymentMethod(Enum):
    CRYPTO = "crypto"
    FIAT = "fiat"


class TokenResaleService:
    """Simplified token resale service - payment in, tokens out directly to client wallet"""
    
    @staticmethod
    async def create_token_order(
        user_telegram_id: int,
        payment_method: PaymentMethod,
        payment_amount: float,
        payment_currency: str,
        token_symbol: str,
        recipient_address: str,
        session: AsyncSession | Session
    ) -> TransactionDTO:
        """Create a new token purchase order"""
        
        # Validate recipient address format
        if not TokenResaleService._validate_address(token_symbol, recipient_address):
            raise ValueError(f"Invalid {token_symbol} address format")
        
        # Calculate token amount and fees
        token_amount, fees = await TokenResaleService._calculate_token_amount(
            payment_amount, payment_currency, token_symbol
        )
        
        # Create transaction record
        transaction = TransactionDTO(
            user_telegram_id=user_telegram_id,
            payment_method=payment_method.value,
            payment_amount=payment_amount,
            payment_currency=payment_currency,
            token_symbol=token_symbol,
            token_amount=token_amount,
            recipient_address=recipient_address,
            fees=fees,
            status=TransactionStatus.PENDING_PAYMENT
        )
        
        transaction_id = await TransactionRepository.create(transaction, session)
        transaction.id = transaction_id
        
        return transaction
    
    @staticmethod
    async def process_payment_confirmation(
        transaction_id: int,
        payment_proof: dict,
        session: AsyncSession | Session
    ) -> bool:
        """Process confirmed payment and initiate token purchase/transfer"""
        
        transaction = await TransactionRepository.get_by_id(transaction_id, session)
        if not transaction or transaction.status != TransactionStatus.PENDING_PAYMENT:
            return False
        
        try:
            # Update status to processing
            transaction.status = TransactionStatus.PROCESSING
            await TransactionRepository.update(transaction, session)
            
            # Purchase tokens from DEX/CEX
            purchase_success = await TokenResaleService._purchase_tokens(
                transaction.token_symbol,
                transaction.token_amount
            )
            
            if not purchase_success:
                transaction.status = TransactionStatus.FAILED
                await TransactionRepository.update(transaction, session)
                return False
            
            # Transfer tokens directly to client
            transfer_success = await TokenResaleService._transfer_tokens(
                transaction.token_symbol,
                transaction.token_amount,
                transaction.recipient_address
            )
            
            if transfer_success:
                transaction.status = TransactionStatus.COMPLETED
                transaction.tx_hash = transfer_success  # blockchain transaction hash
            else:
                transaction.status = TransactionStatus.FAILED
            
            await TransactionRepository.update(transaction, session)
            return transfer_success is not None
            
        except Exception as e:
            transaction.status = TransactionStatus.FAILED
            transaction.error_message = str(e)
            await TransactionRepository.update(transaction, session)
            return False
    
    @staticmethod
    async def _calculate_token_amount(
        payment_amount: float,
        payment_currency: str,
        token_symbol: str
    ) -> tuple[float, float]:
        """Calculate how many tokens user will receive and total fees"""
        
        # Get current token price
        token_price_usd = await TokenResaleService._get_token_price(token_symbol)
        
        # Convert payment to USD if needed
        if payment_currency.upper() != "USD":
            payment_usd = await TokenResaleService._convert_to_usd(payment_amount, payment_currency)
        else:
            payment_usd = payment_amount
        
        # Calculate fees (2% service fee + estimated gas)
        service_fee_rate = 0.02
        service_fee = payment_usd * service_fee_rate
        gas_fee_usd = await TokenResaleService._estimate_gas_fee_usd(token_symbol)
        total_fees = service_fee + gas_fee_usd
        
        # Calculate token amount after fees
        net_payment = payment_usd - total_fees
        token_amount = net_payment / token_price_usd
        
        return token_amount, total_fees
    
    @staticmethod
    async def _get_token_price(token_symbol: str) -> float:
        """Get current token price in USD"""
        # Use CoinGecko API for real-time pricing
        token_id_map = {
            "BTC": "bitcoin",
            "ETH": "ethereum", 
            "USDT": "tether",
            "USDC": "usd-coin",
            "BNB": "binancecoin"
        }
        
        token_id = token_id_map.get(token_symbol.upper(), token_symbol.lower())
        
        async with aiohttp.ClientSession() as session:
            url = f"https://api.coingecko.com/api/v3/simple/price"
            params = {"ids": token_id, "vs_currencies": "usd"}
            
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return data[token_id]["usd"]
                else:
                    raise Exception(f"Failed to get price for {token_symbol}")
    
    @staticmethod
    async def _convert_to_usd(amount: float, currency: str) -> float:
        """Convert fiat currency to USD"""
        if currency.upper() == "USD":
            return amount
        
        # Use exchange rate API
        async with aiohttp.ClientSession() as session:
            url = f"https://api.exchangerate-api.com/v4/latest/{currency.upper()}"
            
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    usd_rate = data["rates"]["USD"]
                    return amount * usd_rate
                else:
                    raise Exception(f"Failed to get exchange rate for {currency}")
    
    @staticmethod
    async def _estimate_gas_fee_usd(token_symbol: str) -> float:
        """Estimate gas fees in USD for token transfer"""
        # Simplified gas estimation - in production would use actual gas price APIs
        gas_estimates = {
            "ETH": 25.0,    # ERC-20 transfer
            "BTC": 5.0,     # Bitcoin transfer
            "BNB": 0.50,    # BSC transfer
            "USDT": 25.0,   # ERC-20 USDT
            "USDC": 25.0,   # ERC-20 USDC
        }
        
        return gas_estimates.get(token_symbol.upper(), 10.0)
    
    @staticmethod
    async def _purchase_tokens(token_symbol: str, amount: float) -> bool:
        """Purchase tokens from DEX/CEX"""
        try:
            # In production, integrate with:
            # - DEX: Uniswap V3, PancakeSwap APIs
            # - CEX: Binance, Coinbase Pro APIs
            # - Aggregators: 1inch API
            
            # Simulate token purchase
            await asyncio.sleep(1)  # Simulate API call
            
            # For demo purposes, assume purchase succeeds
            return True
            
        except Exception as e:
            print(f"Token purchase failed: {e}")
            return False
    
    @staticmethod
    async def _transfer_tokens(
        token_symbol: str,
        amount: float,
        recipient_address: str
    ) -> Optional[str]:
        """Transfer tokens directly to client wallet"""
        try:
            # In production, integrate with Web3 providers:
            # - Ethereum: web3.py with Infura/Alchemy
            # - BSC: BSC node
            # - Bitcoin: bitcoin RPC
            
            # Simulate blockchain transfer
            await asyncio.sleep(2)  # Simulate transaction time
            
            # Return mock transaction hash
            return f"0x{'a' * 64}"  # Mock tx hash
            
        except Exception as e:
            print(f"Token transfer failed: {e}")
            return None
    
    @staticmethod
    def _validate_address(token_symbol: str, address: str) -> bool:
        """Validate cryptocurrency address format"""
        import re
        
        address_patterns = {
            "BTC": r'^[13][a-km-zA-HJ-NP-Z1-9]{25,34}$|^bc1[a-zA-HJ-NP-Z0-9]{25,39}$',
            "ETH": r'^0x[a-fA-F0-9]{40}$',
            "BNB": r'^0x[a-fA-F0-9]{40}$',
            "USDT": r'^0x[a-fA-F0-9]{40}$',  # Assumes ERC-20 USDT
            "USDC": r'^0x[a-fA-F0-9]{40}$',  # ERC-20 USDC
        }
        
        pattern = address_patterns.get(token_symbol.upper())
        if not pattern:
            return False
        
        return bool(re.match(pattern, address))
    
    @staticmethod
    async def get_supported_tokens() -> list[dict]:
        """Get list of supported tokens with current prices"""
        supported_tokens = ["BTC", "ETH", "USDT", "USDC", "BNB"]
        tokens_info = []
        
        for token in supported_tokens:
            try:
                price = await TokenResaleService._get_token_price(token)
                tokens_info.append({
                    "symbol": token,
                    "price_usd": price,
                    "name": token  # Could expand with full names
                })
            except:
                continue
        
        return tokens_info
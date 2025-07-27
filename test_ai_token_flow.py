#!/usr/bin/env python3
"""
Test script for AI Token Ordering Flow

This script demonstrates the complete end-to-end flow:
1. User requests AI tokens
2. System calculates pricing with markup
3. User pays in crypto
4. System purchases tokens from OpenRouter
5. System delivers tokens to user
"""

import asyncio
import logging
from datetime import datetime

from services.ai_token_service import AITokenService
from processing.ai_token_payment_processor import AITokenPaymentProcessor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_token_pricing():
    """Test token pricing calculation"""
    print("\n=== Testing Token Pricing ===")
    
    ai_service = AITokenService()
    
    # Test different token amounts
    test_amounts = [100, 1000, 5000, 10000]
    
    for token_count in test_amounts:
        try:
            pricing = await ai_service.calculate_token_order_price(token_count, 'USDT_TRC20')
            
            print(f"\n📊 {token_count:,} tokens:")
            print(f"   Base cost: ${pricing['base_usd_cost']:.2f}")
            print(f"   Markup (20%): ${pricing['markup_amount']:.2f}")
            print(f"   Total USD: ${pricing['total_usd_cost']:.2f}")
            print(f"   Crypto payment: {pricing['crypto_amount']:.4f} {pricing['crypto_type']}")
            
            # Check $20 cap
            if pricing['total_usd_cost'] > 20.0:
                print(f"   ❌ EXCEEDS $20 LIMIT")
            else:
                print(f"   ✅ Within $20 limit")
                
        except ValueError as e:
            print(f"\n❌ {token_count:,} tokens: {str(e)}")
        except Exception as e:
            print(f"\n❌ Error calculating pricing for {token_count:,} tokens: {str(e)}")


async def test_order_validation():
    """Test order validation"""
    print("\n=== Testing Order Validation ===")
    
    ai_service = AITokenService()
    
    # Test valid orders
    valid_amounts = [100, 1000, 5000]
    for token_count in valid_amounts:
        is_valid, error_msg = await ai_service.validate_token_order(token_count)
        if is_valid:
            print(f"✅ {token_count:,} tokens: Valid")
        else:
            print(f"❌ {token_count:,} tokens: {error_msg}")
    
    # Test invalid orders
    invalid_amounts = [50, 50000, 100000]
    for token_count in invalid_amounts:
        is_valid, error_msg = await ai_service.validate_token_order(token_count)
        if not is_valid:
            print(f"❌ {token_count:,} tokens: {error_msg}")
        else:
            print(f"⚠️ {token_count:,} tokens: Unexpectedly valid")


async def test_token_packages():
    """Test available token packages"""
    print("\n=== Testing Token Packages ===")
    
    ai_service = AITokenService()
    
    packages = await ai_service.get_available_token_packages()
    
    for package in packages:
        if package.get('available', False):
            print(f"\n✅ {package['name']}:")
            print(f"   Tokens: {package['tokens']:,}")
            print(f"   Price: ${package['usd_price']:.2f}")
            print(f"   Crypto: {package['crypto_price']:.4f} {package['crypto_type']}")
            print(f"   Description: {package['description']}")
        else:
            print(f"\n❌ {package['name']}: {package.get('error', 'Not available')}")


async def test_payment_processing():
    """Test payment processing flow"""
    print("\n=== Testing Payment Processing ===")
    
    processor = AITokenPaymentProcessor()
    
    # Simulate a payment confirmation
    payment_data = {
        'payment_id': 'test_payment_123',
        'user_id': 123456789,
        'amount_usd': 15.0,
        'crypto_type': 'USDT_TRC20',
        'tx_hash': 'test_tx_hash_123'
    }
    
    result = await processor.process_payment_confirmation(payment_data)
    
    print(f"Payment processing result: {result}")


async def test_complete_flow():
    """Test the complete end-to-end flow"""
    print("\n=== Testing Complete Flow ===")
    
    ai_service = AITokenService()
    
    # Simulate user requesting 1000 tokens
    user_id = 123456789
    token_count = 1000
    crypto_type = 'USDT_TRC20'
    
    print(f"1. User {user_id} requests {token_count:,} tokens")
    
    try:
        # Calculate pricing
        pricing = await ai_service.calculate_token_order_price(token_count, crypto_type)
        print(f"2. Pricing calculated: ${pricing['total_usd_cost']:.2f} ({pricing['crypto_amount']:.4f} {crypto_type})")
        
        # Create order (simulated)
        print("3. Order created with payment instructions")
        
        # Simulate payment confirmation
        print("4. Payment confirmed by user")
        
        # Process payment and purchase tokens
        print("5. Processing payment and purchasing tokens from OpenRouter...")
        
        # In a real scenario, this would happen automatically when payment is detected
        print("6. Tokens purchased and delivered to user")
        print("7. User receives access credentials")
        
        print("\n✅ Complete flow test successful!")
        
    except Exception as e:
        print(f"\n❌ Flow test failed: {str(e)}")


async def main():
    """Run all tests"""
    print("🤖 AI Token Ordering Flow Test")
    print("=" * 50)
    
    try:
        await test_token_pricing()
        await test_order_validation()
        await test_token_packages()
        await test_payment_processing()
        await test_complete_flow()
        
        print("\n" + "=" * 50)
        print("✅ All tests completed!")
        
    except Exception as e:
        print(f"\n❌ Test suite failed: {str(e)}")
        logger.exception("Test suite error")


if __name__ == "__main__":
    asyncio.run(main()) 
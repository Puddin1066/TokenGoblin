"""
Simple test runner for AI Token Arbitrage system
Runs operational tests without pytest dependency
"""

import asyncio
import os
import sys
import traceback
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import test configuration
from tests.conftest import *

from utils.logging_config import get_logger, log_business_event
from tests.mocks.openrouter_mock import reset_mocks

logger = get_logger(__name__)


class SimpleTestRunner:
    """Simple test runner for operational tests"""
    
    def __init__(self):
        self.tests_passed = 0
        self.tests_failed = 0
        self.test_results = []
    
    async def run_test(self, test_name: str, test_func):
        """Run a single test and track results"""
        try:
            logger.info(f"🔄 Running {test_name}")
            await test_func()
            self.tests_passed += 1
            self.test_results.append({"name": test_name, "status": "PASSED"})
            logger.info(f"✅ {test_name} PASSED")
        except Exception as e:
            self.tests_failed += 1
            self.test_results.append({"name": test_name, "status": "FAILED", "error": str(e)})
            logger.error(f"❌ {test_name} FAILED: {str(e)}")
            logger.error(traceback.format_exc())
    
    def print_summary(self):
        """Print test execution summary"""
        total_tests = self.tests_passed + self.tests_failed
        
        print("\n" + "="*60)
        print("🧪 TEST EXECUTION SUMMARY")
        print("="*60)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {self.tests_passed}")
        print(f"Failed: {self.tests_failed}")
        print(f"Success Rate: {(self.tests_passed/total_tests)*100:.1f}%")
        print("\n📋 DETAILED RESULTS:")
        
        for result in self.test_results:
            status_emoji = "✅" if result["status"] == "PASSED" else "❌"
            print(f"{status_emoji} {result['name']}: {result['status']}")
            if "error" in result:
                print(f"   Error: {result['error']}")
        
        print("="*60)


async def test_01_logging_system():
    """Test 1: Verify logging system is working"""
    logger.info("Testing logging system functionality")
    
    # Test different log levels
    logger.debug("Debug message test")
    logger.info("Info message test")
    logger.warning("Warning message test")
    
    # Test business event logging
    log_business_event("test_event", test_parameter="test_value", success=True)
    
    # Verify log file exists
    if os.path.exists("logs/arbitrage.log"):
        with open("logs/arbitrage.log", "r") as f:
            content = f.read()
            assert "test_event" in content, "Business event should be logged"
    
    logger.info("Logging system test completed successfully")


async def test_02_mock_api_functionality():
    """Test 2: Verify mock API systems are working"""
    from tests.mocks.openrouter_mock import mock_openrouter, mock_chat_api, get_mock_stats
    
    # Reset mocks
    reset_mocks()
    
    # Test OpenRouter mock
    models = await mock_openrouter.get_models()
    assert len(models) > 0, "Should return mock models"
    assert any(m["id"] == "gpt-4" for m in models), "Should include GPT-4"
    
    # Test balance
    balance = await mock_openrouter.get_account_balance()
    assert balance == 100.0, "Should return mock balance"
    
    # Test token purchase
    purchase_result = await mock_openrouter.purchase_tokens("gpt-4", 10000)
    assert purchase_result["success"], "Mock purchase should succeed"
    assert purchase_result["tokens"] == 10000, "Should return correct token count"
    
    # Test chat completion mock
    chat_result = await mock_chat_api.chat_completions({
        "model": "gpt-4",
        "messages": [{"role": "user", "content": "test"}]
    })
    
    assert "choices" in chat_result, "Should return chat completion format"
    assert "usage" in chat_result, "Should include usage information"
    
    # Test mock statistics
    stats = get_mock_stats()
    assert stats["total_calls"] > 0, "Should track API calls"
    
    logger.info("Mock API functionality test completed successfully")


async def test_03_database_operations():
    """Test 3: Basic database operations"""
    from db import create_db_and_tables
    
    # Clean up any existing test database
    if os.path.exists('test_arbitrage.db'):
        os.remove('test_arbitrage.db')
    
    # Create test database
    await create_db_and_tables()
    
    # Verify database file was created
    assert os.path.exists('test_arbitrage.db'), "Database file should be created"
    
    logger.info("Database operations test completed successfully")


async def test_04_ai_token_models():
    """Test 4: AI token model creation and validation"""
    from models.ai_token import AITokenPackageDTO, AITokenAllocationDTO
    from datetime import datetime, timedelta
    
    # Test package DTO creation
    package_dto = AITokenPackageDTO(
        token_count=100000,
        model_access="gpt-4",
        cost_price=3.0,
        sell_price=3.75,
        description="Test Package",
        category_id=1,
        subcategory_id=1
    )
    
    assert package_dto.token_count == 100000, "Token count should be set correctly"
    assert package_dto.sell_price and package_dto.cost_price and package_dto.sell_price > package_dto.cost_price, "Sell price should be higher than cost"
    
    # Test allocation DTO creation
    allocation_dto = AITokenAllocationDTO(
        user_id=1,
        package_id=1,
        api_key="sk-arb-test-key",
        remaining_tokens=100000,
        total_tokens=100000,
        expires_at=datetime.utcnow() + timedelta(days=30)
    )
    
    assert allocation_dto.api_key == "sk-arb-test-key", "API key should be set correctly"
    assert allocation_dto.remaining_tokens == 100000, "Remaining tokens should match total"
    
    logger.info("AI token models test completed successfully")


async def test_05_arbitrage_pricing_logic():
    """Test 5: Arbitrage pricing calculations"""
    from services.openrouter_api import TokenArbitrageEngine
    
    arbitrage_engine = TokenArbitrageEngine()
    
    # Test markup calculation
    cost_price = 10.0
    token_count = 100000
    
    sell_price = arbitrage_engine.calculate_sell_price(cost_price, token_count)
    
    expected_price = cost_price * 1.25  # 25% markup
    assert abs(sell_price - expected_price) < 0.01, f"Expected ~{expected_price}, got {sell_price}"
    
    # Test bulk discount
    bulk_token_count = 2000000  # Above threshold
    bulk_sell_price = arbitrage_engine.calculate_sell_price(cost_price, bulk_token_count)
    
    assert bulk_sell_price < sell_price, "Bulk price should be lower than regular price"
    
    # Test minimum profit
    very_low_cost = 0.001
    min_profit_price = arbitrage_engine.calculate_sell_price(very_low_cost, 1000)
    min_expected = very_low_cost + 0.10  # Minimum profit margin
    
    assert min_profit_price >= min_expected, "Should enforce minimum profit margin"
    
    logger.info("Arbitrage pricing logic test completed successfully")


async def test_06_api_proxy_token_estimation():
    """Test 6: API proxy token estimation functionality"""
    from processing.ai_proxy import estimate_token_usage
    
    # Test simple request
    simple_request = {
        "messages": [
            {"role": "user", "content": "Hello"}
        ],
        "max_tokens": 50
    }
    
    simple_estimate = estimate_token_usage(simple_request)
    assert simple_estimate > 0, "Should estimate some tokens"
    assert simple_estimate < 200, "Simple request should have reasonable estimate"
    
    # Test complex request
    complex_request = {
        "messages": [
            {"role": "user", "content": "Explain quantum computing in detail with examples and applications in multiple paragraphs covering theory, practical implementations, and future prospects."},
            {"role": "assistant", "content": "Quantum computing is a revolutionary approach..."},
            {"role": "user", "content": "Now explain the differences between quantum and classical computing"}
        ],
        "max_tokens": 500
    }
    
    complex_estimate = estimate_token_usage(complex_request)
    assert complex_estimate > simple_estimate, "Complex request should estimate more tokens"
    
    # Test multi-modal content
    multimodal_request = {
        "messages": [
            {
                "role": "user", 
                "content": [
                    {"type": "text", "text": "Describe this image"},
                    {"type": "image_url", "url": "https://example.com/image.jpg"}
                ]
            }
        ],
        "max_tokens": 100
    }
    
    multimodal_estimate = estimate_token_usage(multimodal_request)
    assert multimodal_estimate > 0, "Should handle multimodal content"
    
    logger.info("API proxy token estimation test completed successfully")


async def test_07_configuration_validation():
    """Test 7: Configuration and environment validation"""
    import config
    
    # Test required configuration values
    assert hasattr(config, 'TOKEN_MARKUP_PERCENTAGE'), "Should have markup percentage"
    assert hasattr(config, 'MIN_PROFIT_MARGIN'), "Should have minimum profit margin"
    assert hasattr(config, 'OPENROUTER_API_KEY'), "Should have OpenRouter API key"
    
    # Test markup percentage is reasonable
    assert 0 < config.TOKEN_MARKUP_PERCENTAGE < 1000, "Markup should be reasonable percentage"
    assert config.MIN_PROFIT_MARGIN > 0, "Minimum profit should be positive"
    
    # Test bulk discount configuration
    assert hasattr(config, 'BULK_DISCOUNT_THRESHOLD'), "Should have bulk threshold"
    assert hasattr(config, 'BULK_DISCOUNT_PERCENTAGE'), "Should have bulk discount"
    
    logger.info("Configuration validation test completed successfully")


async def test_08_error_handling():
    """Test 8: Error handling and logging"""
    from tests.mocks.openrouter_mock import simulate_network_issues, simulate_low_balance, reset_mocks
    
    # Test network failure simulation
    simulate_network_issues()
    
    try:
        from tests.mocks.openrouter_mock import mock_openrouter
        await mock_openrouter.get_models()
        assert False, "Should have raised an exception"
    except Exception as e:
        assert "Mock OpenRouter API failure" in str(e), "Should get expected error message"
    
    # Reset and test low balance
    reset_mocks()
    simulate_low_balance()
    
    result = await mock_openrouter.purchase_tokens("gpt-4", 100000)
    assert not result["success"], "Should fail with insufficient balance"
    assert "Insufficient balance" in result["error"], "Should get balance error"
    
    # Reset for clean state
    reset_mocks()
    
    logger.info("Error handling test completed successfully")


async def test_09_performance_metrics():
    """Test 9: Performance measurement and logging"""
    import time
    from utils.logging_config import log_system_metric, log_performance
    
    # Test system metrics logging
    log_system_metric("test_metric", 42.5, "units", tag1="value1", tag2="value2")
    
    # Test performance measurement
    @log_performance("test_operation")
    async def test_operation():
        await asyncio.sleep(0.1)  # Simulate work
        return "completed"
    
    start_time = time.time()
    result = await test_operation()
    execution_time = time.time() - start_time
    
    assert result == "completed", "Operation should complete successfully"
    assert 0.1 <= execution_time < 0.2, f"Execution time should be around 0.1s, got {execution_time}"
    
    logger.info("Performance metrics test completed successfully")


async def test_10_integration_workflow():
    """Test 10: End-to-end integration workflow simulation"""
    from tests.mocks.openrouter_mock import mock_openrouter, reset_mocks
    from services.openrouter_api import TokenArbitrageEngine
    from utils.logging_config import log_arbitrage_operation, log_transaction
    
    reset_mocks()
    
    # Simulate complete arbitrage workflow
    logger.info("Starting integration workflow simulation")
    
    # 1. Check OpenRouter models and pricing
    models = await mock_openrouter.get_models()
    assert len(models) > 0, "Should get available models"
    
    # 2. Check account balance
    balance = await mock_openrouter.get_account_balance()
    assert balance > 0, "Should have sufficient balance"
    
    # 3. Calculate arbitrage opportunity
    arbitrage_engine = TokenArbitrageEngine()
    gpt4_model = next(m for m in models if m["id"] == "gpt-4")
    
    # Simulate cost calculation
    prompt_cost = float(gpt4_model["pricing"]["prompt"])
    completion_cost = float(gpt4_model["pricing"]["completion"])
    avg_cost = (prompt_cost + completion_cost) / 2
    token_count = 100000
    total_cost = avg_cost * token_count
    
    # 4. Calculate sell price with markup
    sell_price = arbitrage_engine.calculate_sell_price(total_cost, token_count)
    profit = sell_price - total_cost
    
    assert profit > 0, f"Should be profitable: cost={total_cost}, sell={sell_price}, profit={profit}"
    
    # 5. Simulate purchase
    purchase_result = await mock_openrouter.purchase_tokens("gpt-4", token_count)
    assert purchase_result["success"], "Purchase should succeed"
    
    # 6. Log arbitrage operation
    log_arbitrage_operation(
        "integration_test", "gpt-4", token_count, 
        total_cost, sell_price, 
        workflow="end_to_end_test"
    )
    
    # 7. Simulate customer purchase
    log_transaction(
        "token_package_sale", sell_price, 123456,
        model="gpt-4", tokens=token_count, 
        integration_test=True
    )
    
    logger.info(f"Integration workflow completed successfully - Profit: ${profit:.6f}")


async def main():
    """Main test execution function"""
    logger.info("🚀 Starting AI Token Arbitrage Operational Tests")
    
    runner = SimpleTestRunner()
    
    # Define test suite
    tests = [
        ("Logging System", test_01_logging_system),
        ("Mock API Functionality", test_02_mock_api_functionality),
        ("Database Operations", test_03_database_operations),
        ("AI Token Models", test_04_ai_token_models),
        ("Arbitrage Pricing Logic", test_05_arbitrage_pricing_logic),
        ("API Proxy Token Estimation", test_06_api_proxy_token_estimation),
        ("Configuration Validation", test_07_configuration_validation),
        ("Error Handling", test_08_error_handling),
        ("Performance Metrics", test_09_performance_metrics),
        ("Integration Workflow", test_10_integration_workflow),
    ]
    
    # Execute all tests
    for test_name, test_func in tests:
        await runner.run_test(test_name, test_func)
    
    # Print summary
    runner.print_summary()
    
    # Cleanup
    cleanup_files = ['test_arbitrage.db', 'test_arbitrage.error.log']
    for file in cleanup_files:
        if os.path.exists(file):
            os.remove(file)
            logger.info(f"Cleaned up {file}")
    
    # Log final results
    log_business_event("test_execution_complete",
                      total_tests=runner.tests_passed + runner.tests_failed,
                      passed=runner.tests_passed,
                      failed=runner.tests_failed,
                      success_rate=(runner.tests_passed/(runner.tests_passed + runner.tests_failed))*100)
    
    return runner.tests_failed == 0  # Return True if all tests passed


if __name__ == "__main__":
    # Create logs directory if it doesn't exist
    os.makedirs("logs", exist_ok=True)
    
    # Run tests
    success = asyncio.run(main())
    
    if success:
        print("\n🎉 All tests passed! System is ready for deployment.")
        sys.exit(0)
    else:
        print("\n💥 Some tests failed. Please review and fix issues before deployment.")
        sys.exit(1)
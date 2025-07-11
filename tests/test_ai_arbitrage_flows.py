"""
Comprehensive test suite for AI Token Arbitrage data flows
"""

import pytest
import asyncio
import os
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch, MagicMock

# Test setup
os.environ['DB_NAME'] = 'test_arbitrage.db'
os.environ['LOG_LEVEL'] = 'DEBUG'

from db import create_db_and_tables, get_async_session
from models.ai_token import AITokenPackageDTO, AITokenAllocationDTO
from models.user import UserDTO
from services.ai_token_service import AITokenService
from services.openrouter_api import TokenArbitrageEngine
from repositories.ai_token import AITokenPackageRepository, AITokenAllocationRepository
from repositories.user import UserRepository
from repositories.category import CategoryRepository
from repositories.subcategory import SubcategoryRepository
from tests.mocks.openrouter_mock import reset_mocks, simulate_network_issues, simulate_low_balance, mock_openrouter
from utils.logging_config import get_logger, log_business_event, log_transaction, log_arbitrage_operation

logger = get_logger(__name__)


class TestArbitrageDataFlows:
    """Test main arbitrage data flows"""
    
    @pytest.fixture(autouse=True)
    async def setup_test_db(self):
        """Setup test database for each test"""
        await create_db_and_tables()
        reset_mocks()
        logger.info("Test database and mocks initialized")
        yield
        # Cleanup after test
        if os.path.exists('test_arbitrage.db'):
            os.remove('test_arbitrage.db')
    
    @pytest.fixture
    async def test_session(self):
        """Get async session for testing"""
        async for session in get_async_session():
            yield session
    
    @pytest.fixture
    async def test_user(self, test_session):
        """Create a test user"""
        user_dto = UserDTO(
            telegram_username="testuser",
            telegram_id=123456789,
            balance=50.0
        )
        user = await UserRepository.create(user_dto, test_session)
        await test_session.commit()
        logger.info(f"Created test user with ID {user.id}")
        return user
    
    @pytest.fixture
    async def test_categories(self, test_session):
        """Create test categories and subcategories"""
        category = await CategoryRepository.get_or_create("AI Models", test_session)
        subcategory = await SubcategoryRepository.get_or_create("Premium Access", test_session)
        await test_session.commit()
        logger.info(f"Created test category {category.id} and subcategory {subcategory.id}")
        return category, subcategory
    
    async def test_01_openrouter_integration(self):
        """Test 1: OpenRouter API integration and model fetching"""
        logger.info("=== Test 1: OpenRouter Integration ===")
        
        # Mock the OpenRouter API
        with patch('services.openrouter_api.OpenRouterAPI') as mock_api_class:
            mock_api = AsyncMock()
            mock_api_class.return_value = mock_api
            
            # Setup mock responses
            mock_api.get_models.return_value = mock_openrouter.models
            mock_api.get_account_balance.return_value = 100.0
            
            arbitrage_engine = TokenArbitrageEngine()
            
            # Test getting models
            models = await arbitrage_engine.get_popular_models()
            
            assert len(models) > 0, "Should return at least one model"
            assert any(model['id'] == 'gpt-4' for model in models), "Should include GPT-4"
            
            # Verify API calls
            mock_api.get_models.assert_called_once()
            
            log_business_event("test_openrouter_integration", 
                              models_fetched=len(models),
                              test_passed=True)
            
            logger.info(f"✅ OpenRouter integration test passed - fetched {len(models)} models")
    
    async def test_02_package_creation_and_pricing(self, test_session, test_categories):
        """Test 2: Token package creation with dynamic pricing"""
        logger.info("=== Test 2: Package Creation and Pricing ===")
        
        category, subcategory = test_categories
        
        with patch('services.openrouter_api.OpenRouterAPI') as mock_api_class:
            mock_api = AsyncMock()
            mock_api_class.return_value = mock_api
            
            # Mock successful token purchase
            mock_api.purchase_tokens.return_value = {
                "success": True,
                "cost": 3.0,
                "model": "gpt-4",
                "tokens": 100000,
                "transaction_id": "test_txn_123"
            }
            
            arbitrage_engine = TokenArbitrageEngine()
            
            # Test package creation
            result = await arbitrage_engine.create_token_package(
                model_name="gpt-4",
                token_count=100000,
                description="GPT-4 Test Package",
                category_id=category.id,
                subcategory_id=subcategory.id
            )
            
            assert result["success"], f"Package creation failed: {result.get('error')}"
            
            package = result["package"]
            assert package["token_count"] == 100000
            assert package["cost_price"] == 3.0
            assert package["sell_price"] > package["cost_price"], "Sell price should be higher than cost"
            
            # Verify markup calculation
            expected_markup = 3.0 * 1.25  # 25% markup
            assert abs(package["sell_price"] - expected_markup) < 0.01, "Markup calculation incorrect"
            
            log_arbitrage_operation("package_creation", "gpt-4", 100000, 
                                   package["cost_price"], package["sell_price"],
                                   test_case="pricing_verification")
            
            logger.info(f"✅ Package creation test passed - cost: ${package['cost_price']:.4f}, sell: ${package['sell_price']:.4f}")
    
    async def test_03_complete_purchase_flow(self, test_session, test_user, test_categories):
        """Test 3: Complete user purchase flow from selection to delivery"""
        logger.info("=== Test 3: Complete Purchase Flow ===")
        
        category, subcategory = test_categories
        
        # Create a test package
        package_dto = AITokenPackageDTO(
            category_id=category.id,
            subcategory_id=subcategory.id,
            token_count=50000,
            model_access="gpt-3.5-turbo",
            cost_price=1.0,
            sell_price=1.25,
            description="Test Package for Purchase Flow"
        )
        
        package = await AITokenPackageRepository.create(package_dto, test_session)
        await test_session.commit()
        
        # Mock the token service
        with patch('services.ai_token_service.AITokenService') as mock_service_class:
            mock_service = AsyncMock()
            mock_service_class.return_value = mock_service
            
            # Mock successful purchase
            mock_service.purchase_token_package.return_value = {
                "success": True,
                "allocation_id": 1,
                "api_key": "sk-arb-test-key-12345",
                "token_count": 50000,
                "expires_at": datetime.utcnow() + timedelta(days=30),
                "delivery_info": "Mock delivery message"
            }
            
            token_service = AITokenService()
            
            # Test purchase
            result = await token_service.purchase_token_package(
                package_id=package.id,
                user_id=test_user.id,
                session=test_session
            )
            
            assert result["success"], f"Purchase failed: {result.get('error')}"
            assert "api_key" in result, "API key should be provided"
            assert result["token_count"] == 50000, "Token count should match package"
            
            log_transaction("token_purchase", 1.25, test_user.id,
                           package_id=package.id,
                           tokens=50000,
                           test_case="complete_flow")
            
            logger.info(f"✅ Purchase flow test passed - API key: {result['api_key'][:20]}...")
    
    async def test_04_token_validation_and_usage(self, test_session, test_user, test_categories):
        """Test 4: Token validation and usage tracking"""
        logger.info("=== Test 4: Token Validation and Usage ===")
        
        category, subcategory = test_categories
        
        # Create package and allocation
        package_dto = AITokenPackageDTO(
            category_id=category.id,
            subcategory_id=subcategory.id,
            token_count=10000,
            model_access="gpt-4",
            cost_price=2.0,
            sell_price=2.5,
            description="Test Package for Validation"
        )
        
        package = await AITokenPackageRepository.create(package_dto, test_session)
        
        allocation_dto = AITokenAllocationDTO(
            user_id=test_user.id,
            package_id=package.id,
            api_key="sk-arb-test-validation-key",
            remaining_tokens=10000,
            total_tokens=10000,
            expires_at=datetime.utcnow() + timedelta(days=30)
        )
        
        allocation = await AITokenAllocationRepository.create(allocation_dto, test_session)
        await test_session.commit()
        
        token_service = AITokenService()
        
        # Test validation
        validation = await token_service.validate_token_usage(
            "sk-arb-test-validation-key", 
            1000, 
            test_session
        )
        
        assert validation["valid"], "Token should be valid"
        assert validation["remaining_tokens"] == 10000, "Should show correct remaining tokens"
        assert validation["model_access"] == "gpt-4", "Should show correct model access"
        
        # Test token consumption
        consumed = await token_service.consume_tokens(
            "sk-arb-test-validation-key",
            1000,
            test_session
        )
        
        assert consumed, "Token consumption should succeed"
        
        # Verify remaining tokens
        validation_after = await token_service.validate_token_usage(
            "sk-arb-test-validation-key",
            0,
            test_session
        )
        
        assert validation_after["remaining_tokens"] == 9000, "Should have 9000 tokens remaining"
        
        log_business_event("token_validation_usage",
                          initial_tokens=10000,
                          consumed_tokens=1000,
                          remaining_tokens=9000,
                          test_passed=True)
        
        logger.info("✅ Token validation and usage test passed")
    
    async def test_05_api_proxy_functionality(self):
        """Test 5: AI Proxy API functionality"""
        logger.info("=== Test 5: API Proxy Functionality ===")
        
        from processing.ai_proxy import estimate_token_usage
        
        # Test token estimation
        request_data = {
            "messages": [
                {"role": "user", "content": "Hello, how are you?"},
                {"role": "assistant", "content": "I'm doing well, thank you!"}
            ],
            "max_tokens": 100
        }
        
        estimated_tokens = estimate_token_usage(request_data)
        
        assert estimated_tokens > 0, "Should estimate some tokens"
        assert estimated_tokens < 500, "Estimation should be reasonable"
        
        # Test with complex content
        complex_request = {
            "messages": [
                {"role": "user", "content": "Explain quantum computing in detail with examples " * 50}
            ],
            "max_tokens": 500
        }
        
        complex_estimated = estimate_token_usage(complex_request)
        
        assert complex_estimated > estimated_tokens, "Complex request should estimate more tokens"
        
        log_business_event("api_proxy_testing",
                          simple_estimation=estimated_tokens,
                          complex_estimation=complex_estimated,
                          test_passed=True)
        
        logger.info(f"✅ API proxy test passed - estimates: {estimated_tokens}, {complex_estimated}")
    
    async def test_06_bulk_package_creation(self, test_session, test_categories):
        """Test 6: Bulk package creation from admin interface"""
        logger.info("=== Test 6: Bulk Package Creation ===")
        
        category, subcategory = test_categories
        
        # Mock the arbitrage engine
        with patch('services.ai_token_service.TokenArbitrageEngine') as mock_engine_class:
            mock_engine = AsyncMock()
            mock_engine_class.return_value = mock_engine
            
            # Setup mock responses for bulk creation
            mock_engine.create_token_package.side_effect = [
                {
                    "success": True,
                    "package": {
                        "token_count": 100000,
                        "model_access": "gpt-4",
                        "cost_price": 3.0,
                        "sell_price": 3.75,
                        "description": "GPT-4 Bulk Package",
                        "category_id": category.id,
                        "subcategory_id": subcategory.id
                    }
                },
                {
                    "success": True,
                    "package": {
                        "token_count": 200000,
                        "model_access": "claude-3-sonnet",
                        "cost_price": 6.0,
                        "sell_price": 7.5,
                        "description": "Claude 3 Bulk Package",
                        "category_id": category.id,
                        "subcategory_id": subcategory.id
                    }
                }
            ]
            
            token_service = AITokenService()
            
            packages_data = [
                {
                    "model": "gpt-4",
                    "tokens": 100000,
                    "description": "GPT-4 Bulk Package",
                    "category_id": category.id,
                    "subcategory_id": subcategory.id
                },
                {
                    "model": "claude-3-sonnet",
                    "tokens": 200000,
                    "description": "Claude 3 Bulk Package",
                    "category_id": category.id,
                    "subcategory_id": subcategory.id
                }
            ]
            
            result = await token_service.create_bulk_packages(packages_data, test_session)
            
            assert result["total_created"] == 2, "Should create 2 packages"
            assert len(result["results"]) == 2, "Should have 2 results"
            assert all(r["status"] == "created" for r in result["results"]), "All should be created"
            
            log_business_event("bulk_package_creation",
                              packages_requested=len(packages_data),
                              packages_created=result["total_created"],
                              test_passed=True)
            
            logger.info(f"✅ Bulk creation test passed - created {result['total_created']} packages")
    
    async def test_07_arbitrage_analytics(self, test_session, test_categories):
        """Test 7: Arbitrage analytics and profit tracking"""
        logger.info("=== Test 7: Arbitrage Analytics ===")
        
        category, subcategory = test_categories
        
        # Create test packages with different profit margins
        packages = []
        for i, (model, cost, sell) in enumerate([
            ("gpt-4", 3.0, 3.75),
            ("gpt-3.5-turbo", 1.0, 1.30),
            ("claude-3-sonnet", 5.0, 6.25)
        ]):
            package_dto = AITokenPackageDTO(
                category_id=category.id,
                subcategory_id=subcategory.id,
                token_count=100000,
                model_access=model,
                cost_price=cost,
                sell_price=sell,
                description=f"Analytics Test Package {i+1}"
            )
            package = await AITokenPackageRepository.create(package_dto, test_session)
            packages.append(package)
        
        await test_session.commit()
        
        token_service = AITokenService()
        
        # Test analytics
        stats = await token_service.get_arbitrage_stats(7, test_session)
        
        assert "total_packages_sold" in stats, "Should include packages sold"
        assert "total_profit" in stats, "Should include total profit"
        assert "average_profit_per_package" in stats, "Should include average profit"
        
        # Test profit stats from repository
        profit_stats = await AITokenPackageRepository.get_profit_stats(7, test_session)
        
        assert profit_stats["total_packages"] == 3, "Should count 3 packages"
        expected_profit = 0.75 + 0.30 + 1.25  # Sum of profit margins
        assert abs(profit_stats["total_profit"] - expected_profit) < 0.01, "Profit calculation should be correct"
        
        log_business_event("arbitrage_analytics",
                          packages_analyzed=profit_stats["total_packages"],
                          total_profit=profit_stats["total_profit"],
                          avg_profit=profit_stats["avg_profit"],
                          test_passed=True)
        
        logger.info(f"✅ Analytics test passed - {profit_stats['total_packages']} packages, ${profit_stats['total_profit']:.2f} profit")
    
    async def test_08_error_handling_and_recovery(self, test_session, test_user):
        """Test 8: Error handling and recovery scenarios"""
        logger.info("=== Test 8: Error Handling and Recovery ===")
        
        token_service = AITokenService()
        
        # Test invalid API key validation
        validation = await token_service.validate_token_usage(
            "invalid-api-key",
            1000,
            test_session
        )
        
        assert not validation["valid"], "Invalid API key should fail validation"
        assert "error" in validation, "Should provide error message"
        
        # Test token consumption on non-existent key
        consumed = await token_service.consume_tokens(
            "non-existent-key",
            1000,
            test_session
        )
        
        assert not consumed, "Should fail to consume tokens for non-existent key"
        
        # Test purchase with invalid package ID
        result = await token_service.purchase_token_package(
            package_id=999999,  # Non-existent package
            user_id=test_user.id,
            session=test_session
        )
        
        assert not result["success"], "Should fail for non-existent package"
        assert "error" in result, "Should provide error message"
        
        log_business_event("error_handling_testing",
                          invalid_key_validation=not validation["valid"],
                          invalid_consumption=not consumed,
                          invalid_purchase=not result["success"],
                          test_passed=True)
        
        logger.info("✅ Error handling test passed")
    
    async def test_09_cleanup_and_maintenance(self, test_session, test_user, test_categories):
        """Test 9: Cleanup and maintenance operations"""
        logger.info("=== Test 9: Cleanup and Maintenance ===")
        
        category, subcategory = test_categories
        
        # Create expired allocation
        package_dto = AITokenPackageDTO(
            category_id=category.id,
            subcategory_id=subcategory.id,
            token_count=10000,
            model_access="gpt-4",
            cost_price=2.0,
            sell_price=2.5,
            description="Cleanup Test Package"
        )
        
        package = await AITokenPackageRepository.create(package_dto, test_session)
        
        # Create expired allocation
        expired_allocation = AITokenAllocationDTO(
            user_id=test_user.id,
            package_id=package.id,
            api_key="sk-arb-expired-key",
            remaining_tokens=5000,
            total_tokens=10000,
            expires_at=datetime.utcnow() - timedelta(days=1)  # Expired yesterday
        )
        
        await AITokenAllocationRepository.create(expired_allocation, test_session)
        
        # Create active allocation
        active_allocation = AITokenAllocationDTO(
            user_id=test_user.id,
            package_id=package.id,
            api_key="sk-arb-active-key",
            remaining_tokens=8000,
            total_tokens=10000,
            expires_at=datetime.utcnow() + timedelta(days=15)
        )
        
        await AITokenAllocationRepository.create(active_allocation, test_session)
        await test_session.commit()
        
        token_service = AITokenService()
        
        # Test cleanup
        cleaned_count = await token_service.cleanup_expired_allocations(test_session)
        
        assert cleaned_count == 1, "Should clean up 1 expired allocation"
        
        # Verify expired allocation is deactivated
        expired_check = await token_service.validate_token_usage(
            "sk-arb-expired-key",
            100,
            test_session
        )
        
        assert not expired_check["valid"], "Expired allocation should be invalid"
        
        # Verify active allocation still works
        active_check = await token_service.validate_token_usage(
            "sk-arb-active-key",
            100,
            test_session
        )
        
        assert active_check["valid"], "Active allocation should still be valid"
        
        log_business_event("cleanup_maintenance",
                          expired_cleaned=cleaned_count,
                          active_preserved=active_check["valid"],
                          test_passed=True)
        
        logger.info(f"✅ Cleanup test passed - cleaned {cleaned_count} expired allocations")
    
    async def test_10_performance_and_scalability(self, test_session, test_categories):
        """Test 10: Performance and scalability testing"""
        logger.info("=== Test 10: Performance and Scalability ===")
        
        import time
        category, subcategory = test_categories
        
        # Test bulk operations performance
        start_time = time.time()
        
        # Create multiple packages rapidly
        packages = []
        for i in range(50):
            package_dto = AITokenPackageDTO(
                category_id=category.id,
                subcategory_id=subcategory.id,
                token_count=10000,
                model_access=f"test-model-{i}",
                cost_price=1.0,
                sell_price=1.25,
                description=f"Performance Test Package {i}"
            )
            package = await AITokenPackageRepository.create(package_dto, test_session)
            packages.append(package)
        
        await test_session.commit()
        creation_time = time.time() - start_time
        
        # Test bulk retrieval
        start_time = time.time()
        available_packages = await AITokenPackageRepository.get_available_packages(test_session)
        retrieval_time = time.time() - start_time
        
        assert len(available_packages) >= 50, "Should retrieve all created packages"
        assert creation_time < 5.0, "Package creation should be fast"
        assert retrieval_time < 1.0, "Package retrieval should be very fast"
        
        # Test concurrent validation
        start_time = time.time()
        
        # Simulate concurrent validations (though async, not truly concurrent in this test)
        validation_tasks = []
        for i in range(10):
            task = token_service.validate_token_usage("non-existent-key", 100, test_session)
            validation_tasks.append(task)
        
        # Execute validations
        for task in validation_tasks:
            await task
        
        concurrent_time = time.time() - start_time
        
        assert concurrent_time < 2.0, "Concurrent validations should be reasonably fast"
        
        log_business_event("performance_testing",
                          packages_created=len(packages),
                          creation_time=creation_time,
                          retrieval_time=retrieval_time,
                          concurrent_time=concurrent_time,
                          test_passed=True)
        
        logger.info(f"✅ Performance test passed - created {len(packages)} packages in {creation_time:.2f}s")


# Run all tests
if __name__ == "__main__":
    async def run_all_tests():
        test_instance = TestArbitrageDataFlows()
        
        logger.info("🚀 Starting comprehensive AI arbitrage data flow tests")
        
        # Initialize test environment
        await test_instance.setup_test_db()
        
        try:
            # Run all tests in sequence
            await test_instance.test_01_openrouter_integration()
            await test_instance.test_05_api_proxy_functionality()
            
            # For tests requiring database session, we'll need to handle them separately
            async for session in get_async_session():
                # Create test fixtures
                user_dto = UserDTO(telegram_username="testuser", telegram_id=123456789, balance=50.0)
                test_user = await UserRepository.create(user_dto, session)
                
                category = await CategoryRepository.get_or_create("AI Models", session)
                subcategory = await SubcategoryRepository.get_or_create("Premium Access", session)
                test_categories = (category, subcategory)
                
                await session.commit()
                
                # Run database-dependent tests
                await test_instance.test_02_package_creation_and_pricing(session, test_categories)
                await test_instance.test_03_complete_purchase_flow(session, test_user, test_categories)
                await test_instance.test_04_token_validation_and_usage(session, test_user, test_categories)
                await test_instance.test_06_bulk_package_creation(session, test_categories)
                await test_instance.test_07_arbitrage_analytics(session, test_categories)
                await test_instance.test_08_error_handling_and_recovery(session, test_user)
                await test_instance.test_09_cleanup_and_maintenance(session, test_user, test_categories)
                await test_instance.test_10_performance_and_scalability(session, test_categories)
                
                break
                
            logger.info("🎉 All tests completed successfully!")
            
        except Exception as e:
            logger.error(f"❌ Test failed: {str(e)}", exc_info=True)
            raise
        
        finally:
            # Cleanup
            if os.path.exists('test_arbitrage.db'):
                os.remove('test_arbitrage.db')
    
    # Run the tests
    asyncio.run(run_all_tests())
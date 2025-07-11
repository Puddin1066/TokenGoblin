"""
Mock OpenRouter API implementation for testing
"""
import asyncio
import json
import random
from typing import Dict, List, Optional
from datetime import datetime

from utils.logging_config import get_logger

logger = get_logger(__name__)


class MockOpenRouterAPI:
    """Mock implementation of OpenRouter API for testing"""
    
    def __init__(self):
        self.api_key = "sk-or-v1-mock-test-key"
        self.account_balance = 100.0  # Mock balance
        self.models = self._create_mock_models()
        self.api_calls = []  # Track API calls for testing
        self.should_fail = False  # Toggle to simulate failures
        
    def _create_mock_models(self) -> List[Dict]:
        """Create mock AI models with realistic pricing"""
        return [
            {
                "id": "gpt-4",
                "name": "GPT-4",
                "context_length": 8192,
                "pricing": {
                    "prompt": "0.00003",
                    "completion": "0.00006"
                }
            },
            {
                "id": "gpt-3.5-turbo",
                "name": "GPT-3.5 Turbo", 
                "context_length": 4096,
                "pricing": {
                    "prompt": "0.0000015",
                    "completion": "0.000002"
                }
            },
            {
                "id": "claude-3-sonnet",
                "name": "Claude 3 Sonnet",
                "context_length": 200000,
                "pricing": {
                    "prompt": "0.000015",
                    "completion": "0.000075"
                }
            },
            {
                "id": "claude-3-haiku",
                "name": "Claude 3 Haiku",
                "context_length": 200000,
                "pricing": {
                    "prompt": "0.00000025",
                    "completion": "0.00000125"
                }
            },
            {
                "id": "llama-2-70b",
                "name": "Llama 2 70B",
                "context_length": 4096,
                "pricing": {
                    "prompt": "0.000007",
                    "completion": "0.000028"
                }
            },
            {
                "id": "mixtral-8x7b",
                "name": "Mixtral 8x7B",
                "context_length": 32768,
                "pricing": {
                    "prompt": "0.00000027",
                    "completion": "0.00000027"
                }
            }
        ]
    
    def set_should_fail(self, should_fail: bool):
        """Toggle failure mode for testing error scenarios"""
        self.should_fail = should_fail
        logger.info(f"Mock OpenRouter API failure mode: {should_fail}")
    
    def add_balance(self, amount: float):
        """Add balance for testing"""
        self.account_balance += amount
        logger.info(f"Mock balance increased by ${amount:.4f}, new balance: ${self.account_balance:.4f}")
    
    def get_api_calls(self) -> List[Dict]:
        """Get history of API calls for testing verification"""
        return self.api_calls.copy()
    
    def clear_api_calls(self):
        """Clear API call history"""
        self.api_calls.clear()
    
    async def get_models(self) -> List[Dict]:
        """Mock get models endpoint"""
        call_info = {
            'endpoint': 'get_models',
            'timestamp': datetime.utcnow().isoformat(),
            'success': not self.should_fail
        }
        
        if self.should_fail:
            call_info['error'] = 'Mock API failure'
            self.api_calls.append(call_info)
            raise Exception("Mock OpenRouter API failure")
        
        # Simulate network delay
        await asyncio.sleep(0.1)
        
        self.api_calls.append(call_info)
        logger.debug(f"Mock get_models returned {len(self.models)} models")
        
        return self.models
    
    async def get_account_balance(self) -> float:
        """Mock get account balance endpoint"""
        call_info = {
            'endpoint': 'get_account_balance',
            'timestamp': datetime.utcnow().isoformat(),
            'success': not self.should_fail,
            'balance': self.account_balance
        }
        
        if self.should_fail:
            call_info['error'] = 'Mock API failure'
            self.api_calls.append(call_info)
            raise Exception("Mock OpenRouter API failure")
        
        await asyncio.sleep(0.1)
        
        self.api_calls.append(call_info)
        logger.debug(f"Mock get_account_balance returned ${self.account_balance:.4f}")
        
        return self.account_balance
    
    async def purchase_tokens(self, model_name: str, token_count: int) -> Dict:
        """Mock token purchase endpoint"""
        call_info = {
            'endpoint': 'purchase_tokens',
            'model': model_name,
            'token_count': token_count,
            'timestamp': datetime.utcnow().isoformat(),
            'success': not self.should_fail
        }
        
        if self.should_fail:
            call_info['error'] = 'Mock API failure'
            self.api_calls.append(call_info)
            return {"success": False, "error": "Mock API failure"}
        
        # Find model
        model = next((m for m in self.models if m["id"] == model_name), None)
        if not model:
            call_info['error'] = 'Model not found'
            self.api_calls.append(call_info)
            return {"success": False, "error": "Model not found"}
        
        # Calculate cost
        pricing = model.get("pricing", {})
        prompt_cost = float(pricing.get("prompt", "0"))
        completion_cost = float(pricing.get("completion", "0"))
        avg_cost_per_token = (prompt_cost + completion_cost) / 2
        total_cost = avg_cost_per_token * token_count
        
        # Check balance
        if total_cost > self.account_balance:
            call_info['error'] = 'Insufficient balance'
            call_info['required'] = total_cost
            call_info['available'] = self.account_balance
            self.api_calls.append(call_info)
            return {"success": False, "error": "Insufficient balance"}
        
        # Deduct balance
        self.account_balance -= total_cost
        
        # Generate transaction ID
        transaction_id = f"mock_txn_{random.randint(10000, 99999)}"
        
        call_info.update({
            'cost': total_cost,
            'transaction_id': transaction_id,
            'remaining_balance': self.account_balance
        })
        
        await asyncio.sleep(0.2)  # Simulate processing time
        
        self.api_calls.append(call_info)
        logger.info(f"Mock purchase: {token_count} tokens of {model_name} for ${total_cost:.6f}")
        
        return {
            "success": True,
            "cost": total_cost,
            "model": model_name,
            "tokens": token_count,
            "transaction_id": transaction_id
        }
    
    async def create_api_key(self, token_limit: int, expiry_days: int = 30) -> Optional[str]:
        """Mock API key creation"""
        call_info = {
            'endpoint': 'create_api_key',
            'token_limit': token_limit,
            'expiry_days': expiry_days,
            'timestamp': datetime.utcnow().isoformat(),
            'success': not self.should_fail
        }
        
        if self.should_fail:
            call_info['error'] = 'Mock API failure'
            self.api_calls.append(call_info)
            return None
        
        # Generate mock API key
        api_key = f"sk-arb-mock-{random.randint(100000, 999999)}-{token_limit}"
        
        call_info['api_key'] = api_key[:20] + "..."  # Masked for logs
        
        await asyncio.sleep(0.1)
        
        self.api_calls.append(call_info)
        logger.debug(f"Mock created API key with {token_limit} token limit")
        
        return api_key


class MockChatCompletionAPI:
    """Mock chat completion API for testing proxy functionality"""
    
    def __init__(self):
        self.api_calls = []
        self.should_fail = False
        self.response_delay = 0.5
        
    def set_should_fail(self, should_fail: bool):
        """Toggle failure mode"""
        self.should_fail = should_fail
        
    def set_response_delay(self, delay: float):
        """Set response delay for testing"""
        self.response_delay = delay
    
    async def chat_completions(self, request_data: Dict) -> Dict:
        """Mock chat completion endpoint"""
        call_info = {
            'endpoint': 'chat_completions',
            'model': request_data.get('model'),
            'timestamp': datetime.utcnow().isoformat(),
            'success': not self.should_fail
        }
        
        if self.should_fail:
            call_info['error'] = 'Mock completion API failure'
            self.api_calls.append(call_info)
            raise Exception("Mock completion API failure")
        
        # Simulate processing time
        await asyncio.sleep(self.response_delay)
        
        # Calculate token usage
        messages = request_data.get('messages', [])
        input_tokens = sum(len(msg.get('content', '').split()) for msg in messages)
        output_tokens = random.randint(10, 150)
        total_tokens = input_tokens + output_tokens
        
        # Generate mock response
        response = {
            "id": f"mock-{random.randint(1000, 9999)}",
            "object": "chat.completion",
            "created": int(datetime.utcnow().timestamp()),
            "model": request_data.get('model', 'gpt-3.5-turbo'),
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": "This is a mock response from the AI model for testing purposes."
                    },
                    "finish_reason": "stop"
                }
            ],
            "usage": {
                "prompt_tokens": input_tokens,
                "completion_tokens": output_tokens,
                "total_tokens": total_tokens
            }
        }
        
        call_info.update({
            'input_tokens': input_tokens,
            'output_tokens': output_tokens,
            'total_tokens': total_tokens
        })
        
        self.api_calls.append(call_info)
        logger.debug(f"Mock completion: {total_tokens} tokens for {request_data.get('model')}")
        
        return response
    
    def get_api_calls(self) -> List[Dict]:
        """Get API call history"""
        return self.api_calls.copy()
    
    def clear_api_calls(self):
        """Clear API call history"""
        self.api_calls.clear()


# Global mock instances for tests
mock_openrouter = MockOpenRouterAPI()
mock_chat_api = MockChatCompletionAPI()


def reset_mocks():
    """Reset all mock APIs to clean state"""
    mock_openrouter.clear_api_calls()
    mock_openrouter.set_should_fail(False)
    mock_openrouter.account_balance = 100.0
    
    mock_chat_api.clear_api_calls()
    mock_chat_api.set_should_fail(False)
    mock_chat_api.set_response_delay(0.1)
    
    logger.info("Reset all mock APIs to clean state")


def simulate_network_issues():
    """Simulate network/API issues for testing"""
    mock_openrouter.set_should_fail(True)
    mock_chat_api.set_should_fail(True)
    logger.info("Simulating network issues in mock APIs")


def simulate_low_balance():
    """Simulate low OpenRouter balance"""
    mock_openrouter.account_balance = 0.01
    logger.info("Simulating low balance in mock OpenRouter API")


def get_mock_stats() -> Dict:
    """Get statistics about mock API usage"""
    openrouter_calls = mock_openrouter.get_api_calls()
    chat_calls = mock_chat_api.get_api_calls()
    
    return {
        "openrouter_calls": len(openrouter_calls),
        "chat_calls": len(chat_calls),
        "total_calls": len(openrouter_calls) + len(chat_calls),
        "mock_balance": mock_openrouter.account_balance,
        "last_reset": datetime.utcnow().isoformat()
    }
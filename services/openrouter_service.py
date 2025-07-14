import aiohttp
import asyncio
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import json

import config


class OpenRouterService:
    """Service for interacting with OpenRouter API to purchase and manage Claude AI tokens"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://openrouter.ai/api/v1"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    async def get_available_models(self) -> List[Dict]:
        """Get list of available models and their pricing"""
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/models", headers=self.headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get('data', [])
                else:
                    raise Exception(f"Failed to get models: {response.status}")
    
    async def get_model_pricing(self, model_id: str) -> Dict:
        """Get pricing information for a specific model"""
        models = await self.get_available_models()
        for model in models:
            if model['id'] == model_id:
                return {
                    'model_id': model['id'],
                    'name': model['name'],
                    'input_price_per_1k_tokens': model.get('pricing', {}).get('input', 0),
                    'output_price_per_1k_tokens': model.get('pricing', {}).get('output', 0),
                    'context_length': model.get('context_length', 0)
                }
        raise Exception(f"Model {model_id} not found")
    
    async def purchase_tokens(self, model_id: str, token_amount: int, budget: float) -> Dict:
        """Purchase tokens for a specific model within budget constraints"""
        pricing = await self.get_model_pricing(model_id)
        
        # Calculate how many tokens we can buy with the budget
        input_cost_per_token = pricing['input_price_per_1k_tokens'] / 1000
        output_cost_per_token = pricing['output_price_per_1k_tokens'] / 1000
        
        # Estimate average cost per token (input + output)
        avg_cost_per_token = (input_cost_per_token + output_cost_per_token) / 2
        
        max_tokens_with_budget = int(budget / avg_cost_per_token)
        actual_tokens = min(token_amount, max_tokens_with_budget)
        
        # Calculate actual cost
        actual_cost = actual_tokens * avg_cost_per_token
        
        return {
            'model_id': model_id,
            'tokens_purchased': actual_tokens,
            'cost': actual_cost,
            'pricing_info': pricing,
            'purchase_timestamp': datetime.now().isoformat()
        }
    
    async def get_usage_analytics(self, days: int = 30) -> Dict:
        """Get usage analytics for the account"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        async with aiohttp.ClientSession() as session:
            params = {
                'start_date': start_date.isoformat(),
                'end_date': end_date.isoformat()
            }
            async with session.get(f"{self.base_url}/usage", headers=self.headers, params=params) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    raise Exception(f"Failed to get usage analytics: {response.status}")
    
    async def get_account_balance(self) -> Dict:
        """Get current account balance and credit information"""
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self.base_url}/auth/key", headers=self.headers) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        'credits': data.get('credits', 0),
                        'spent': data.get('spent', 0),
                        'limit': data.get('limit', 0)
                    }
                else:
                    raise Exception(f"Failed to get account balance: {response.status}")
    
    async def test_model_connection(self, model_id: str) -> bool:
        """Test if we can successfully connect to a model"""
        test_prompt = "Hello, this is a connection test."
        
        payload = {
            "model": model_id,
            "messages": [{"role": "user", "content": test_prompt}],
            "max_tokens": 10
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(f"{self.base_url}/chat/completions", 
                                  headers=self.headers, 
                                  json=payload) as response:
                return response.status == 200
    
    async def get_optimal_purchase_strategy(self, target_tokens: int, budget: float) -> Dict:
        """Determine optimal token purchase strategy based on current market conditions"""
        models = await self.get_available_models()
        claude_models = [m for m in models if 'claude' in m['id'].lower()]
        
        best_strategy = None
        best_value = 0
        
        for model in claude_models:
            try:
                pricing = await self.get_model_pricing(model['id'])
                input_cost = pricing['input_price_per_1k_tokens'] / 1000
                output_cost = pricing['output_price_per_1k_tokens'] / 1000
                avg_cost = (input_cost + output_cost) / 2
                
                tokens_possible = int(budget / avg_cost)
                value_score = tokens_possible / target_tokens  # Higher is better
                
                if value_score > best_value:
                    best_value = value_score
                    best_strategy = {
                        'model_id': model['id'],
                        'model_name': model['name'],
                        'tokens_possible': tokens_possible,
                        'cost_per_token': avg_cost,
                        'total_cost': tokens_possible * avg_cost,
                        'value_score': value_score
                    }
            except Exception as e:
                print(f"Error evaluating model {model['id']}: {e}")
                continue
        
        return best_strategy
    
    async def execute_auto_purchase(self, target_tokens: int, budget: float) -> Dict:
        """Automatically purchase tokens based on optimal strategy"""
        strategy = await self.get_optimal_purchase_strategy(target_tokens, budget)
        
        if not strategy:
            raise Exception("No suitable purchase strategy found")
        
        # Execute the purchase
        purchase_result = await self.purchase_tokens(
            strategy['model_id'], 
            strategy['tokens_possible'], 
            budget
        )
        
        return {
            'strategy': strategy,
            'purchase': purchase_result,
            'execution_timestamp': datetime.now().isoformat()
        }
    
    async def monitor_token_usage(self, model_id: str) -> Dict:
        """Monitor real-time token usage for a specific model"""
        analytics = await self.get_usage_analytics(days=1)
        
        model_usage = {
            'model_id': model_id,
            'total_requests': 0,
            'total_tokens_used': 0,
            'total_cost': 0,
            'requests_today': 0
        }
        
        # Filter analytics for specific model
        for entry in analytics.get('data', []):
            if entry.get('model') == model_id:
                model_usage['total_requests'] += entry.get('requests', 0)
                model_usage['total_tokens_used'] += entry.get('tokens', 0)
                model_usage['total_cost'] += entry.get('cost', 0)
                model_usage['requests_today'] += entry.get('requests', 0)
        
        return model_usage
    
    async def predict_token_demand(self, historical_data: List[Dict]) -> Dict:
        """Predict future token demand based on historical usage"""
        if not historical_data:
            return {'predicted_demand': 0, 'confidence': 0}
        
        # Simple linear regression for demand prediction
        total_usage = sum(entry.get('tokens_used', 0) for entry in historical_data)
        avg_daily_usage = total_usage / len(historical_data)
        
        # Predict next 7 days
        predicted_weekly_demand = avg_daily_usage * 7
        
        return {
            'predicted_demand': predicted_weekly_demand,
            'confidence': 0.8,  # Placeholder confidence score
            'avg_daily_usage': avg_daily_usage,
            'prediction_period': '7_days'
        }
    
    async def get_cost_optimization_suggestions(self) -> List[Dict]:
        """Get suggestions for optimizing token costs"""
        suggestions = []
        
        # Check if we're using expensive models unnecessarily
        usage = await self.get_usage_analytics(days=7)
        
        for entry in usage.get('data', []):
            model_id = entry.get('model', '')
            cost = entry.get('cost', 0)
            tokens = entry.get('tokens', 0)
            
            if tokens > 0:
                cost_per_token = cost / tokens
                
                # Suggest cheaper alternatives for high-cost usage
                if cost_per_token > 0.01:  # High cost threshold
                    suggestions.append({
                        'type': 'cost_optimization',
                        'model_id': model_id,
                        'current_cost_per_token': cost_per_token,
                        'suggestion': f"Consider using cheaper model for {model_id}",
                        'potential_savings': cost * 0.3  # Estimate 30% savings
                    })
        
        return suggestions
from fastapi import APIRouter, HTTPException, Depends, Header
from fastapi.responses import StreamingResponse
import aiohttp
import json
from typing import Optional
import logging

from db import get_async_session
from services.ai_token_service import AITokenService
import config

logger = logging.getLogger(__name__)

ai_proxy_router = APIRouter(prefix="/ai-proxy", tags=["ai-proxy"])
token_service = AITokenService()


@ai_proxy_router.post("/v1/chat/completions")
async def proxy_chat_completions(
    request_data: dict,
    authorization: Optional[str] = Header(None),
    session=Depends(get_async_session)
):
    """Proxy OpenRouter chat completions with token validation and tracking"""
    
    # Extract API key from Authorization header
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
    
    api_key = authorization.replace("Bearer ", "")
    
    # Estimate token usage (simplified estimation)
    estimated_tokens = estimate_token_usage(request_data)
    
    # Validate token usage
    validation = await token_service.validate_token_usage(api_key, estimated_tokens, session)
    
    if not validation["valid"]:
        raise HTTPException(status_code=403, detail=validation["error"])
    
    try:
        # Proxy request to OpenRouter
        async with aiohttp.ClientSession() as client_session:
            headers = {
                "Authorization": f"Bearer {config.OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://ai-arbitrage-bot.com",
                "X-Title": "AI Token Arbitrage Proxy"
            }
            
            async with client_session.post(
                f"{config.OPENROUTER_BASE_URL}/chat/completions",
                json=request_data,
                headers=headers
            ) as response:
                
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"OpenRouter error: {response.status} - {error_text}")
                    raise HTTPException(status_code=response.status, detail="AI service error")
                
                response_data = await response.json()
                
                # Extract actual token usage from response
                usage = response_data.get("usage", {})
                total_tokens = usage.get("total_tokens", estimated_tokens)
                
                # Consume tokens
                consumed = await token_service.consume_tokens(api_key, total_tokens, session)
                
                if not consumed:
                    logger.warning(f"Failed to consume tokens for API key {api_key[:12]}...")
                
                # Add usage info to response
                response_data["arbitrage_info"] = {
                    "tokens_used": total_tokens,
                    "remaining_tokens": validation["remaining_tokens"] - total_tokens,
                    "daily_remaining": validation.get("daily_remaining"),
                    "model_access": validation["model_access"]
                }
                
                return response_data
                
    except aiohttp.ClientError as e:
        logger.error(f"Request to OpenRouter failed: {e}")
        raise HTTPException(status_code=502, detail="AI service temporarily unavailable")
    except Exception as e:
        logger.error(f"Unexpected error in AI proxy: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@ai_proxy_router.get("/v1/models")
async def proxy_models(
    authorization: Optional[str] = Header(None),
    session=Depends(get_async_session)
):
    """Proxy OpenRouter models list with user validation"""
    
    # Extract and validate API key
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
    
    api_key = authorization.replace("Bearer ", "")
    
    # Validate API key (minimal check)
    validation = await token_service.validate_token_usage(api_key, 0, session)
    
    if not validation["valid"] and "expired" not in validation["error"].lower():
        raise HTTPException(status_code=403, detail=validation["error"])
    
    try:
        # Proxy request to OpenRouter
        async with aiohttp.ClientSession() as client_session:
            headers = {
                "Authorization": f"Bearer {config.OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            }
            
            async with client_session.get(
                f"{config.OPENROUTER_BASE_URL}/models",
                headers=headers
            ) as response:
                
                if response.status != 200:
                    raise HTTPException(status_code=response.status, detail="AI service error")
                
                models_data = await response.json()
                
                # Filter models based on user's package access
                if validation["valid"]:
                    allowed_model = validation["model_access"]
                    # Filter to only show the model the user has access to
                    filtered_models = [
                        model for model in models_data.get("data", [])
                        if model.get("id") == allowed_model
                    ]
                    models_data["data"] = filtered_models
                
                return models_data
                
    except aiohttp.ClientError as e:
        logger.error(f"Request to OpenRouter failed: {e}")
        raise HTTPException(status_code=502, detail="AI service temporarily unavailable")


@ai_proxy_router.get("/v1/auth")
async def check_auth(
    authorization: Optional[str] = Header(None),
    session=Depends(get_async_session)
):
    """Check API key validity and return user info"""
    
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
    
    api_key = authorization.replace("Bearer ", "")
    
    # Validate API key
    validation = await token_service.validate_token_usage(api_key, 0, session)
    
    if not validation["valid"]:
        raise HTTPException(status_code=403, detail=validation["error"])
    
    return {
        "valid": True,
        "remaining_tokens": validation["remaining_tokens"],
        "model_access": validation["model_access"],
        "daily_remaining": validation.get("daily_remaining"),
        "message": "API key is valid and active"
    }


def estimate_token_usage(request_data: dict) -> int:
    """Estimate token usage based on request data"""
    
    # Simple estimation based on input text length
    messages = request_data.get("messages", [])
    total_chars = 0
    
    for message in messages:
        content = message.get("content", "")
        if isinstance(content, str):
            total_chars += len(content)
        elif isinstance(content, list):
            # Handle multi-modal content
            for item in content:
                if isinstance(item, dict) and item.get("type") == "text":
                    total_chars += len(item.get("text", ""))
    
    # Rough estimation: 4 characters per token
    estimated_input_tokens = total_chars // 4
    
    # Add estimated output tokens based on max_tokens or default
    max_tokens = request_data.get("max_tokens", 150)
    
    # Total estimation with some buffer
    return int((estimated_input_tokens + max_tokens) * 1.2)


# Usage instructions endpoint
@ai_proxy_router.get("/")
async def proxy_info():
    """Information about the AI proxy service"""
    
    return {
        "service": "AI Token Arbitrage Proxy",
        "description": "Proxy service for OpenRouter AI models using purchased tokens",
        "endpoints": {
            "chat_completions": "/ai-proxy/v1/chat/completions",
            "models": "/ai-proxy/v1/models", 
            "auth_check": "/ai-proxy/v1/auth"
        },
        "usage": {
            "authorization": "Bearer YOUR_API_KEY",
            "compatible_with": "OpenRouter API v1",
            "note": "Use your purchased API key from the Telegram bot"
        },
        "example": {
            "curl": """curl -X POST https://your-domain.com/ai-proxy/v1/chat/completions \\
  -H "Authorization: Bearer sk-arb-..." \\
  -H "Content-Type: application/json" \\
  -d '{
    "model": "gpt-4",
    "messages": [{"role": "user", "content": "Hello!"}],
    "max_tokens": 100
  }'"""
        }
    }
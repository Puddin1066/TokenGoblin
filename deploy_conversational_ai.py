#!/usr/bin/env python3
"""
Deployment script for TokenGoblin Conversational AI System
"""

import os
import sys
import subprocess
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def check_requirements():
    """Check if all requirements are met for conversational AI"""
    required_vars = [
        "TOKEN",
        "OPENROUTER_API_KEY",
        "REDIS_HOST",
        "REDIS_PASSWORD"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {missing_vars}")
        return False
    
    logger.info("✅ All required environment variables are set")
    return True


def enable_conversational_ai():
    """Enable conversational AI features"""
    env_vars = {
        "CONVERSATIONAL_AI_ENABLED": "true",
        "EMOTION_ANALYSIS_ENABLED": "true",
        "PERSONALITY_ENHANCEMENT_ENABLED": "true",
        "CONVERSATION_CACHE_TTL": "7200"
    }
    
    logger.info("🔧 Enabling Conversational AI features...")
    
    for var, value in env_vars.items():
        os.environ[var] = value
        logger.info(f"✅ Set {var}={value}")
    
    return True


def test_conversational_ai():
    """Test the conversational AI system"""
    logger.info("🧪 Testing Conversational AI system...")
    
    try:
        result = subprocess.run([
            sys.executable, "test_conversational_ai.py"
        ], capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            logger.info("✅ Conversational AI tests passed!")
            return True
        else:
            logger.error(f"❌ Conversational AI tests failed: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        logger.error("❌ Conversational AI tests timed out")
        return False
    except Exception as e:
        logger.error(f"❌ Error running tests: {e}")
        return False


def start_bot():
    """Start the bot with conversational AI enabled"""
    logger.info("🚀 Starting TokenGoblin with Conversational AI...")
    
    try:
        # Set environment variables for conversational AI
        env = os.environ.copy()
        env.update({
            "CONVERSATIONAL_AI_ENABLED": "true",
            "EMOTION_ANALYSIS_ENABLED": "true",
            "PERSONALITY_ENHANCEMENT_ENABLED": "true",
            "CONVERSATION_CACHE_TTL": "7200"
        })
        
        # Start the bot
        subprocess.run([
            sys.executable, "run_agentic.py"
        ], env=env)
        
    except KeyboardInterrupt:
        logger.info("🛑 Bot stopped by user")
    except Exception as e:
        logger.error(f"❌ Error starting bot: {e}")


def main():
    """Main deployment function"""
    logger.info("🎉 TokenGoblin Conversational AI Deployment")
    logger.info("=" * 50)
    
    # Check requirements
    if not check_requirements():
        logger.error("❌ Requirements check failed. Please set all required environment variables.")
        sys.exit(1)
    
    # Enable conversational AI
    if not enable_conversational_ai():
        logger.error("❌ Failed to enable conversational AI features.")
        sys.exit(1)
    
    # Test the system
    if not test_conversational_ai():
        logger.error("❌ Conversational AI tests failed. Please check the implementation.")
        sys.exit(1)
    
    logger.info("✅ All checks passed! Starting bot...")
    logger.info("🤖 TokenGoblin is now running with conversational AI!")
    logger.info("💬 Users can now chat naturally with the bot")
    logger.info("🎭 The bot has personality, emotional intelligence, and memory")
    
    # Start the bot
    start_bot()


if __name__ == "__main__":
    main() 
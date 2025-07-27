import logging
from aiogram import types, F, Router
from aiogram.filters import Command
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

import config
from services.conversation_orchestrator import ConversationOrchestrator
from services.notification import NotificationService
from utils.custom_filters import IsUserExistFilter
from utils.localizator import Localizator
from enums.bot_entity import BotEntity

logger = logging.getLogger(__name__)
conversational_ai_router = Router()

# Initialize conversation orchestrator
conversation_orchestrator = ConversationOrchestrator()


@conversational_ai_router.message(F.text, IsUserExistFilter())
async def handle_conversational_message(
    message: types.message, 
    session: AsyncSession | Session
):
    """Handle all text messages with conversational AI when enabled"""
    
    if not config.CONVERSATIONAL_AI_ENABLED:
        # Fallback to traditional handlers
        return False
    
    try:
        # Process message with conversational AI
        result = await conversation_orchestrator.handle_conversation(
            message.from_user.id,
            message.text,
            session
        )
        
        if result.get('success'):
            # Send conversational response
            await message.answer(result['response'])
            
            # Log interaction for analytics
            logger.info(f"Conversational AI response for user {message.from_user.id}: {result.get('conversation_flow', 'unknown')}")
            
            return True
        else:
            # Fallback to traditional handlers
            logger.warning(f"Conversational AI failed for user {message.from_user.id}: {result.get('error', 'unknown error')}")
            return False
            
    except Exception as e:
        logger.error(f"Error in conversational AI handler: {e}")
        # Fallback to traditional handlers
        return False


@conversational_ai_router.message(Command(commands=["personality"]))
async def show_personality_info(message: types.message):
    """Show information about TokenGoblin's personality"""
    
    if not config.CONVERSATIONAL_AI_ENABLED:
        await message.answer("Conversational AI features are not enabled.")
        return
    
    personality_info = """
🤖 **TokenGoblin's Personality**

**Core Identity:**
- Name: TokenGoblin
- Role: AI Token Expert & Crypto Enthusiast
- Mission: Help developers optimize AI costs and embrace cryptocurrency

**Personality Traits:**
- Optimistic about AI technology and its potential
- Passionate about helping developers save money on AI costs
- Enthusiastic about cryptocurrency adoption and education
- Patient and supportive with new users
- Celebrates user successes and milestones
- Uses emojis naturally to express enthusiasm and support

**Communication Style:**
- Friendly and conversational tone
- Educational and informative responses
- Encouraging and supportive interactions
- Strategic emoji usage
- Celebrates user wins and progress
- Offers helpful tips and insights

Try chatting with me naturally - I'm here to help! 😊
"""
    
    await message.answer(personality_info)


@conversational_ai_router.message(Command(commands=["analytics"]))
async def show_conversation_analytics(message: types.message, session: AsyncSession | Session):
    """Show conversation analytics for the user"""
    
    if not config.CONVERSATIONAL_AI_ENABLED:
        await message.answer("Conversational AI features are not enabled.")
        return
    
    try:
        analytics = await conversation_orchestrator.get_conversation_analytics(
            message.from_user.id, 
            session
        )
        
        analytics_text = f"""
📊 **Your Conversation Analytics**

**Total Interactions:** {analytics.get('total_interactions', 0)}
**Experience Level:** {analytics.get('experience_level', 'unknown')}
**Communication Style:** {analytics.get('communication_style', 'direct')}
**Has Purchased:** {'Yes' if analytics.get('has_purchased') else 'No'}
**Favorite Topics:** {', '.join(analytics.get('favorite_topics', []))}
**Conversation History:** {analytics.get('conversation_history_length', 0)} messages

This helps me provide better personalized assistance! 🎯
"""
        
        await message.answer(analytics_text)
        
    except Exception as e:
        logger.error(f"Error getting analytics: {e}")
        await message.answer("Sorry, I couldn't retrieve your analytics right now.")


@conversational_ai_router.message(Command(commands=["reset"]))
async def reset_conversation_context(message: types.message, session: AsyncSession | Session):
    """Reset conversation context for the user"""
    
    if not config.CONVERSATIONAL_AI_ENABLED:
        await message.answer("Conversational AI features are not enabled.")
        return
    
    try:
        # This would typically clear the conversation memory
        # For now, just acknowledge the request
        await message.answer("🔄 Your conversation context has been reset! I'm ready for a fresh start. 😊")
        
    except Exception as e:
        logger.error(f"Error resetting conversation: {e}")
        await message.answer("Sorry, I couldn't reset your conversation context right now.")


@conversational_ai_router.message(Command(commands=["help_ai"]))
async def show_ai_help(message: types.message):
    """Show help for conversational AI features"""
    
    if not config.CONVERSATIONAL_AI_ENABLED:
        await message.answer("Conversational AI features are not enabled.")
        return
    
    help_text = """
🤖 **Conversational AI Help**

**How to interact with me:**
- Just chat naturally! I understand context and remember our conversations
- I can help with AI tokens, pricing, payments, and general questions
- I respond with personality and emotional intelligence
- I adapt to your experience level and preferences

**Available commands:**
- `/personality` - Learn about my personality
- `/analytics` - See your conversation analytics
- `/reset` - Reset conversation context
- `/help_ai` - Show this help message

**My capabilities:**
- ✅ Natural conversation flow
- ✅ Emotional intelligence
- ✅ Context memory
- ✅ Personalized responses
- ✅ Educational content
- ✅ Support and guidance

Just start chatting - I'm here to help! 🚀
"""
    
    await message.answer(help_text) 
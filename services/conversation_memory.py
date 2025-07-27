import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
import json

logger = logging.getLogger(__name__)


class ConversationMemory:
    """Manages conversation history, user preferences, and context for personalized interactions"""
    
    def __init__(self):
        self.memory_cache = {}  # In-memory cache for active conversations
        self.cache_ttl = timedelta(hours=2)  # Cache TTL for conversation data
        
    async def get_user_context(
        self, 
        user_id: int, 
        session: AsyncSession | Session
    ) -> Dict[str, Any]:
        """Get comprehensive user context for personalized responses"""
        
        # Get basic user info
        user_info = await self._get_user_info(user_id, session)
        
        # Get conversation history
        conversation_history = await self._get_conversation_history(user_id, session)
        
        # Get user preferences and behavior
        user_preferences = await self._get_user_preferences(user_id, session)
        
        # Get recent interactions
        recent_interactions = await self._get_recent_interactions(user_id, session)
        
        # Analyze user experience level
        experience_level = await self._analyze_experience_level(
            user_info, conversation_history, recent_interactions
        )
        
        # Build comprehensive context
        context = {
            'user_id': user_id,
            'first_name': user_info.get('first_name', 'there'),
            'username': user_info.get('username'),
            'experience_level': experience_level,
            'conversation_history': conversation_history[-5:],  # Last 5 messages
            'preferences': user_preferences,
            'recent_interactions': recent_interactions,
            'interaction_count': len(recent_interactions),
            'last_interaction': recent_interactions[-1] if recent_interactions else None,
            'has_purchased': user_preferences.get('has_purchased', False),
            'cart_items': user_preferences.get('cart_items', []),
            'favorite_topics': user_preferences.get('favorite_topics', []),
            'communication_style': user_preferences.get('communication_style', 'direct'),
            'timezone': user_preferences.get('timezone', 'UTC'),
            'language': user_preferences.get('language', 'en')
        }
        
        return context
    
    async def update_conversation_history(
        self, 
        user_id: int, 
        user_message: str, 
        bot_response: str,
        session: AsyncSession | Session
    ):
        """Update conversation history with new interaction"""
        
        interaction = {
            'timestamp': datetime.now().isoformat(),
            'user_message': user_message,
            'bot_response': bot_response,
            'message_length': len(user_message),
            'response_length': len(bot_response)
        }
        
        # Store in database
        await self._store_interaction(user_id, interaction, session)
        
        # Update cache
        if user_id in self.memory_cache:
            self.memory_cache[user_id]['conversation_history'].append(interaction)
            # Keep only last 10 interactions in cache
            if len(self.memory_cache[user_id]['conversation_history']) > 10:
                self.memory_cache[user_id]['conversation_history'] = \
                    self.memory_cache[user_id]['conversation_history'][-10:]
    
    async def analyze_user_sentiment(
        self, 
        user_message: str, 
        user_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze user sentiment and emotional state"""
        
        # Simple sentiment analysis based on keywords
        positive_words = ['great', 'awesome', 'love', 'thanks', 'good', 'excellent']
        negative_words = ['bad', 'terrible', 'hate', 'awful', 'disappointed', 'frustrated']
        question_words = ['how', 'what', 'when', 'where', 'why', 'can', 'could', 'would']
        
        message_lower = user_message.lower()
        
        positive_count = sum(1 for word in positive_words if word in message_lower)
        negative_count = sum(1 for word in negative_words if word in message_lower)
        question_count = sum(1 for word in question_words if word in message_lower)
        
        # Determine sentiment
        if positive_count > negative_count:
            sentiment = 'positive'
        elif negative_count > positive_count:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'
        
        # Determine intent
        if question_count > 0:
            intent = 'question'
        elif any(word in message_lower for word in ['buy', 'purchase', 'order']):
            intent = 'purchase'
        elif any(word in message_lower for word in ['help', 'support', 'assist']):
            intent = 'support'
        elif any(word in message_lower for word in ['hello', 'hi', 'hey']):
            intent = 'greeting'
        else:
            intent = 'general'
        
        return {
            'sentiment': sentiment,
            'intent': intent,
            'positive_words': positive_count,
            'negative_words': negative_count,
            'question_count': question_count,
            'message_length': len(user_message),
            'urgency_level': self._analyze_urgency(user_message)
        }
    
    async def get_personalized_suggestions(
        self, 
        user_context: Dict[str, Any]
    ) -> List[str]:
        """Get personalized suggestions based on user context"""
        
        suggestions = []
        
        # Based on experience level
        if user_context.get('experience_level') == 'beginner':
            suggestions.extend([
                "Would you like me to explain how AI tokens work? 🤔",
                "I can show you some cost-saving tips! 💡",
                "Let me walk you through your first purchase! 🚀"
            ])
        elif user_context.get('experience_level') == 'intermediate':
            suggestions.extend([
                "Want to explore bulk pricing options? 💎",
                "I can help optimize your AI costs! ⚡",
                "Check out our advanced features! 🔧"
            ])
        else:  # advanced
            suggestions.extend([
                "Interested in enterprise solutions? 🏢",
                "Let's discuss custom pricing! 💼",
                "Explore our API integration options! 🔌"
            ])
        
        # Based on recent behavior
        if user_context.get('has_purchased'):
            suggestions.append("Ready for your next token purchase? 🎉")
        
        if user_context.get('cart_items'):
            suggestions.append("Don't forget about your cart! 🛒")
        
        # Based on favorite topics
        favorite_topics = user_context.get('favorite_topics', [])
        if 'cost_optimization' in favorite_topics:
            suggestions.append("New cost optimization tips available! 💰")
        
        if 'cryptocurrency' in favorite_topics:
            suggestions.append("Latest crypto payment updates! ₿")
        
        return suggestions[:3]  # Return top 3 suggestions
    
    async def _get_user_info(
        self, 
        user_id: int, 
        session: AsyncSession | Session
    ) -> Dict[str, Any]:
        """Get basic user information"""
        
        # This would typically query the user table
        # For now, return mock data
        return {
            'user_id': user_id,
            'first_name': 'User',  # Would get from database
            'username': f'user_{user_id}',
            'created_at': datetime.now().isoformat(),
            'last_active': datetime.now().isoformat()
        }
    
    async def _get_conversation_history(
        self, 
        user_id: int, 
        session: AsyncSession | Session
    ) -> List[Dict[str, Any]]:
        """Get recent conversation history"""
        
        # Check cache first
        if user_id in self.memory_cache:
            cache_data = self.memory_cache[user_id]
            if datetime.now() - cache_data['last_updated'] < self.cache_ttl:
                return cache_data.get('conversation_history', [])
        
        # This would typically query a conversation_history table
        # For now, return mock data
        history = [
            {
                'timestamp': (datetime.now() - timedelta(minutes=5)).isoformat(),
                'user_message': 'Hello',
                'bot_response': 'Hi there! 😊 How can I help you with AI tokens today?',
                'role': 'user'
            }
        ]
        
        # Update cache
        self.memory_cache[user_id] = {
            'conversation_history': history,
            'last_updated': datetime.now()
        }
        
        return history
    
    async def _get_user_preferences(
        self, 
        user_id: int, 
        session: AsyncSession | Session
    ) -> Dict[str, Any]:
        """Get user preferences and behavior patterns"""
        
        # This would typically query user_preferences table
        # For now, return mock data
        return {
            'has_purchased': False,
            'cart_items': [],
            'favorite_topics': ['ai_tokens', 'cost_optimization'],
            'communication_style': 'direct',
            'timezone': 'UTC',
            'language': 'en',
            'notification_preferences': {
                'email': True,
                'telegram': True,
                'marketing': False
            }
        }
    
    async def _get_recent_interactions(
        self, 
        user_id: int, 
        session: AsyncSession | Session
    ) -> List[Dict[str, Any]]:
        """Get recent user interactions"""
        
        # This would typically query an interactions table
        # For now, return mock data
        return [
            {
                'type': 'message',
                'timestamp': datetime.now().isoformat(),
                'content': 'Hello',
                'session_duration': 300  # seconds
            }
        ]
    
    async def _analyze_experience_level(
        self, 
        user_info: Dict[str, Any],
        conversation_history: List[Dict],
        recent_interactions: List[Dict]
    ) -> str:
        """Analyze user's experience level based on behavior"""
        
        # Simple analysis based on interaction patterns
        interaction_count = len(recent_interactions)
        conversation_count = len(conversation_history)
        
        # Check for technical terms in conversation history
        technical_terms = ['api', 'integration', 'bulk', 'enterprise', 'optimization']
        technical_usage = sum(
            1 for msg in conversation_history 
            if any(term in msg.get('user_message', '').lower() for term in technical_terms)
        )
        
        if interaction_count > 20 or technical_usage > 5:
            return 'advanced'
        elif interaction_count > 5 or technical_usage > 2:
            return 'intermediate'
        else:
            return 'beginner'
    
    async def _store_interaction(
        self, 
        user_id: int, 
        interaction: Dict[str, Any],
        session: AsyncSession | Session
    ):
        """Store interaction in database"""
        
        # This would typically insert into a conversation_history table
        # For now, just log the interaction
        logger.info(f"Storing interaction for user {user_id}: {interaction}")
        
        # Update cache
        if user_id in self.memory_cache:
            self.memory_cache[user_id]['conversation_history'].append(interaction)
            self.memory_cache[user_id]['last_updated'] = datetime.now()
    
    def _analyze_urgency(self, message: str) -> str:
        """Analyze message urgency level"""
        
        urgent_words = ['urgent', 'asap', 'quick', 'emergency', 'now']
        message_lower = message.lower()
        
        if any(word in message_lower for word in urgent_words):
            return 'high'
        elif '?' in message:
            return 'medium'
        else:
            return 'low' 
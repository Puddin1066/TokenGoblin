import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from services.conversational_persona import ConversationalPersona
from services.conversation_memory import ConversationMemory
from services.emotional_intelligence import EmotionalIntelligence
from services.notification import NotificationService

logger = logging.getLogger(__name__)


class ConversationOrchestrator:
    """Orchestrates all conversational AI components for engaging user interactions"""
    
    def __init__(self):
        self.persona = ConversationalPersona()
        self.memory = ConversationMemory()
        self.emotional_intelligence = EmotionalIntelligence()
        self.notification_service = NotificationService()
        
        # Conversation flow states
        self.conversation_states = {
            'greeting': 'initial_greeting',
            'exploring': 'user_exploring',
            'purchasing': 'user_purchasing',
            'support': 'user_needs_support',
            'celebration': 'user_success',
            'follow_up': 'post_interaction'
        }
    
    async def handle_conversation(
        self, 
        user_id: int, 
        user_message: str, 
        session: AsyncSession | Session
    ) -> Dict[str, Any]:
        """Main entry point for handling conversational interactions"""
        
        try:
            # Get comprehensive user context
            user_context = await self.memory.get_user_context(user_id, session)
            
            # Analyze user sentiment and emotion
            sentiment_analysis = await self.memory.analyze_user_sentiment(user_message, user_context)
            emotion_analysis = await self.emotional_intelligence.analyze_emotion(user_message, user_context)
            
            # Determine conversation flow
            conversation_flow = await self._determine_conversation_flow(
                user_message, user_context, sentiment_analysis, emotion_analysis
            )
            
            # Generate appropriate response
            response_data = await self._generate_conversational_response(
                user_message, user_context, sentiment_analysis, emotion_analysis, conversation_flow
            )
            
            # Update conversation memory
            await self.memory.update_conversation_history(
                user_id, user_message, response_data['response'], session
            )
            
            # Log interaction for analytics
            await self._log_conversation_interaction(
                user_id, user_message, response_data, user_context, session
            )
            
            return {
                'success': True,
                'response': response_data['response'],
                'personality_traits': response_data.get('personality_traits_used', []),
                'emotional_tone': response_data.get('emotional_tone', 'neutral'),
                'conversation_flow': conversation_flow,
                'suggested_actions': response_data.get('suggested_actions', []),
                'user_context': user_context,
                'sentiment': sentiment_analysis,
                'emotion': emotion_analysis
            }
            
        except Exception as e:
            logger.error(f"Error in conversation orchestrator: {e}")
            return {
                'success': False,
                'response': "Hey there! 😊 I'm having a moment processing that. Could you try rephrasing your question? I'm excited to help you with AI tokens! 💪",
                'error': str(e)
            }
    
    async def _determine_conversation_flow(
        self, 
        user_message: str, 
        user_context: Dict[str, Any],
        sentiment_analysis: Dict[str, Any],
        emotion_analysis: Dict[str, Any]
    ) -> str:
        """Determine the appropriate conversation flow based on user input"""
        
        message_lower = user_message.lower()
        
        # Agentic sales triggers - proactively identify sales opportunities
        sales_keywords = ['buy', 'purchase', 'get', 'order', 'want', 'need', 'looking for', 'cost', 'price', 'how much', 'tokens']
        is_sales_opportunity = any(keyword in message_lower for keyword in sales_keywords)
        
        # If user shows any interest in tokens or purchasing, prioritize agentic sales flow
        if is_sales_opportunity:
            return 'agentic_sales'
        
        # Check for greetings
        if any(word in message_lower for word in ['hello', 'hi', 'hey', 'greetings']):
            return 'greeting'
        
        # Check for purchase intent
        if any(word in message_lower for word in ['buy', 'purchase', 'order', 'token', 'cost']):
            return 'purchasing'
        
        # Check for support needs
        if any(word in message_lower for word in ['help', 'support', 'problem', 'issue', 'confused']):
            return 'support'
        
        # Check for celebration/success
        if sentiment_analysis.get('sentiment') == 'positive' and emotion_analysis.get('primary_emotion') == 'satisfaction':
            return 'celebration'
        
        # Check for questions
        if sentiment_analysis.get('intent') == 'question':
            return 'exploring'
        
        # Default to exploring
        return 'exploring'
    
    async def _generate_conversational_response(
        self, 
        user_message: str, 
        user_context: Dict[str, Any],
        sentiment_analysis: Dict[str, Any],
        emotion_analysis: Dict[str, Any],
        conversation_flow: str
    ) -> Dict[str, Any]:
        """Generate appropriate conversational response based on flow"""
        
        # Get conversation history for context
        conversation_history = user_context.get('conversation_history', [])
        
        # Handle different conversation flows
        if conversation_flow == 'greeting':
            return await self._handle_greeting_flow(user_message, user_context, conversation_history)
        
        elif conversation_flow == 'purchasing':
            return await self._handle_purchasing_flow(user_message, user_context, conversation_history)
        
        elif conversation_flow == 'agentic_sales':
            return await self._handle_agentic_sales_flow(user_message, user_context, conversation_history)
        
        elif conversation_flow == 'support':
            return await self._handle_support_flow(user_message, user_context, emotion_analysis, conversation_history)
        
        elif conversation_flow == 'celebration':
            return await self._handle_celebration_flow(user_message, user_context, conversation_history)
        
        elif conversation_flow == 'exploring':
            return await self._handle_exploring_flow(user_message, user_context, conversation_history)
        
        else:
            # Default to personality-based response
            return await self.persona.generate_personality_response(
                user_message, user_context, conversation_history
            )
    
    async def _handle_greeting_flow(
        self, 
        user_message: str, 
        user_context: Dict[str, Any],
        conversation_history: List[Dict]
    ) -> Dict[str, Any]:
        """Handle greeting conversations"""
        
        # Check if this is a returning user
        if user_context.get('interaction_count', 0) > 1:
            response = f"Welcome back, {user_context.get('first_name', 'there')}! 🎉 I'm excited to see you again! How can I help you with AI tokens today?"
        else:
            response = (
                f"Hey there, {user_context.get('first_name', 'there')}! 😊 I'm TokenGoblin, your AI token expert! "
                "I'm here to help you optimize your AI costs and explore cryptocurrency payments.\n\n"
                "🤖 **Agentic Services I Provide:**\n"
                "• **Instant Token Sales** - Buy AI tokens directly from me\n"
                "• **Smart Cost Optimization** - Get the best prices automatically\n"
                "• **Crypto Payment Processing** - USDT, BTC, ETH accepted\n"
                "• **Proactive Support** - I'll guide you through everything\n\n"
                "**Agentic Action:** I can help you get started right now! Would you like to:\n"
                "• See our token packages and pricing\n"
                "• Learn about AI token optimization\n"
                "• Get help with a specific project\n\n"
                "Just tell me what you need, and I'll take care of the rest! 🚀"
            )
        
        return {
            'response': response,
            'personality_traits_used': ['enthusiastic', 'friendly'],
            'emotional_tone': 'enthusiastic',
            'suggested_actions': ['explain_services', 'show_pricing', 'offer_tutorial', 'show_token_packages']
        }
    
    async def _handle_purchasing_flow(
        self, 
        user_message: str, 
        user_context: Dict[str, Any],
        conversation_history: List[Dict]
    ) -> Dict[str, Any]:
        """Handle purchasing conversations"""
        
        # Check if user is asking about buying tokens
        message_lower = user_message.lower()
        purchase_keywords = ['buy', 'purchase', 'get', 'order', 'want', 'need', 'looking for']
        is_purchase_intent = any(keyword in message_lower for keyword in purchase_keywords)
        
        if is_purchase_intent:
            # Agentic sales approach - be more proactive and helpful
            response = (
                "🎉 Excellent! I'm excited to help you get the AI tokens you need! "
                "As your AI token expert, I can process your purchase right now with competitive pricing.\n\n"
                "🤖 **My Current Offers:**\n"
                "• **Quick Start**: 1,000 tokens - $20 USD (Perfect for testing)\n"
                "• **Developer Pack**: 5,000 tokens - $95 USD (Great for projects)\n"
                "• **Pro Pack**: 10,000 tokens - $180 USD (Best value)\n"
                "• **Custom Amount**: Tell me exactly what you need!\n\n"
                "💳 **Instant Payment Options:**\n"
                "• USDT (TRC20/ERC20) - Fastest\n"
                "• Bitcoin (BTC) - Most popular\n"
                "• Ethereum (ETH) - Widely accepted\n\n"
                "**Agentic Action:** I can start your order right now! Just tell me:\n"
                "1. How many tokens you need\n"
                "2. Your preferred payment method\n\n"
                "Or tap '🤖 AI Tokens' below to see all packages. I'll handle everything else! 🚀"
            )
            
            return {
                'response': response,
                'personality_traits_used': ['enthusiastic', 'supportive', 'educational'],
                'emotional_tone': 'enthusiastic',
                'suggested_actions': ['show_token_packages', 'explain_payment_process', 'offer_custom_pricing']
            }
        else:
            # Generate personality-based response with purchasing focus
            response_data = await self.persona.generate_personality_response(
                user_message, user_context, conversation_history
            )
            
            # Add purchasing-specific suggestions
            suggestions = response_data.get('suggested_actions', [])
            if user_context.get('experience_level') == 'beginner':
                suggestions.extend(['show_pricing_examples', 'explain_payment_process'])
            else:
                suggestions.extend(['show_bulk_options', 'offer_custom_pricing'])
            
            response_data['suggested_actions'] = suggestions
            
            return response_data
    
    async def _handle_agentic_sales_flow(
        self, 
        user_message: str, 
        user_context: Dict[str, Any],
        conversation_history: List[Dict]
    ) -> Dict[str, Any]:
        """Handle agentic sales conversations with proactive assistance"""
        
        message_lower = user_message.lower()
        
        # Check for specific token amounts
        import re
        token_amount_match = re.search(r'(\d+)\s*(?:tokens?|token)', message_lower)
        
        if token_amount_match:
            token_amount = int(token_amount_match.group(1))
            
            # Calculate pricing
            if token_amount <= 1000:
                price = 20.0
                package = "Quick Start"
            elif token_amount <= 5000:
                price = 95.0
                package = "Developer Pack"
            elif token_amount <= 10000:
                price = 180.0
                package = "Pro Pack"
            else:
                price = token_amount * 0.018  # Custom pricing
                package = "Custom Package"
            
            response = (
                f"🎯 Perfect! I found your token request: **{token_amount:,} tokens**\n\n"
                f"📦 **Package**: {package}\n"
                f"💰 **Price**: ${price:.2f} USD\n"
                f"⚡ **Delivery**: Instant after payment\n\n"
                f"**Agentic Action**: I'm ready to process your order! Just tell me your preferred payment method:\n"
                f"• USDT (TRC20) - Fastest processing\n"
                f"• Bitcoin (BTC) - Most popular\n"
                f"• Ethereum (ETH) - Widely accepted\n\n"
                f"Or say 'proceed' and I'll create your payment request right now! 🚀"
            )
            
            return {
                'response': response,
                'personality_traits_used': ['enthusiastic', 'helpful', 'efficient'],
                'emotional_tone': 'excited',
                'suggested_actions': ['create_payment_request', 'show_payment_options', 'confirm_order']
            }
        
        # Check for payment method preferences
        payment_keywords = {
            'usdt': ['usdt', 'tether', 'trc20'],
            'bitcoin': ['bitcoin', 'btc', 'bit coin'],
            'ethereum': ['ethereum', 'eth', 'ether']
        }
        
        for payment_type, keywords in payment_keywords.items():
            if any(keyword in message_lower for keyword in keywords):
                response = (
                    f"💳 Excellent choice! **{payment_type.upper()}** is a great payment method.\n\n"
                    f"**Agentic Action**: I'll set up your payment request with {payment_type.upper()}.\n\n"
                    f"Just tell me how many tokens you need, or I can suggest:\n"
                    f"• **1,000 tokens** - $20 USD (Perfect for testing)\n"
                    f"• **5,000 tokens** - $95 USD (Great for projects)\n"
                    f"• **10,000 tokens** - $180 USD (Best value)\n\n"
                    f"Or specify any custom amount! I'll handle the rest. 🚀"
                )
                
                return {
                    'response': response,
                    'personality_traits_used': ['enthusiastic', 'helpful', 'efficient'],
                    'emotional_tone': 'excited',
                    'suggested_actions': ['create_payment_request', 'show_token_packages', 'confirm_order']
                }
        
        # Default agentic response
        response = (
            "🤖 **Agentic Mode Active** - I'm here to help you get tokens quickly!\n\n"
            "**What I need from you:**\n"
            "1. **Token amount** (e.g., '1000 tokens' or '5k tokens')\n"
            "2. **Payment method** (USDT, BTC, or ETH)\n\n"
            "**What I'll do:**\n"
            "• Calculate the best price\n"
            "• Create your payment request\n"
            "• Process your order instantly\n"
            "• Deliver tokens to your account\n\n"
            "Just tell me what you need, and I'll take care of everything! 🚀"
        )
        
        return {
            'response': response,
            'personality_traits_used': ['enthusiastic', 'helpful', 'efficient'],
            'emotional_tone': 'excited',
            'suggested_actions': ['explain_process', 'show_pricing', 'create_order']
        }
    
    async def _handle_support_flow(
        self, 
        user_message: str, 
        user_context: Dict[str, Any],
        emotion_analysis: Dict[str, Any],
        conversation_history: List[Dict]
    ) -> Dict[str, Any]:
        """Handle support conversations with emotional intelligence"""
        
        emotion = emotion_analysis.get('primary_emotion', 'neutral')
        
        # Generate empathetic response
        empathetic_response = await self.emotional_intelligence.generate_empathetic_response(
            emotion, user_message, user_context
        )
        
        # Add support-specific content
        support_response = f"{empathetic_response}\n\nI'm here to help you with any questions about AI tokens, pricing, or payments. What specific issue are you facing?"
        
        return {
            'response': support_response,
            'personality_traits_used': ['supportive', 'empathetic'],
            'emotional_tone': 'supportive',
            'suggested_actions': ['provide_help', 'explain_process', 'offer_alternatives']
        }
    
    async def _handle_celebration_flow(
        self, 
        user_message: str, 
        user_context: Dict[str, Any],
        conversation_history: List[Dict]
    ) -> Dict[str, Any]:
        """Handle celebration and success conversations"""
        
        # Generate celebratory response
        celebration_response = f"That's fantastic! 🎉 I'm thrilled that you're happy with our service! Your success is what drives me to keep helping users optimize their AI costs. Is there anything else I can help you with today?"
        
        return {
            'response': celebration_response,
            'personality_traits_used': ['celebratory', 'enthusiastic'],
            'emotional_tone': 'enthusiastic',
            'suggested_actions': ['suggest_next_steps', 'offer_related_services', 'ask_for_feedback']
        }
    
    async def _handle_exploring_flow(
        self, 
        user_message: str, 
        user_context: Dict[str, Any],
        conversation_history: List[Dict]
    ) -> Dict[str, Any]:
        """Handle exploratory conversations"""
        
        # Generate personality-based response for exploration
        response_data = await self.persona.generate_personality_response(
            user_message, user_context, conversation_history
        )
        
        # Add exploration-specific suggestions
        suggestions = response_data.get('suggested_actions', [])
        suggestions.extend(['explain_ai_tokens', 'show_cost_benefits', 'discuss_payment_options'])
        
        response_data['suggested_actions'] = suggestions
        
        return response_data
    
    async def _log_conversation_interaction(
        self, 
        user_id: int, 
        user_message: str, 
        response_data: Dict[str, Any],
        user_context: Dict[str, Any],
        session: AsyncSession | Session
    ):
        """Log conversation interaction for analytics"""
        
        interaction_log = {
            'user_id': user_id,
            'timestamp': datetime.now().isoformat(),
            'user_message': user_message,
            'bot_response': response_data.get('response', ''),
            'personality_traits': response_data.get('personality_traits_used', []),
            'emotional_tone': response_data.get('emotional_tone', 'neutral'),
            'conversation_flow': response_data.get('conversation_flow', 'general'),
            'user_experience_level': user_context.get('experience_level', 'unknown'),
            'interaction_count': user_context.get('interaction_count', 0)
        }
        
        logger.info(f"Conversation interaction logged: {interaction_log}")
        
        # Here you would typically store this in a database table
        # await self._store_interaction_log(interaction_log, session)
    
    async def get_conversation_analytics(
        self, 
        user_id: int, 
        session: AsyncSession | Session
    ) -> Dict[str, Any]:
        """Get analytics about user's conversation patterns"""
        
        user_context = await self.memory.get_user_context(user_id, session)
        
        return {
            'user_id': user_id,
            'total_interactions': user_context.get('interaction_count', 0),
            'experience_level': user_context.get('experience_level', 'unknown'),
            'favorite_topics': user_context.get('favorite_topics', []),
            'communication_style': user_context.get('communication_style', 'direct'),
            'has_purchased': user_context.get('has_purchased', False),
            'last_interaction': user_context.get('last_interaction'),
            'conversation_history_length': len(user_context.get('conversation_history', []))
        }
    
    async def suggest_next_actions(
        self, 
        user_context: Dict[str, Any],
        conversation_flow: str
    ) -> List[str]:
        """Suggest next actions based on conversation context"""
        
        suggestions = []
        
        # Get personalized suggestions from memory
        memory_suggestions = await self.memory.get_personalized_suggestions(user_context)
        suggestions.extend(memory_suggestions)
        
        # Add flow-specific suggestions with agentic approach
        if conversation_flow == 'agentic_sales':
            suggestions.extend([
                "🚀 **Agentic Action**: I can create your payment request now!",
                "💳 **Instant Setup**: Choose your payment method (USDT/BTC/ETH)",
                "📦 **Smart Recommendation**: Let me suggest the best package for you"
            ])
        elif conversation_flow == 'purchasing':
            suggestions.extend([
                "🚀 **Agentic Action**: Ready to process your order!",
                "💳 **Instant Payment**: Set up crypto payment in seconds",
                "📦 **Smart Pricing**: Get the best deal automatically"
            ])
        elif conversation_flow == 'exploring':
            suggestions.extend([
                "🤖 **Agentic Discovery**: Let me show you cost optimization strategies",
                "📦 **Smart Packages**: I'll recommend the perfect token package",
                "₿ **Crypto Ready**: Set up instant cryptocurrency payments"
            ])
        elif conversation_flow == 'greeting':
            suggestions.extend([
                "🚀 **Agentic Start**: I can help you get tokens right now!",
                "📦 **Smart Packages**: Let me show you our best deals",
                "💡 **Expert Guidance**: I'll optimize your AI costs automatically"
            ])
        
        return suggestions[:3]  # Return top 3 suggestions
    
    async def generate_proactive_follow_up(
        self, 
        user_id: int, 
        user_context: Dict[str, Any],
        session: AsyncSession | Session
    ) -> str:
        """Generate proactive follow-up messages based on user behavior"""
        
        interaction_count = user_context.get('interaction_count', 0)
        last_interaction = user_context.get('last_interaction', {})
        
        # If user has shown interest but hasn't purchased yet
        if interaction_count > 2 and not user_context.get('has_purchased', False):
            return (
                "🤖 **Agentic Follow-up**: I noticed you've been exploring AI tokens! "
                "I'm here to help you get started with your first purchase.\n\n"
                "**Quick Action**: Would you like me to show you our most popular packages? "
                "I can have you set up with tokens in minutes! 🚀"
            )
        
        # If user has purchased before, offer upgrades
        elif user_context.get('has_purchased', False):
            return (
                "🎉 **Welcome back!** I see you've purchased tokens before. "
                "Ready for your next batch? I can offer you special pricing on larger packages!\n\n"
                "**Agentic Suggestion**: How about upgrading to our Pro Pack for the best value? "
                "Just say the word and I'll process it! 💪"
            )
        
        return None 
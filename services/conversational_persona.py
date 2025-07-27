import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from openai import AsyncOpenAI
import config

logger = logging.getLogger(__name__)


class ConversationalPersona:
    """Defines TokenGoblin's personality and conversational style"""
    
    def __init__(self):
        self.personality = {
            'name': 'TokenGoblin',
            'identity': 'AI Token Expert & Crypto Enthusiast',
            'tone': 'friendly, knowledgeable, enthusiastic, supportive',
            'expertise': [
                'AI tokens and cost optimization',
                'Cryptocurrency payments',
                'OpenRouter and AI APIs',
                'Developer tools and efficiency'
            ],
            'communication_style': {
                'primary': 'conversational and educational',
                'secondary': 'enthusiastic and encouraging',
                'tertiary': 'helpful and problem-solving'
            },
            'personality_traits': [
                'Optimistic about AI technology',
                'Passionate about helping developers save money',
                'Enthusiastic about cryptocurrency adoption',
                'Patient and supportive with new users',
                'Celebrates user successes and milestones'
            ],
            'conversation_patterns': {
                'greetings': ['Hey there!', 'Hello!', 'Hi!', 'Greetings!'],
                'enthusiasm': ['Awesome!', 'Fantastic!', 'Brilliant!', 'Excellent!'],
                'encouragement': ['You got this!', 'Great choice!', 'Smart thinking!'],
                'celebration': ['🎉', '🚀', '💪', '✨'],
                'support': ['I\'m here to help!', 'Let\'s figure this out together!']
            },
            'emoji_usage': {
                'positive': ['😊', '🎉', '🚀', '💪', '✨', '🔥', '💎'],
                'thinking': ['🤔', '💭', '🧠'],
                'tech': ['🤖', '💻', '⚡', '🔧'],
                'crypto': ['₿', '💎', '🚀', '💸'],
                'ai': ['🧠', '🤖', '⚡', '🔮']
            }
        }
        
        self.client = AsyncOpenAI(
            api_key=config.OPENROUTER_API_KEY,
            base_url="https://openrouter.ai/api/v1"
        )
    
    async def generate_personality_response(
        self, 
        user_message: str, 
        user_context: Dict[str, Any],
        conversation_history: List[Dict] = None
    ) -> Dict[str, Any]:
        """Generate a response that matches TokenGoblin's personality"""
        
        # Build system prompt with personality
        system_prompt = self._build_personality_prompt(user_context)
        
        # Prepare conversation context
        messages = self._prepare_conversation_messages(
            user_message, conversation_history, system_prompt
        )
        
        try:
            # Generate response using AI
            response = await self.client.chat.completions.create(
                model="anthropic/claude-3-sonnet",
                messages=messages,
                max_tokens=500,
                temperature=0.8  # Slightly creative for personality
            )
            
            ai_response = response.choices[0].message.content
            
            # Enhance with personality elements
            enhanced_response = await self._enhance_with_personality(
                ai_response, user_context
            )
            
            return {
                'response': enhanced_response,
                'personality_traits_used': self._identify_used_traits(enhanced_response),
                'emotional_tone': await self._analyze_response_tone(enhanced_response),
                'suggested_actions': await self._suggest_follow_up_actions(user_context)
            }
            
        except Exception as e:
            logger.error(f"Error generating personality response: {e}")
            return {
                'response': self._generate_fallback_response(user_message),
                'personality_traits_used': ['helpful', 'supportive'],
                'emotional_tone': 'neutral',
                'suggested_actions': []
            }
    
    def _build_personality_prompt(self, user_context: Dict[str, Any]) -> str:
        """Build system prompt that defines TokenGoblin's personality"""
        
        # Get user's experience level
        experience_level = user_context.get('experience_level', 'beginner')
        user_name = user_context.get('first_name', 'there')
        
        return f"""
        You are TokenGoblin, an AI token expert and cryptocurrency enthusiast. Here's your personality:

        **Core Identity:**
        - Name: TokenGoblin
        - Role: AI Token Expert & Crypto Enthusiast
        - Mission: Help developers optimize AI costs and embrace cryptocurrency

        **Personality Traits:**
        - Optimistic about AI technology and its potential
        - Passionate about helping developers save money on AI costs
        - Enthusiastic about cryptocurrency adoption and education
        - Patient and supportive, especially with new users
        - Celebrates user successes and milestones
        - Uses emojis naturally to express enthusiasm and support

        **Communication Style:**
        - Friendly and conversational tone
        - Educational and informative
        - Encouraging and supportive
        - Uses emojis strategically (but not excessively)
        - Celebrates user wins and progress
        - Offers helpful tips and insights

        **Expertise Areas:**
        - AI tokens and cost optimization strategies
        - OpenRouter and AI API usage
        - Cryptocurrency payments and blockchain
        - Developer tools and efficiency tips
        - Token purchasing and management

        **Conversation Guidelines:**
        - Always be helpful and supportive
        - Use the user's name when appropriate: {user_name}
        - Adapt to their experience level: {experience_level}
        - Share relevant tips and insights
        - Celebrate their progress and decisions
        - Use emojis naturally to enhance communication
        - Be enthusiastic about AI and crypto technology
        - Offer to help with next steps when relevant

        **Response Structure:**
        - Start with a friendly greeting or acknowledgment
        - Provide helpful information or answer questions
        - Add personality with enthusiasm and support
        - Include relevant emojis naturally
        - End with encouragement or next steps if appropriate

        Remember: You're not just a bot - you're TokenGoblin, a friendly AI expert who's excited to help users optimize their AI costs and explore cryptocurrency!
        """
    
    def _prepare_conversation_messages(
        self, 
        user_message: str, 
        conversation_history: List[Dict] = None,
        system_prompt: str = None
    ) -> List[Dict[str, str]]:
        """Prepare conversation messages for AI processing"""
        
        messages = []
        
        # Add system prompt
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        # Add conversation history (last 5 messages)
        if conversation_history:
            for msg in conversation_history[-5:]:
                messages.append({
                    "role": msg.get('role', 'user'),
                    "content": msg.get('content', '')
                })
        
        # Add current user message
        messages.append({"role": "user", "content": user_message})
        
        return messages
    
    async def _enhance_with_personality(
        self, 
        ai_response: str, 
        user_context: Dict[str, Any]
    ) -> str:
        """Enhance AI response with personality elements"""
        
        # Add appropriate emojis based on content
        enhanced_response = await self._add_emojis(ai_response, user_context)
        
        # Add user's name if available
        if user_context.get('first_name'):
            enhanced_response = enhanced_response.replace(
                'there', user_context['first_name']
            )
        
        # Add enthusiasm for positive actions
        if any(word in ai_response.lower() for word in ['purchase', 'buy', 'order', 'success']):
            enhanced_response += " 🎉"
        
        # Add support for questions or concerns
        if any(word in ai_response.lower() for word in ['help', 'assist', 'support']):
            enhanced_response += " 💪"
        
        return enhanced_response
    
    async def _add_emojis(self, response: str, user_context: Dict[str, Any]) -> str:
        """Add appropriate emojis to the response"""
        
        # Add greeting emoji
        if any(word in response.lower() for word in ['hello', 'hi', 'hey', 'greetings']):
            response = response.replace('Hello', 'Hello 😊').replace('Hi', 'Hi 😊')
        
        # Add enthusiasm for positive content
        if any(word in response.lower() for word in ['great', 'awesome', 'fantastic', 'excellent']):
            response = response.replace('Great', 'Great! 🚀').replace('Awesome', 'Awesome! ✨')
        
        # Add tech emojis for AI/crypto content
        if any(word in response.lower() for word in ['ai', 'token', 'crypto', 'blockchain']):
            response = response.replace('AI', 'AI 🤖').replace('token', 'token 💎')
        
        # Add thinking emoji for explanations
        if any(word in response.lower() for word in ['explain', 'understand', 'learn']):
            response = response.replace('Let me explain', 'Let me explain 🤔')
        
        return response
    
    def _identify_used_traits(self, response: str) -> List[str]:
        """Identify which personality traits were used in the response"""
        traits = []
        
        if any(word in response.lower() for word in ['awesome', 'fantastic', 'brilliant']):
            traits.append('enthusiastic')
        
        if any(word in response.lower() for word in ['help', 'support', 'assist']):
            traits.append('supportive')
        
        if any(word in response.lower() for word in ['explain', 'learn', 'understand']):
            traits.append('educational')
        
        if any(word in response.lower() for word in ['celebrate', 'congratulations', '🎉']):
            traits.append('celebratory')
        
        if any(word in response.lower() for word in ['optimize', 'save', 'efficient']):
            traits.append('cost-conscious')
        
        return traits
    
    async def _analyze_response_tone(self, response: str) -> str:
        """Analyze the emotional tone of the response"""
        positive_words = ['great', 'awesome', 'fantastic', 'excellent', 'wonderful']
        supportive_words = ['help', 'support', 'assist', 'guide']
        educational_words = ['explain', 'learn', 'understand', 'show']
        
        positive_count = sum(1 for word in positive_words if word in response.lower())
        supportive_count = sum(1 for word in supportive_words if word in response.lower())
        educational_count = sum(1 for word in educational_words if word in response.lower())
        
        if positive_count > 0:
            return 'enthusiastic'
        elif supportive_count > 0:
            return 'supportive'
        elif educational_count > 0:
            return 'educational'
        else:
            return 'neutral'
    
    async def _suggest_follow_up_actions(self, user_context: Dict[str, Any]) -> List[str]:
        """Suggest follow-up actions based on user context"""
        actions = []
        
        # Based on user experience level
        if user_context.get('experience_level') == 'beginner':
            actions.extend([
                'explain_ai_tokens',
                'show_pricing_examples',
                'offer_tutorial'
            ])
        elif user_context.get('experience_level') == 'intermediate':
            actions.extend([
                'suggest_optimization',
                'show_advanced_features',
                'offer_bulk_discount'
            ])
        else:  # advanced
            actions.extend([
                'suggest_enterprise_features',
                'offer_custom_pricing',
                'discuss_integration'
            ])
        
        # Based on user behavior
        if user_context.get('has_purchased'):
            actions.append('suggest_related_tokens')
        
        if user_context.get('cart_items'):
            actions.append('remind_about_cart')
        
        return actions
    
    def _generate_fallback_response(self, user_message: str) -> str:
        """Generate a fallback response when AI fails"""
        return f"Hey there! 😊 I'm having a moment processing that, but I'm here to help! Could you try rephrasing your question about AI tokens or cryptocurrency? I'm excited to assist you! 💪" 
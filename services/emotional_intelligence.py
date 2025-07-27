import asyncio
import logging
from typing import Dict, List, Any, Optional
from openai import AsyncOpenAI
import config

logger = logging.getLogger(__name__)


class EmotionalIntelligence:
    """Analyzes user emotions and generates empathetic responses"""
    
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=config.OPENROUTER_API_KEY,
            base_url="https://openrouter.ai/api/v1"
        )
        
        # Emotion categories and their triggers
        self.emotion_triggers = {
            'frustration': [
                'frustrated', 'annoyed', 'angry', 'mad', 'upset', 'disappointed',
                'not working', 'broken', 'error', 'problem', 'issue', 'difficult'
            ],
            'confusion': [
                'confused', 'don\'t understand', 'unclear', 'complicated', 'complex',
                'not sure', 'what do you mean', 'explain', 'help me understand'
            ],
            'excitement': [
                'excited', 'awesome', 'amazing', 'fantastic', 'great', 'love it',
                'perfect', 'brilliant', 'wonderful', 'excellent', 'super'
            ],
            'anxiety': [
                'worried', 'concerned', 'anxious', 'nervous', 'scared', 'afraid',
                'not sure', 'maybe', 'think', 'hope', 'wish'
            ],
            'satisfaction': [
                'happy', 'satisfied', 'pleased', 'content', 'good', 'nice',
                'works', 'solved', 'fixed', 'resolved', 'completed'
            ]
        }
        
        # Empathetic response templates
        self.empathetic_responses = {
            'frustration': [
                "I understand this can be frustrating 😔 Let me help you resolve this!",
                "I can see why you'd be frustrated with that. Let's work together to fix it! 💪",
                "That sounds really annoying! I'm here to help make this easier for you 😊"
            ],
            'confusion': [
                "I totally get why that might be confusing! Let me break it down for you 🤔",
                "No worries at all! This can be tricky to understand. Let me explain it simply 😊",
                "I understand the confusion! Let me walk you through this step by step 💡"
            ],
            'excitement': [
                "I'm so excited that you're excited! 🎉 This is going to be amazing!",
                "Your enthusiasm is contagious! I love seeing users get excited about this! ✨",
                "That's fantastic! I'm thrilled you're happy with this! 🚀"
            ],
            'anxiety': [
                "I understand your concern, and I want to reassure you that everything will be okay 😊",
                "It's totally normal to feel a bit anxious about this. I'm here to support you! 💪",
                "I can sense your worry, and I want you to know I'm here to help make this easier 😌"
            ],
            'satisfaction': [
                "I'm so glad you're happy with this! Your satisfaction means everything to me! 😊",
                "That's wonderful to hear! I love when things work out perfectly! ✨",
                "I'm thrilled that you're satisfied! This is exactly what I love to hear! 🎉"
            ]
        }
    
    async def analyze_emotion(self, user_message: str, user_context: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the emotional state of the user"""
        
        try:
            # Use AI to analyze emotion more accurately
            emotion_analysis = await self._ai_analyze_emotion(user_message, user_context)
            
            # Combine with keyword-based analysis
            keyword_emotion = self._keyword_based_emotion_analysis(user_message)
            
            # Merge results
            final_emotion = self._merge_emotion_analysis(emotion_analysis, keyword_emotion)
            
            return final_emotion
            
        except Exception as e:
            logger.error(f"Error analyzing emotion: {e}")
            # Fallback to keyword-based analysis
            return self._keyword_based_emotion_analysis(user_message)
    
    async def generate_empathetic_response(
        self, 
        emotion: str, 
        user_message: str, 
        user_context: Dict[str, Any]
    ) -> str:
        """Generate an empathetic response based on detected emotion"""
        
        try:
            # Use AI to generate personalized empathetic response
            ai_response = await self._ai_generate_empathetic_response(
                emotion, user_message, user_context
            )
            
            # Enhance with personality elements
            enhanced_response = await self._enhance_empathetic_response(
                ai_response, emotion, user_context
            )
            
            return enhanced_response
            
        except Exception as e:
            logger.error(f"Error generating empathetic response: {e}")
            # Fallback to template-based response
            return self._get_empathetic_template(emotion, user_context)
    
    async def _ai_analyze_emotion(
        self, 
        user_message: str, 
        user_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Use AI to analyze user emotion"""
        
        prompt = f"""
        Analyze the emotional state of this user message:
        
        Message: "{user_message}"
        User Context: {user_context.get('experience_level', 'unknown')} level user
        
        Provide analysis in JSON format:
        {{
            "primary_emotion": "emotion_name",
            "emotion_intensity": "low/medium/high",
            "confidence": 0.0-1.0,
            "emotional_triggers": ["list", "of", "triggers"],
            "suggested_response_tone": "tone_description",
            "user_needs": ["list", "of", "perceived", "needs"]
        }}
        
        Emotion categories: frustration, confusion, excitement, anxiety, satisfaction, neutral
        """
        
        response = await self.client.chat.completions.create(
            model="anthropic/claude-3-sonnet",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
            temperature=0.3
        )
        
        # Parse JSON response
        import json
        try:
            return json.loads(response.choices[0].message.content)
        except:
            return {
                'primary_emotion': 'neutral',
                'emotion_intensity': 'low',
                'confidence': 0.5,
                'emotional_triggers': [],
                'suggested_response_tone': 'neutral',
                'user_needs': []
            }
    
    def _keyword_based_emotion_analysis(self, user_message: str) -> Dict[str, Any]:
        """Analyze emotion based on keywords"""
        
        message_lower = user_message.lower()
        
        # Count emotion triggers
        emotion_counts = {}
        for emotion, triggers in self.emotion_triggers.items():
            count = sum(1 for trigger in triggers if trigger in message_lower)
            if count > 0:
                emotion_counts[emotion] = count
        
        # Determine primary emotion
        if emotion_counts:
            primary_emotion = max(emotion_counts, key=emotion_counts.get)
            intensity = 'high' if emotion_counts[primary_emotion] > 2 else 'medium'
        else:
            primary_emotion = 'neutral'
            intensity = 'low'
        
        return {
            'primary_emotion': primary_emotion,
            'emotion_intensity': intensity,
            'confidence': 0.7 if emotion_counts else 0.3,
            'emotional_triggers': list(emotion_counts.keys()),
            'suggested_response_tone': self._get_suggested_tone(primary_emotion),
            'user_needs': self._infer_user_needs(primary_emotion, message_lower)
        }
    
    def _merge_emotion_analysis(
        self, 
        ai_analysis: Dict[str, Any], 
        keyword_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Merge AI and keyword-based emotion analysis"""
        
        # Prefer AI analysis if confidence is high
        if ai_analysis.get('confidence', 0) > 0.7:
            return ai_analysis
        
        # Otherwise, combine both analyses
        merged = {
            'primary_emotion': ai_analysis.get('primary_emotion', keyword_analysis.get('primary_emotion')),
            'emotion_intensity': ai_analysis.get('emotion_intensity', keyword_analysis.get('emotion_intensity')),
            'confidence': max(ai_analysis.get('confidence', 0), keyword_analysis.get('confidence', 0)),
            'emotional_triggers': list(set(
                ai_analysis.get('emotional_triggers', []) + 
                keyword_analysis.get('emotional_triggers', [])
            )),
            'suggested_response_tone': ai_analysis.get('suggested_response_tone', keyword_analysis.get('suggested_response_tone')),
            'user_needs': list(set(
                ai_analysis.get('user_needs', []) + 
                keyword_analysis.get('user_needs', [])
            ))
        }
        
        return merged
    
    async def _ai_generate_empathetic_response(
        self, 
        emotion: str, 
        user_message: str, 
        user_context: Dict[str, Any]
    ) -> str:
        """Use AI to generate personalized empathetic response"""
        
        prompt = f"""
        Generate an empathetic response for a user who is feeling {emotion}.
        
        User Message: "{user_message}"
        User Context: {user_context.get('experience_level', 'unknown')} level user
        Detected Emotion: {emotion}
        
        Guidelines:
        - Be empathetic and understanding
        - Acknowledge their emotion
        - Offer support and help
        - Use TokenGoblin's friendly personality
        - Include appropriate emojis
        - Keep it conversational and warm
        - Focus on being helpful and supportive
        
        Generate a response that shows you understand their emotion and want to help.
        """
        
        response = await self.client.chat.completions.create(
            model="anthropic/claude-3-sonnet",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=200,
            temperature=0.8
        )
        
        return response.choices[0].message.content
    
    async def _enhance_empathetic_response(
        self, 
        response: str, 
        emotion: str, 
        user_context: Dict[str, Any]
    ) -> str:
        """Enhance empathetic response with personality elements"""
        
        # Add user's name if available
        if user_context.get('first_name'):
            response = response.replace('there', user_context['first_name'])
        
        # Add emotion-specific emojis
        emotion_emojis = {
            'frustration': '😔',
            'confusion': '🤔',
            'excitement': '🎉',
            'anxiety': '😌',
            'satisfaction': '😊',
            'neutral': '😊'
        }
        
        if emotion in emotion_emojis and emotion_emojis[emotion] not in response:
            response += f" {emotion_emojis[emotion]}"
        
        return response
    
    def _get_empathetic_template(self, emotion: str, user_context: Dict[str, Any]) -> str:
        """Get template-based empathetic response"""
        
        if emotion in self.empathetic_responses:
            import random
            template = random.choice(self.empathetic_responses[emotion])
            
            # Personalize with user's name
            if user_context.get('first_name'):
                template = template.replace('you', f"you, {user_context['first_name']}")
            
            return template
        else:
            return "I'm here to help you! 😊"
    
    def _get_suggested_tone(self, emotion: str) -> str:
        """Get suggested response tone based on emotion"""
        
        tone_mapping = {
            'frustration': 'supportive and helpful',
            'confusion': 'explanatory and patient',
            'excitement': 'enthusiastic and celebratory',
            'anxiety': 'reassuring and calming',
            'satisfaction': 'congratulatory and encouraging',
            'neutral': 'friendly and informative'
        }
        
        return tone_mapping.get(emotion, 'friendly')
    
    def _infer_user_needs(self, emotion: str, message: str) -> List[str]:
        """Infer user needs based on emotion and message"""
        
        needs_mapping = {
            'frustration': ['help', 'solution', 'support'],
            'confusion': ['explanation', 'clarity', 'guidance'],
            'excitement': ['celebration', 'encouragement', 'next_steps'],
            'anxiety': ['reassurance', 'support', 'guidance'],
            'satisfaction': ['acknowledgment', 'encouragement', 'next_opportunities'],
            'neutral': ['information', 'guidance', 'options']
        }
        
        return needs_mapping.get(emotion, ['support']) 
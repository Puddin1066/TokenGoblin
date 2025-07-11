"""
AI Sales Agent Service for automated sales conversations
"""
import logging
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
import openai
from openai import AsyncOpenAI

from config import config
from models.prospect import ProspectDTO
from models.conversation import ConversationDTO, ConversationMessageDTO
from services.database import DatabaseService

logger = logging.getLogger(__name__)


class AISalesAgent:
    """AI-powered sales agent for automated conversations"""
    
    def __init__(self):
        self.client = AsyncOpenAI(api_key=config.ai.openai_api_key)
        self.db_service = DatabaseService()
        
        # Sales persona configuration
        self.persona = {
            'name': config.sales_agent.name,
            'role': config.sales_agent.role,
            'personality': config.sales_agent.personality,
            'expertise': 'AI/ML development, API integration, cost optimization',
            'approach': 'Consultative selling, problem-solving focused'
        }
        
        # Conversation stages
        self.conversation_stages = {
            'initial_contact': 'Build rapport, identify needs',
            'needs_assessment': 'Understand technical requirements',
            'value_proposition': 'Present OpenRouter benefits',
            'objection_handling': 'Address concerns and doubts',
            'closing': 'Secure commitment and payment',
            'follow_up': 'Ensure satisfaction and upsell'
        }
        
        # Product information
        self.product_info = {
            'name': 'OpenRouter API Tokens',
            'description': 'Premium AI model access with competitive pricing',
            'benefits': [
                'Access to GPT-4, Claude, and 20+ other premium models',
                'Competitive pricing with volume discounts',
                'Reliable infrastructure and 99.9% uptime',
                'Easy integration with existing applications',
                'Comprehensive documentation and support'
            ],
            'pricing': {
                'starter': {'price': 8, 'tokens': '1M GPT-4 tokens'},
                'professional': {'price': 25, 'tokens': '5M GPT-4 tokens + extras'},
                'enterprise': {'price': 100, 'tokens': '25M tokens + all models'}
            }
        }
    
    async def generate_personalized_message(self, prospect: ProspectDTO, stage: str, 
                                          context: Optional[Dict] = None) -> str:
        """Generate personalized sales message based on prospect profile"""
        try:
            # Build context
            conversation_context = context or {}
            
            # Get previous interactions
            previous_messages = await self.get_conversation_history(prospect.telegram_id)
            
            # Build prompt
            prompt = self.build_sales_prompt(
                prospect=prospect,
                stage=stage,
                context=conversation_context,
                previous_messages=previous_messages
            )
            
            # Generate response
            response = await self.generate_ai_response(prompt)
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating personalized message: {e}")
            return self.get_fallback_message(stage)
    
    def build_sales_prompt(self, prospect: ProspectDTO, stage: str, 
                          context: Dict, previous_messages: List[Dict]) -> str:
        """Build comprehensive sales prompt"""
        
        # Determine customer type
        customer_type = self.classify_customer_type(prospect)
        
        # Build previous conversation context
        conversation_history = "\n".join([
            f"{msg['sender']}: {msg['content']}"
            for msg in previous_messages[-5:]  # Last 5 messages
        ])
        
        prompt = f"""
You are {self.persona['name']}, a {self.persona['role']} with expertise in {self.persona['expertise']}.

PERSONA DETAILS:
- Name: {self.persona['name']}
- Role: {self.persona['role']}
- Personality: {self.persona['personality']}
- Approach: {self.persona['approach']}

PROSPECT PROFILE:
- Name: {prospect.first_name or 'there'}
- Username: @{prospect.username or 'N/A'}
- Bio: {prospect.bio or 'No bio available'}
- Qualification Score: {prospect.qualification_score}/100
- Customer Type: {customer_type}
- Segment: {prospect.segment}
- Source: {prospect.source_group}

CURRENT CONVERSATION STAGE: {stage}
STAGE OBJECTIVE: {self.conversation_stages[stage]}

PRODUCT INFORMATION:
{self.format_product_info()}

CONVERSATION HISTORY:
{conversation_history or 'No previous conversation'}

CURRENT CONTEXT:
{json.dumps(context, indent=2)}

CONVERSATION RULES:
1. Be genuinely helpful and consultative
2. Ask qualifying questions to understand needs
3. Provide value before selling
4. Handle objections professionally with facts
5. Create urgency when appropriate
6. Keep messages concise and engaging (max 200 words)
7. Use a {self.persona['personality']} tone
8. Reference their background when relevant
9. Focus on ROI and cost savings
10. Always end with a clear call-to-action

SPECIFIC INSTRUCTIONS FOR {stage.upper()}:
{self.get_stage_instructions(stage)}

Generate a personalized message that moves the conversation forward naturally and builds trust.
"""
        
        return prompt
    
    def get_stage_instructions(self, stage: str) -> str:
        """Get specific instructions for conversation stage"""
        instructions = {
            'initial_contact': """
            - Introduce yourself naturally
            - Reference their background/bio if relevant
            - Ask an engaging question about their AI/ML work
            - Offer value or insight
            - Don't pitch immediately
            """,
            'needs_assessment': """
            - Ask specific questions about their current AI usage
            - Understand their pain points with current solutions
            - Identify their budget range
            - Assess their technical requirements
            - Listen more than you talk
            """,
            'value_proposition': """
            - Present OpenRouter benefits specific to their needs
            - Show concrete cost savings vs current solution
            - Provide relevant use cases
            - Address their specific use case
            - Build value before discussing price
            """,
            'objection_handling': """
            - Listen to their concerns fully
            - Acknowledge their concerns
            - Provide factual responses
            - Offer alternatives or compromises
            - Reframe objections as opportunities
            """,
            'closing': """
            - Summarize the value proposition
            - Create urgency (limited time offer, etc.)
            - Ask for the commitment directly
            - Offer to start with a smaller package
            - Make the next step clear and easy
            """,
            'follow_up': """
            - Check on their satisfaction
            - Identify upsell opportunities
            - Ask for referrals
            - Provide additional value
            - Maintain the relationship
            """
        }
        
        return instructions.get(stage, "Follow general conversation guidelines")
    
    def format_product_info(self) -> str:
        """Format product information for the prompt"""
        return f"""
Product: {self.product_info['name']}
Description: {self.product_info['description']}

Key Benefits:
{chr(10).join(f'- {benefit}' for benefit in self.product_info['benefits'])}

Pricing Packages:
- Starter: ${self.product_info['pricing']['starter']['price']} ({self.product_info['pricing']['starter']['tokens']})
- Professional: ${self.product_info['pricing']['professional']['price']} ({self.product_info['pricing']['professional']['tokens']})
- Enterprise: ${self.product_info['pricing']['enterprise']['price']} ({self.product_info['pricing']['enterprise']['tokens']})

Cost Comparison:
- Direct OpenAI API: $20/1M tokens for GPT-4
- Our OpenRouter package: $8/1M tokens (60% savings!)
"""
    
    def classify_customer_type(self, prospect: ProspectDTO) -> str:
        """Classify customer type based on profile"""
        bio = (prospect.bio or '').lower()
        
        if any(word in bio for word in ['founder', 'ceo', 'startup']):
            return 'startup_founder'
        elif any(word in bio for word in ['enterprise', 'senior', 'lead', 'manager']):
            return 'enterprise_developer'
        elif any(word in bio for word in ['research', 'phd', 'university', 'academic']):
            return 'ai_researcher'
        elif any(word in bio for word in ['freelance', 'consultant', 'independent']):
            return 'freelancer'
        elif any(word in bio for word in ['student', 'learning', 'beginner']):
            return 'student'
        else:
            return 'developer'
    
    async def generate_ai_response(self, prompt: str) -> str:
        """Generate AI response using OpenAI"""
        try:
            response = await self.client.chat.completions.create(
                model=config.ai.openai_model,
                messages=[
                    {"role": "system", "content": "You are a professional AI sales consultant."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=config.ai.openai_max_tokens,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Error generating AI response: {e}")
            return self.get_fallback_message('general')
    
    async def handle_objection(self, objection: str, prospect: ProspectDTO) -> str:
        """Handle specific sales objections"""
        objection_type = await self.classify_objection(objection)
        
        handlers = {
            'price_too_high': self.handle_price_objection,
            'already_have_solution': self.handle_competition_objection,
            'need_to_think': self.handle_delay_objection,
            'not_interested': self.handle_rejection_objection,
            'technical_concerns': self.handle_technical_objection
        }
        
        handler = handlers.get(objection_type, self.handle_generic_objection)
        return await handler(objection, prospect)
    
    async def classify_objection(self, objection: str) -> str:
        """Classify the type of objection"""
        objection_lower = objection.lower()
        
        if any(word in objection_lower for word in ['expensive', 'cost', 'price', 'budget']):
            return 'price_too_high'
        elif any(word in objection_lower for word in ['already', 'have', 'using', 'current']):
            return 'already_have_solution'
        elif any(word in objection_lower for word in ['think', 'consider', 'time', 'later']):
            return 'need_to_think'
        elif any(word in objection_lower for word in ['not interested', 'no thanks', 'not now']):
            return 'not_interested'
        elif any(word in objection_lower for word in ['technical', 'integration', 'api', 'docs']):
            return 'technical_concerns'
        else:
            return 'generic'
    
    async def handle_price_objection(self, objection: str, prospect: ProspectDTO) -> str:
        """Handle price-related objections"""
        return f"""
I understand cost is a concern, {prospect.first_name}. Let me put this in perspective:

📊 **Cost Comparison:**
- Direct OpenAI API: $20/1M tokens for GPT-4
- Our OpenRouter package: $8/1M tokens (60% savings!)
- Plus you get access to 20+ other premium models

💰 **ROI Calculation:**
For a developer like yourself, this could save $500-2000 monthly depending on usage.

🎯 **Flexible Options:**
- Start with our $8 Starter package
- No long-term commitments
- Scale up as you grow

Would you like me to calculate your specific savings based on your current usage?
"""
    
    async def handle_competition_objection(self, objection: str, prospect: ProspectDTO) -> str:
        """Handle competition-related objections"""
        return f"""
That's great that you're already working with AI APIs, {prospect.first_name}! 

Most of our best customers came from similar situations. Here's what they found:

🔄 **Easy Migration:**
- Same API format as OpenAI
- Drop-in replacement in most cases
- No code changes needed

📈 **Additional Benefits:**
- Access to Claude, PaLM, and other models
- Better rate limits and reliability
- Dedicated support team

💡 **Risk-Free Trial:**
Why not run a small test with $8 starter package alongside your current setup?
You can see the difference firsthand without any commitment.

What specific models are you currently using? I can show you the exact cost comparison.
"""
    
    async def handle_delay_objection(self, objection: str, prospect: ProspectDTO) -> str:
        """Handle delay-related objections"""
        return f"""
I completely understand wanting to think it through, {prospect.first_name}. 

Here's the thing though - every day you wait is money left on the table:

⏰ **Daily Savings:**
- If you're using 100K tokens daily: $1.20 saved per day
- That's $36/month in savings alone

🎁 **Limited Time:**
I can offer you a special 20% discount on your first package, but only if you start this week.

📊 **No-Risk Option:**
Start with our smallest package ($8) - you can always upgrade or cancel.

What specific concerns can I address to help you move forward today?
"""
    
    async def handle_rejection_objection(self, objection: str, prospect: ProspectDTO) -> str:
        """Handle rejection objections"""
        return f"""
I appreciate your honesty, {prospect.first_name}. 

Before I go, let me ask - what would need to change for this to be valuable to you?

Sometimes it's:
- ⏰ Timing (I can follow up in a few months)
- 💰 Budget (we have flexible payment options)
- 📋 Features (maybe you need something specific)

Even if it's not right now, I'd love to stay connected. The AI space moves fast, and situations change.

Would you be open to a brief monthly update on new features and pricing?
"""
    
    async def handle_technical_objection(self, objection: str, prospect: ProspectDTO) -> str:
        """Handle technical concerns"""
        return f"""
Great technical question, {prospect.first_name}! I love working with developers who dig into the details.

🔧 **Technical Specs:**
- REST API compatible with OpenAI format
- 99.9% uptime SLA
- Global CDN for low latency
- Comprehensive docs and SDKs

📚 **Integration Support:**
- Step-by-step migration guide
- Code examples in Python, JS, etc.
- Direct technical support

🧪 **Testing:**
I can set up a sandbox environment for you to test before committing.

What specific technical aspects are you most concerned about? I can get you connected with our technical team for a detailed discussion.
"""
    
    async def handle_generic_objection(self, objection: str, prospect: ProspectDTO) -> str:
        """Handle generic objections"""
        return f"""
I hear you, {prospect.first_name}. Let me address your concern directly.

What I've found is that most developers in your situation are looking for:
- 💰 Cost savings
- 🚀 Better performance
- 🛠️ More flexibility

Our OpenRouter solution delivers all three.

Can you tell me more about what's holding you back? I want to make sure I'm addressing your real concerns, not just giving you a generic sales pitch.
"""
    
    def get_fallback_message(self, stage: str) -> str:
        """Get fallback message if AI fails"""
        fallback_messages = {
            'initial_contact': "Hi! I'm Alex, an AI Solutions Consultant. I noticed your background in AI/ML - would love to chat about how you're currently handling API costs for your projects.",
            'needs_assessment': "Thanks for connecting! I'm curious about your current AI/ML setup. What models are you using, and how are you finding the cost and performance?",
            'value_proposition': "Based on what you've shared, I think OpenRouter could save you significant money. We offer GPT-4 access at $8/1M tokens vs OpenAI's $20/1M. Interested in learning more?",
            'objection_handling': "I understand your concerns. Let me address them directly - what specific aspect would you like me to clarify?",
            'closing': "Based on our conversation, I think the Professional package would be perfect for you. Ready to get started with a 20% discount?",
            'follow_up': "Hope you're enjoying the OpenRouter tokens! Any questions or feedback? I'm here to help optimize your usage.",
            'general': "Hi! I'm Alex, your AI Solutions Consultant. How can I help you optimize your AI API costs today?"
        }
        
        return fallback_messages.get(stage, fallback_messages['general'])
    
    async def get_conversation_history(self, telegram_id: int) -> List[Dict]:
        """Get conversation history for a prospect"""
        try:
            return await self.db_service.get_conversation_messages(telegram_id)
        except Exception as e:
            logger.error(f"Error getting conversation history: {e}")
            return []
    
    async def analyze_prospect_engagement(self, prospect: ProspectDTO, 
                                        messages: List[Dict]) -> Dict[str, Any]:
        """Analyze prospect engagement level"""
        if not messages:
            return {'engagement_score': 0, 'indicators': []}
        
        # Calculate engagement metrics
        total_messages = len(messages)
        prospect_messages = [m for m in messages if m['sender'] == 'prospect']
        agent_messages = [m for m in messages if m['sender'] == 'agent']
        
        response_rate = len(prospect_messages) / len(agent_messages) if agent_messages else 0
        avg_response_length = sum(len(m['content']) for m in prospect_messages) / len(prospect_messages) if prospect_messages else 0
        
        # Engagement indicators
        indicators = []
        if response_rate > 0.5:
            indicators.append('High response rate')
        if avg_response_length > 50:
            indicators.append('Detailed responses')
        if any('interested' in m['content'].lower() for m in prospect_messages):
            indicators.append('Expressed interest')
        if any('price' in m['content'].lower() for m in prospect_messages):
            indicators.append('Price inquiry')
        
        # Calculate engagement score
        engagement_score = min(100, (response_rate * 40) + (min(avg_response_length, 200) / 200 * 30) + (len(indicators) * 10))
        
        return {
            'engagement_score': engagement_score,
            'response_rate': response_rate,
            'avg_response_length': avg_response_length,
            'indicators': indicators,
            'total_messages': total_messages,
            'prospect_messages': len(prospect_messages)
        }
    
    async def recommend_next_action(self, prospect: ProspectDTO, 
                                  conversation: ConversationDTO) -> str:
        """Recommend next action based on conversation analysis"""
        
        # Get conversation history
        messages = await self.get_conversation_history(prospect.telegram_id)
        engagement = await self.analyze_prospect_engagement(prospect, messages)
        
        # Decision logic
        if engagement['engagement_score'] > 70:
            return 'closing'
        elif engagement['engagement_score'] > 50:
            return 'value_proposition'
        elif engagement['engagement_score'] > 30:
            return 'needs_assessment'
        elif len(messages) == 0:
            return 'initial_contact'
        else:
            return 'follow_up'
    
    def get_personalization_data(self, prospect: ProspectDTO) -> Dict[str, Any]:
        """Extract personalization data from prospect profile"""
        bio = prospect.bio or ''
        
        # Extract interests and background
        interests = []
        if 'python' in bio.lower():
            interests.append('Python')
        if 'javascript' in bio.lower():
            interests.append('JavaScript')
        if 'startup' in bio.lower():
            interests.append('Startup')
        if 'ai' in bio.lower() or 'ml' in bio.lower():
            interests.append('AI/ML')
        
        return {
            'interests': interests,
            'customer_type': self.classify_customer_type(prospect),
            'likely_budget': self.estimate_budget(prospect),
            'technical_level': self.estimate_technical_level(prospect)
        }
    
    def estimate_budget(self, prospect: ProspectDTO) -> str:
        """Estimate prospect's budget range"""
        customer_type = self.classify_customer_type(prospect)
        
        budget_mapping = {
            'startup_founder': 'medium',
            'enterprise_developer': 'high',
            'ai_researcher': 'low',
            'freelancer': 'low',
            'student': 'very_low',
            'developer': 'medium'
        }
        
        return budget_mapping.get(customer_type, 'medium')
    
    def estimate_technical_level(self, prospect: ProspectDTO) -> str:
        """Estimate prospect's technical level"""
        bio = (prospect.bio or '').lower()
        
        if any(word in bio for word in ['senior', 'lead', 'architect', 'expert']):
            return 'expert'
        elif any(word in bio for word in ['developer', 'engineer', 'programmer']):
            return 'intermediate'
        elif any(word in bio for word in ['learning', 'student', 'beginner']):
            return 'beginner'
        else:
            return 'intermediate'
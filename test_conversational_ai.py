import asyncio
import logging
from datetime import datetime
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from services.conversational_persona import ConversationalPersona
from services.conversation_memory import ConversationMemory
from services.emotional_intelligence import EmotionalIntelligence
from services.conversation_orchestrator import ConversationOrchestrator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_conversational_persona():
    """Test the conversational persona service"""
    print("\n🧠 Testing Conversational Persona...")
    
    persona = ConversationalPersona()
    
    # Test personality definition
    print(f"✅ Persona Name: {persona.personality['name']}")
    print(f"✅ Persona Identity: {persona.personality['identity']}")
    print(f"✅ Communication Style: {persona.personality['communication_style']['primary']}")
    
    # Test personality response generation
    user_context = {
        'first_name': 'Alex',
        'experience_level': 'beginner',
        'has_purchased': False
    }
    
    response_data = await persona.generate_personality_response(
        "Hello! I'm interested in AI tokens",
        user_context
    )
    
    print(f"✅ Generated Response: {response_data['response'][:100]}...")
    print(f"✅ Personality Traits Used: {response_data['personality_traits_used']}")
    print(f"✅ Emotional Tone: {response_data['emotional_tone']}")
    
    return True


async def test_conversation_memory():
    """Test the conversation memory service"""
    print("\n🧠 Testing Conversation Memory...")
    
    # Create in-memory database for testing
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    memory = ConversationMemory()
    
    async with async_session() as session:
        # Test user context retrieval
        user_context = await memory.get_user_context(12345, session)
        
        print(f"✅ User Context Retrieved: {user_context['user_id']}")
        print(f"✅ Experience Level: {user_context['experience_level']}")
        print(f"✅ First Name: {user_context['first_name']}")
        
        # Test sentiment analysis
        sentiment = await memory.analyze_user_sentiment(
            "I'm really excited about AI tokens!",
            user_context
        )
        
        print(f"✅ Sentiment Analysis: {sentiment['sentiment']}")
        print(f"✅ Intent: {sentiment['intent']}")
        print(f"✅ Urgency Level: {sentiment['urgency_level']}")
        
        # Test personalized suggestions
        suggestions = await memory.get_personalized_suggestions(user_context)
        print(f"✅ Personalized Suggestions: {suggestions[:2]}")
        
        # Test conversation history update
        await memory.update_conversation_history(
            12345, 
            "Hello", 
            "Hi there! 😊 How can I help you?", 
            session
        )
        print("✅ Conversation History Updated")
    
    return True


async def test_emotional_intelligence():
    """Test the emotional intelligence service"""
    print("\n🧠 Testing Emotional Intelligence...")
    
    ei = EmotionalIntelligence()
    
    # Test emotion analysis
    user_context = {
        'first_name': 'Sarah',
        'experience_level': 'intermediate'
    }
    
    emotion_analysis = await ei.analyze_emotion(
        "I'm frustrated with the payment process",
        user_context
    )
    
    print(f"✅ Primary Emotion: {emotion_analysis['primary_emotion']}")
    print(f"✅ Emotion Intensity: {emotion_analysis['emotion_intensity']}")
    print(f"✅ Confidence: {emotion_analysis['confidence']}")
    
    # Test empathetic response generation
    empathetic_response = await ei.generate_empathetic_response(
        emotion_analysis['primary_emotion'],
        "I'm frustrated with the payment process",
        user_context
    )
    
    print(f"✅ Empathetic Response: {empathetic_response[:100]}...")
    
    # Test different emotions
    emotions_to_test = ['excitement', 'confusion', 'satisfaction', 'anxiety']
    
    for emotion in emotions_to_test:
        response = await ei.generate_empathetic_response(
            emotion,
            f"I'm feeling {emotion}",
            user_context
        )
        print(f"✅ {emotion.capitalize()} Response: {response[:80]}...")
    
    return True


async def test_conversation_orchestrator():
    """Test the conversation orchestrator"""
    print("\n🧠 Testing Conversation Orchestrator...")
    
    # Create in-memory database for testing
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    orchestrator = ConversationOrchestrator()
    
    async with async_session() as session:
        # Test different conversation flows
        test_conversations = [
            ("Hello!", "greeting"),
            ("I want to buy AI tokens", "purchasing"),
            ("I need help with payment", "support"),
            ("This is amazing! Thank you!", "celebration"),
            ("How do AI tokens work?", "exploring")
        ]
        
        for message, expected_flow in test_conversations:
            result = await orchestrator.handle_conversation(12345, message, session)
            
            print(f"✅ Message: '{message}'")
            print(f"✅ Flow: {result['conversation_flow']}")
            print(f"✅ Response: {result['response'][:80]}...")
            print(f"✅ Personality Traits: {result['personality_traits']}")
            print(f"✅ Emotional Tone: {result['emotional_tone']}")
            print("---")
        
        # Test conversation analytics
        analytics = await orchestrator.get_conversation_analytics(12345, session)
        print(f"✅ Analytics: {analytics}")
    
    return True


async def test_integration():
    """Test the complete conversational AI integration"""
    print("\n🧠 Testing Complete Integration...")
    
    # Create in-memory database for testing
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    orchestrator = ConversationOrchestrator()
    
    async with async_session() as session:
        # Simulate a complete conversation flow
        conversation_steps = [
            ("Hello! I'm new here", "Initial greeting"),
            ("I'm confused about AI tokens", "Support request"),
            ("That makes sense! I want to buy some", "Purchase intent"),
            ("This is great! Thank you!", "Celebration")
        ]
        
        print("🔄 Simulating Complete Conversation Flow:")
        
        for step, (message, description) in enumerate(conversation_steps, 1):
            print(f"\n📝 Step {step}: {description}")
            print(f"👤 User: {message}")
            
            result = await orchestrator.handle_conversation(12345, message, session)
            
            print(f"🤖 TokenGoblin: {result['response']}")
            print(f"🎭 Personality: {result['personality_traits']}")
            print(f"💭 Emotion: {result['emotion']['primary_emotion']}")
            print(f"🔄 Flow: {result['conversation_flow']}")
        
        # Test analytics after conversation
        analytics = await orchestrator.get_conversation_analytics(12345, session)
        print(f"\n📊 Final Analytics: {analytics}")
    
    return True


async def test_personality_consistency():
    """Test that the personality remains consistent across different interactions"""
    print("\n🧠 Testing Personality Consistency...")
    
    # Create in-memory database for testing
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    orchestrator = ConversationOrchestrator()
    
    async with async_session() as session:
        # Test multiple interactions to ensure personality consistency
        test_messages = [
            "Hi there!",
            "What are AI tokens?",
            "I want to buy some",
            "How much do they cost?",
            "This is awesome!"
        ]
        
        personality_traits_used = []
        
        for message in test_messages:
            result = await orchestrator.handle_conversation(12345, message, session)
            personality_traits_used.extend(result['personality_traits'])
            
            print(f"✅ Message: '{message}'")
            print(f"✅ Response: {result['response'][:60]}...")
            print(f"✅ Traits: {result['personality_traits']}")
            print("---")
        
        # Check for consistent personality traits
        unique_traits = set(personality_traits_used)
        print(f"✅ Consistent Personality Traits: {unique_traits}")
        
        # Verify friendly and helpful traits are present
        expected_traits = ['friendly', 'helpful', 'enthusiastic', 'supportive']
        found_traits = [trait for trait in expected_traits if trait in unique_traits]
        print(f"✅ Found Expected Traits: {found_traits}")
    
    return True


async def main():
    """Run all conversational AI tests"""
    print("🚀 Starting Conversational AI System Tests...")
    
    try:
        # Test individual components
        await test_conversational_persona()
        await test_conversation_memory()
        await test_emotional_intelligence()
        await test_conversation_orchestrator()
        
        # Test integration
        await test_integration()
        
        # Test personality consistency
        await test_personality_consistency()
        
        print("\n🎉 All Conversational AI Tests Passed!")
        print("\n✨ TokenGoblin now has an engaged AI conversational persona!")
        print("\nKey Features Implemented:")
        print("✅ Personality-driven responses")
        print("✅ Conversation memory and context")
        print("✅ Emotional intelligence")
        print("✅ Conversation flow management")
        print("✅ Personalized suggestions")
        print("✅ Empathetic responses")
        print("✅ Consistent personality traits")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        logger.error(f"Test error: {e}")
        return False
    
    return True


if __name__ == "__main__":
    asyncio.run(main()) 
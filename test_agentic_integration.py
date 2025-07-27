#!/usr/bin/env python3
"""
Integration Tests for TokenGoblin Agentic Functionality
Tests the complete agentic flow from user interaction to sales completion.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from sqlalchemy.orm import Session
from datetime import datetime
import json

# Import the components we need to test
from services.conversation_orchestrator import ConversationOrchestrator
from services.conversation_memory import ConversationMemory
from services.conversational_persona import ConversationalPersona
from services.emotional_intelligence import EmotionalIntelligence
from handlers.user.ai_tokens import ai_tokens_text_message
from run_agentic import handle_conversational_ai_message


class TestAgenticIntegration:
    """Integration tests for complete agentic flow"""
    
    @pytest.fixture
    async def full_orchestrator_setup(self):
        """Set up a complete orchestrator with all dependencies"""
        orchestrator = ConversationOrchestrator()
        
        # Mock the dependencies
        orchestrator.memory = Mock(spec=ConversationMemory)
        orchestrator.persona = Mock(spec=ConversationalPersona)
        orchestrator.emotional_intelligence = Mock(spec=EmotionalIntelligence)
        
        # Set up mock responses
        orchestrator.memory.get_user_context.return_value = {
            'user_id': 12345,
            'first_name': 'Test',
            'last_name': 'User',
            'interaction_count': 1,
            'experience_level': 'beginner',
            'has_purchased': False,
            'conversation_history': [],
            'last_interaction': datetime.now().isoformat()
        }
        
        orchestrator.emotional_intelligence.analyze_sentiment.return_value = {
            'sentiment': 'positive',
            'confidence': 0.85,
            'intent': 'purchase'
        }
        
        orchestrator.emotional_intelligence.analyze_emotion.return_value = {
            'primary_emotion': 'excitement',
            'confidence': 0.78,
            'emotional_intensity': 'high'
        }
        
        return orchestrator
    
    @pytest.fixture
    def mock_telegram_message(self):
        """Create a mock Telegram message"""
        message = Mock()
        message.from_user.id = 12345
        message.from_user.first_name = "Test"
        message.from_user.last_name = "User"
        message.from_user.username = "testuser"
        message.text = "I want to buy tokens"
        message.chat.id = 12345
        return message
    
    @pytest.fixture
    def mock_session(self):
        """Create a mock database session"""
        session = Mock(spec=Session)
        session.commit = AsyncMock()
        session.rollback = AsyncMock()
        return session

    @pytest.mark.asyncio
    async def test_complete_agentic_sales_flow(self, full_orchestrator_setup, mock_telegram_message, mock_session):
        """Test the complete agentic sales flow from start to finish"""
        
        # Step 1: User initiates conversation with sales intent
        response_data = await full_orchestrator_setup.handle_conversation(
            user_id=12345,
            user_message="I need 5000 tokens",
            session=mock_session
        )
        
        # Verify the response is agentic
        assert response_data is not None
        assert 'response' in response_data
        
        response = response_data['response']
        
        # Should detect sales opportunity and provide pricing
        assert "5,000 tokens" in response
        assert "Developer Pack" in response
        assert "$95" in response
        assert "Agentic Action" in response
        assert "payment method" in response.lower()
    
    @pytest.mark.asyncio
    async def test_agentic_sales_progression(self, full_orchestrator_setup, mock_session):
        """Test the progression of agentic sales conversation"""
        
        # Step 1: Initial inquiry
        response1 = await full_orchestrator_setup.handle_conversation(
            user_id=12345,
            user_message="How much do tokens cost?",
            session=mock_session
        )
        
        assert "Agentic Action" in response1['response']
        assert "packages" in response1['response'].lower()
        
        # Step 2: User specifies amount
        response2 = await full_orchestrator_setup.handle_conversation(
            user_id=12345,
            user_message="I want 1000 tokens",
            session=mock_session
        )
        
        assert "1,000 tokens" in response2['response']
        assert "Quick Start" in response2['response']
        assert "$20" in response2['response']
        
        # Step 3: User chooses payment method
        response3 = await full_orchestrator_setup.handle_conversation(
            user_id=12345,
            user_message="I'll pay with USDT",
            session=mock_session
        )
        
        assert "USDT" in response3['response']
        assert "payment request" in response3['response'].lower()
    
    @pytest.mark.asyncio
    async def test_agentic_greeting_to_sales_conversion(self, full_orchestrator_setup, mock_session):
        """Test conversion from greeting to sales"""
        
        # Step 1: User greets the bot
        greeting_response = await full_orchestrator_setup.handle_conversation(
            user_id=12345,
            user_message="Hello",
            session=mock_session
        )
        
        # Should proactively offer sales
        assert "Agentic Services" in greeting_response['response']
        assert "Instant Token Sales" in greeting_response['response']
        
        # Step 2: User shows interest
        interest_response = await full_orchestrator_setup.handle_conversation(
            user_id=12345,
            user_message="Tell me about your packages",
            session=mock_session
        )
        
        # Should switch to agentic sales flow
        assert "packages" in interest_response['response'].lower()
        assert "Agentic Action" in interest_response['response']
    
    @pytest.mark.asyncio
    async def test_agentic_payment_method_handling(self, full_orchestrator_setup, mock_session):
        """Test agentic handling of different payment methods"""
        
        payment_methods = [
            ("USDT", "USDT"),
            ("Bitcoin", "BITCOIN"),
            ("BTC", "BITCOIN"),
            ("Ethereum", "ETHEREUM"),
            ("ETH", "ETHEREUM"),
            ("Tether", "USDT")
        ]
        
        for user_input, expected_method in payment_methods:
            response = await full_orchestrator_setup.handle_conversation(
                user_id=12345,
                user_message=f"I want to pay with {user_input}",
                session=mock_session
            )
            
            assert expected_method in response['response'], f"Failed to recognize {user_input}"
            assert "payment request" in response['response'].lower()
    
    @pytest.mark.asyncio
    async def test_agentic_token_calculation_accuracy(self, full_orchestrator_setup, mock_session):
        """Test accuracy of token calculations in agentic responses"""
        
        test_cases = [
            (1000, 20.0),
            (5000, 95.0),
            (10000, 180.0),
            (2500, 45.0),
            (15000, 270.0)
        ]
        
        for token_amount, expected_price in test_cases:
            response = await full_orchestrator_setup.handle_conversation(
                user_id=12345,
                user_message=f"I need {token_amount} tokens",
                session=mock_session
            )
            
            response_text = response['response']
            assert str(expected_price) in response_text, f"Price {expected_price} not found for {token_amount} tokens"
            assert str(token_amount) in response_text, f"Token amount {token_amount} not found in response"
    
    @pytest.mark.asyncio
    async def test_agentic_user_context_persistence(self, full_orchestrator_setup, mock_session):
        """Test that user context is maintained throughout agentic interactions"""
        
        # First interaction
        response1 = await full_orchestrator_setup.handle_conversation(
            user_id=12345,
            user_message="Hello",
            session=mock_session
        )
        
        # Verify user context was retrieved
        full_orchestrator_setup.memory.get_user_context.assert_called_with(12345, mock_session)
        
        # Second interaction
        response2 = await full_orchestrator_setup.handle_conversation(
            user_id=12345,
            user_message="I want tokens",
            session=mock_session
        )
        
        # Should maintain context
        assert full_orchestrator_setup.memory.get_user_context.call_count >= 2
    
    @pytest.mark.asyncio
    async def test_agentic_emotional_intelligence_integration(self, full_orchestrator_setup, mock_session):
        """Test that emotional intelligence is integrated into agentic responses"""
        
        # Test with different emotional contexts
        emotional_contexts = [
            ("I'm excited to buy tokens!", "excitement"),
            ("I'm worried about the cost", "concern"),
            ("I need help with tokens", "confusion")
        ]
        
        for message, expected_emotion in emotional_contexts:
            # Update mock to return different emotions
            full_orchestrator_setup.emotional_intelligence.analyze_emotion.return_value = {
                'primary_emotion': expected_emotion,
                'confidence': 0.8,
                'emotional_intensity': 'medium'
            }
            
            response = await full_orchestrator_setup.handle_conversation(
                user_id=12345,
                user_message=message,
                session=mock_session
            )
            
            # Should have appropriate emotional tone
            assert 'emotional_tone' in response
            assert response['emotional_tone'] in ['excited', 'supportive', 'empathetic', 'helpful']
    
    @pytest.mark.asyncio
    async def test_agentic_sales_optimization(self, full_orchestrator_setup, mock_session):
        """Test that agentic responses are optimized for sales conversion"""
        
        # Test various sales triggers
        sales_triggers = [
            "tokens",
            "buy",
            "purchase",
            "price",
            "cost",
            "need",
            "want"
        ]
        
        for trigger in sales_triggers:
            response = await full_orchestrator_setup.handle_conversation(
                user_id=12345,
                user_message=f"I {trigger} tokens",
                session=mock_session
            )
            
            # Should provide immediate actionable information
            response_text = response['response']
            assert "Agentic Action" in response_text
            assert "tokens" in response_text.lower()
            assert "payment" in response_text.lower() or "package" in response_text.lower()
    
    @pytest.mark.asyncio
    async def test_agentic_conversation_memory(self, full_orchestrator_setup, mock_session):
        """Test that conversation memory enhances agentic responses"""
        
        # Simulate conversation history
        conversation_history = [
            {'message': 'Hello', 'response': 'Hi! How can I help?', 'timestamp': datetime.now().isoformat()},
            {'message': 'I want tokens', 'response': 'Great! How many?', 'timestamp': datetime.now().isoformat()},
            {'message': '1000 tokens', 'response': 'Perfect! $20 USD', 'timestamp': datetime.now().isoformat()}
        ]
        
        # Update mock to return conversation history
        full_orchestrator_setup.memory.get_user_context.return_value = {
            'user_id': 12345,
            'first_name': 'Test',
            'interaction_count': 4,
            'conversation_history': conversation_history,
            'has_purchased': False
        }
        
        response = await full_orchestrator_setup.handle_conversation(
            user_id=12345,
            user_message="I'm ready to proceed",
            session=mock_session
        )
        
        # Should reference previous conversation context
        response_text = response['response']
        assert "proceed" in response_text.lower() or "continue" in response_text.lower() or "payment" in response_text.lower()
    
    @pytest.mark.asyncio
    async def test_agentic_error_handling(self, full_orchestrator_setup, mock_session):
        """Test that agentic system handles errors gracefully"""
        
        # Simulate an error in emotional intelligence
        full_orchestrator_setup.emotional_intelligence.analyze_emotion.side_effect = Exception("AI Service Error")
        
        # Should still provide a response
        response = await full_orchestrator_setup.handle_conversation(
            user_id=12345,
            user_message="I want tokens",
            session=mock_session
        )
        
        assert response is not None
        assert 'response' in response
        assert len(response['response']) > 0
    
    @pytest.mark.asyncio
    async def test_agentic_performance_metrics(self, full_orchestrator_setup, mock_session):
        """Test that agentic system provides performance metrics"""
        
        # Test response time
        import time
        start_time = time.time()
        
        response = await full_orchestrator_setup.handle_conversation(
            user_id=12345,
            user_message="I need 1000 tokens",
            session=mock_session
        )
        
        end_time = time.time()
        response_time = end_time - start_time
        
        # Should respond quickly (under 1 second for unit test)
        assert response_time < 1.0, f"Response too slow: {response_time:.2f}s"
        
        # Should provide structured response
        assert 'response' in response
        assert 'personality_traits_used' in response
        assert 'emotional_tone' in response
        assert 'suggested_actions' in response


class TestAgenticEffectivenessMetrics:
    """Test suite for measuring agentic effectiveness"""
    
    @pytest.mark.asyncio
    async def test_sales_conversion_rate_optimization(self):
        """Test that agentic responses optimize for sales conversion"""
        
        orchestrator = ConversationOrchestrator()
        
        # Test conversion optimization
        conversion_triggers = [
            "I want to buy",
            "How much?",
            "I need tokens",
            "What packages?"
        ]
        
        for trigger in conversion_triggers:
            response_data = await orchestrator._handle_agentic_sales_flow(
                trigger, {}, []
            )
            
            response = response_data['response']
            
            # Should include conversion elements
            assert "Agentic Action" in response
            assert "payment" in response.lower() or "order" in response.lower()
            assert "tokens" in response.lower()
    
    @pytest.mark.asyncio
    async def test_user_engagement_optimization(self):
        """Test that responses optimize for user engagement"""
        
        orchestrator = ConversationOrchestrator()
        
        response_data = await orchestrator._handle_greeting_flow(
            "Hello", {}, []
        )
        
        response = response_data['response']
        
        # Engagement optimization checks
        engagement_elements = [
            "?",  # Questions
            "packages",  # Specific offerings
            "Agentic Action",  # Clear next steps
            "🚀",  # Emojis for engagement
            "tokens"  # Core product
        ]
        
        for element in engagement_elements:
            assert element in response, f"Missing engagement element: {element}"
    
    @pytest.mark.asyncio
    async def test_response_quality_metrics(self):
        """Test response quality metrics"""
        
        orchestrator = ConversationOrchestrator()
        
        response_data = await orchestrator._handle_agentic_sales_flow(
            "1000 tokens", {}, []
        )
        
        response = response_data['response']
        
        # Quality metrics
        assert len(response) > 100  # Substantial response
        assert "1000" in response  # Specific information
        assert "$" in response  # Pricing information
        assert "Agentic Action" in response  # Clear action
        assert "payment" in response.lower()  # Next step


if __name__ == "__main__":
    # Run the integration tests
    pytest.main([__file__, "-v", "-m", "integration"]) 
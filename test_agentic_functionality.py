#!/usr/bin/env python3
"""
Unit Tests for TokenGoblin Agentic Functionality
Tests the bot's agentic capabilities including sales detection, token calculation, 
payment recognition, and proactive responses.
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from sqlalchemy.orm import Session
from datetime import datetime

# Import the components we need to test
from services.conversation_orchestrator import ConversationOrchestrator
from services.conversation_memory import ConversationMemory
from services.conversational_persona import ConversationalPersona
from services.emotional_intelligence import EmotionalIntelligence
from enums.bot_entity import BotEntity


class TestAgenticFunctionality:
    """Test suite for agentic functionality"""
    
    @pytest.fixture
    def conversation_orchestrator(self):
        """Create a conversation orchestrator instance for testing"""
        orchestrator = ConversationOrchestrator()
        return orchestrator
    
    @pytest.fixture
    def mock_session(self):
        """Create a mock database session"""
        return Mock(spec=Session)
    
    @pytest.fixture
    def sample_user_context(self):
        """Sample user context for testing"""
        return {
            'user_id': 12345,
            'first_name': 'Test',
            'last_name': 'User',
            'interaction_count': 1,
            'experience_level': 'beginner',
            'has_purchased': False,
            'conversation_history': [],
            'last_interaction': datetime.now().isoformat()
        }
    
    @pytest.fixture
    def sample_sentiment_analysis(self):
        """Sample sentiment analysis for testing"""
        return {
            'sentiment': 'positive',
            'confidence': 0.85,
            'intent': 'purchase'
        }
    
    @pytest.fixture
    def sample_emotion_analysis(self):
        """Sample emotion analysis for testing"""
        return {
            'primary_emotion': 'excitement',
            'confidence': 0.78,
            'emotional_intensity': 'high'
        }

    @pytest.mark.asyncio
    async def test_agentic_sales_detection(self, conversation_orchestrator, sample_user_context, sample_sentiment_analysis, sample_emotion_analysis):
        """Test that the bot detects sales opportunities proactively"""
        
        # Test various sales-related messages
        sales_messages = [
            "I want to buy tokens",
            "How much do tokens cost?",
            "I need 1000 tokens",
            "Looking for AI tokens",
            "What's the price for tokens?",
            "I want to purchase some tokens",
            "Get me some tokens",
            "Order tokens please"
        ]
        
        for message in sales_messages:
            flow = await conversation_orchestrator._determine_conversation_flow(
                message, sample_user_context, sample_sentiment_analysis, sample_emotion_analysis
            )
            assert flow == 'agentic_sales', f"Failed to detect sales opportunity in: '{message}'"
    
    @pytest.mark.asyncio
    async def test_token_amount_calculation(self, conversation_orchestrator, sample_user_context):
        """Test that the bot correctly calculates token pricing"""
        
        # Test different token amounts
        test_cases = [
            (1000, 20.0, "Quick Start"),
            (5000, 95.0, "Developer Pack"),
            (10000, 180.0, "Pro Pack"),
            (2500, 45.0, "Custom Package"),  # 2500 * 0.018
            (15000, 270.0, "Custom Package")  # 15000 * 0.018
        ]
        
        for token_amount, expected_price, expected_package in test_cases:
            response_data = await conversation_orchestrator._handle_agentic_sales_flow(
                f"I need {token_amount} tokens", sample_user_context, []
            )
            
            response = response_data['response']
            assert str(expected_price) in response, f"Price {expected_price} not found in response for {token_amount} tokens"
            assert expected_package in response, f"Package {expected_package} not found in response for {token_amount} tokens"
    
    @pytest.mark.asyncio
    async def test_payment_method_recognition(self, conversation_orchestrator, sample_user_context):
        """Test that the bot recognizes different payment methods"""
        
        payment_test_cases = [
            ("I want to pay with USDT", "USDT"),
            ("Bitcoin payment please", "BITCOIN"),
            ("I'll pay with ETH", "ETHEREUM"),
            ("Tether payment", "USDT"),
            ("BTC is my preference", "BITCOIN"),
            ("Ethereum works for me", "ETHEREUM")
        ]
        
        for message, expected_payment in payment_test_cases:
            response_data = await conversation_orchestrator._handle_agentic_sales_flow(
                message, sample_user_context, []
            )
            
            response = response_data['response']
            assert expected_payment in response, f"Payment method {expected_payment} not recognized in: '{message}'"
    
    @pytest.mark.asyncio
    async def test_proactive_greeting_sales_offer(self, conversation_orchestrator, sample_user_context):
        """Test that greeting flow proactively offers sales"""
        
        response_data = await conversation_orchestrator._handle_greeting_flow(
            "Hello", sample_user_context, []
        )
        
        response = response_data['response']
        
        # Check for agentic sales language
        assert "Agentic Services" in response
        assert "Instant Token Sales" in response
        assert "Agentic Action" in response
        assert "tokens" in response.lower()
        assert "packages" in response.lower()
    
    @pytest.mark.asyncio
    async def test_agentic_sales_response_structure(self, conversation_orchestrator, sample_user_context):
        """Test that agentic sales responses have the correct structure"""
        
        response_data = await conversation_orchestrator._handle_agentic_sales_flow(
            "I want to buy 5000 tokens", sample_user_context, []
        )
        
        # Check response structure
        assert 'response' in response_data
        assert 'personality_traits_used' in response_data
        assert 'emotional_tone' in response_data
        assert 'suggested_actions' in response_data
        
        # Check for agentic language
        response = response_data['response']
        assert "Agentic Action" in response
        assert "process your order" in response.lower()
        assert "payment method" in response.lower()
    
    @pytest.mark.asyncio
    async def test_agentic_suggestions(self, conversation_orchestrator, sample_user_context):
        """Test that the bot provides agentic suggestions"""
        
        suggestions = await conversation_orchestrator.suggest_next_actions(
            sample_user_context, 'agentic_sales'
        )
        
        # Check that suggestions contain agentic language
        for suggestion in suggestions:
            assert "Agentic Action" in suggestion or "Instant" in suggestion or "Smart" in suggestion
    
    @pytest.mark.asyncio
    async def test_proactive_follow_up_generation(self, conversation_orchestrator, sample_user_context, mock_session):
        """Test proactive follow-up message generation"""
        
        # Test for new user (no purchase history)
        sample_user_context['interaction_count'] = 3
        sample_user_context['has_purchased'] = False
        
        follow_up = await conversation_orchestrator.generate_proactive_follow_up(
            12345, sample_user_context, mock_session
        )
        
        assert follow_up is not None
        assert "Agentic Follow-up" in follow_up
        assert "packages" in follow_up.lower()
        
        # Test for returning customer
        sample_user_context['has_purchased'] = True
        
        follow_up = await conversation_orchestrator.generate_proactive_follow_up(
            12345, sample_user_context, mock_session
        )
        
        assert follow_up is not None
        assert "Welcome back" in follow_up
        assert "Pro Pack" in follow_up
    
    @pytest.mark.asyncio
    async def test_conversation_flow_prioritization(self, conversation_orchestrator, sample_user_context, sample_sentiment_analysis, sample_emotion_analysis):
        """Test that sales opportunities are prioritized over other flows"""
        
        # Test that sales keywords trigger agentic_sales even with other context
        message = "Hello, I want to buy some tokens"
        
        flow = await conversation_orchestrator._determine_conversation_flow(
            message, sample_user_context, sample_sentiment_analysis, sample_emotion_analysis
        )
        
        assert flow == 'agentic_sales', "Sales opportunity should be prioritized over greeting"
    
    @pytest.mark.asyncio
    async def test_agentic_language_consistency(self, conversation_orchestrator, sample_user_context):
        """Test that agentic language is consistent across different flows"""
        
        # Test greeting flow
        greeting_response = await conversation_orchestrator._handle_greeting_flow(
            "Hi", sample_user_context, []
        )
        
        # Test agentic sales flow
        sales_response = await conversation_orchestrator._handle_agentic_sales_flow(
            "I need tokens", sample_user_context, []
        )
        
        # Both should contain agentic language
        assert "Agentic" in greeting_response['response']
        assert "Agentic" in sales_response['response']
        
        # Both should be enthusiastic
        assert greeting_response['emotional_tone'] == 'enthusiastic'
        assert sales_response['emotional_tone'] == 'excited'
    
    @pytest.mark.asyncio
    async def test_token_package_recommendations(self, conversation_orchestrator, sample_user_context):
        """Test that the bot recommends appropriate token packages"""
        
        response_data = await conversation_orchestrator._handle_agentic_sales_flow(
            "What packages do you have?", sample_user_context, []
        )
        
        response = response_data['response']
        
        # Check for package recommendations
        assert "1,000 tokens" in response
        assert "5,000 tokens" in response
        assert "10,000 tokens" in response
        assert "Quick Start" in response
        assert "Developer Pack" in response
        assert "Pro Pack" in response
    
    @pytest.mark.asyncio
    async def test_payment_options_presentation(self, conversation_orchestrator, sample_user_context):
        """Test that payment options are clearly presented"""
        
        response_data = await conversation_orchestrator._handle_agentic_sales_flow(
            "How can I pay?", sample_user_context, []
        )
        
        response = response_data['response']
        
        # Check for payment options
        assert "USDT" in response
        assert "Bitcoin" in response or "BTC" in response
        assert "Ethereum" in response or "ETH" in response
        assert "TRC20" in response or "ERC20" in response
    
    @pytest.mark.asyncio
    async def test_agentic_action_prompts(self, conversation_orchestrator, sample_user_context):
        """Test that the bot provides clear action prompts"""
        
        response_data = await conversation_orchestrator._handle_agentic_sales_flow(
            "I'm ready to buy", sample_user_context, []
        )
        
        response = response_data['response']
        
        # Check for action prompts
        assert "Agentic Action" in response
        assert "process" in response.lower()
        assert "create" in response.lower() or "set up" in response.lower()
    
    @pytest.mark.asyncio
    async def test_user_context_integration(self, conversation_orchestrator, sample_user_context):
        """Test that user context is properly integrated into responses"""
        
        # Test with user's first name
        response_data = await conversation_orchestrator._handle_greeting_flow(
            "Hello", sample_user_context, []
        )
        
        response = response_data['response']
        assert "Test" in response  # User's first name should be included
    
    @pytest.mark.asyncio
    async def test_emotional_intelligence_integration(self, conversation_orchestrator, sample_user_context, sample_emotion_analysis):
        """Test that emotional intelligence is integrated into responses"""
        
        response_data = await conversation_orchestrator._handle_support_flow(
            "I need help", sample_user_context, sample_emotion_analysis, []
        )
        
        # Should have emotional tone
        assert 'emotional_tone' in response_data
        assert response_data['emotional_tone'] in ['supportive', 'empathetic', 'helpful']
    
    @pytest.mark.asyncio
    async def test_conversation_memory_integration(self, conversation_orchestrator, sample_user_context):
        """Test that conversation memory is properly used"""
        
        # Add some conversation history
        sample_user_context['conversation_history'] = [
            {'message': 'I want tokens', 'response': 'Great!', 'timestamp': datetime.now().isoformat()},
            {'message': 'How much?', 'response': 'Let me show you', 'timestamp': datetime.now().isoformat()}
        ]
        
        response_data = await conversation_orchestrator._handle_agentic_sales_flow(
            "I'm ready to proceed", sample_user_context, sample_user_context['conversation_history']
        )
        
        # Should reference previous conversation
        response = response_data['response']
        assert "proceed" in response.lower() or "continue" in response.lower()


class TestAgenticEffectiveness:
    """Test suite for measuring agentic effectiveness"""
    
    @pytest.mark.asyncio
    async def test_sales_conversion_optimization(self):
        """Test that the bot optimizes for sales conversion"""
        
        orchestrator = ConversationOrchestrator()
        
        # Test that sales opportunities are detected quickly
        sales_messages = [
            "tokens",
            "buy",
            "price",
            "cost"
        ]
        
        for message in sales_messages:
            flow = await orchestrator._determine_conversation_flow(
                message, {}, {}, {}
            )
            assert flow == 'agentic_sales', f"Should detect sales opportunity in '{message}'"
    
    @pytest.mark.asyncio
    async def test_response_time_optimization(self):
        """Test that responses are optimized for speed and effectiveness"""
        
        orchestrator = ConversationOrchestrator()
        
        # Test that agentic responses are immediate and actionable
        response_data = await orchestrator._handle_agentic_sales_flow(
            "1000 tokens", {}, []
        )
        
        response = response_data['response']
        
        # Should provide immediate actionable information
        assert "1000" in response
        assert "$" in response  # Price information
        assert "payment" in response.lower()  # Next step
    
    @pytest.mark.asyncio
    async def test_user_engagement_optimization(self):
        """Test that responses optimize for user engagement"""
        
        orchestrator = ConversationOrchestrator()
        
        # Test that responses encourage continued interaction
        response_data = await orchestrator._handle_greeting_flow(
            "Hello", {}, []
        )
        
        response = response_data['response']
        
        # Should include multiple engagement points
        assert "?" in response  # Questions encourage responses
        assert "packages" in response.lower()  # Specific offerings
        assert "Agentic Action" in response  # Clear next steps


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"]) 
"""
Test configuration and fixtures
"""
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set test environment variables
os.environ['DB_NAME'] = 'test_arbitrage.db'
os.environ['LOG_LEVEL'] = 'DEBUG'
os.environ['REDIS_HOST'] = 'localhost'
os.environ['REDIS_PASSWORD'] = ''
os.environ['OPENROUTER_API_KEY'] = 'sk-or-v1-test-key'
os.environ['TOKEN_MARKUP_PERCENTAGE'] = '25'
os.environ['MIN_PROFIT_MARGIN'] = '0.10'
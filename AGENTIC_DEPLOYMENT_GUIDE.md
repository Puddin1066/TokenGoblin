# 🤖 Agentic Claude AI Token Resale Bot - Deployment Guide

## 🎯 Overview

This guide will help you deploy the agentic Claude AI token resale bot that automatically:
- **Discovers sales opportunities** through intelligent lead generation
- **Executes proactive outreach** to high-value prospects
- **Optimizes pricing dynamically** based on market conditions
- **Manages inventory automatically** with predictive restocking
- **Processes crypto payments** across multiple blockchains
- **Provides intelligent customer support** using Claude AI

## 📋 Prerequisites

### Required API Keys
```bash
# OpenRouter API (for Claude token procurement)
OPENROUTER_API_KEY=your_openrouter_api_key

# Anthropic API (for customer support and analytics)
ANTHROPIC_API_KEY=your_anthropic_api_key

# Telegram Bot Token
TOKEN=your_telegram_bot_token

# Web3 Provider (for blockchain payments)
WEB3_PROVIDER_URL=https://mainnet.infura.io/v3/your_project_id

# Redis (for caching and task queues)
REDIS_HOST=localhost
REDIS_PASSWORD=your_redis_password
```

### System Requirements
- **OS**: Linux (Ubuntu 20.04+ recommended)
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 50GB available space
- **Python**: 3.12+
- **Docker**: 20.10+ (for containerized deployment)

## 🚀 Quick Start Deployment

### 1. Clone and Setup
```bash
# Clone the repository
git clone https://github.com/your-repo/aiogram-shop-bot.git
cd aiogram-shop-bot

# Install dependencies
pip install -r requirements_agentic.txt

# Set up environment variables
cp .env.example .env
```

### 2. Configure Environment Variables
```bash
# Edit .env file
nano .env
```

Add the following variables:
```env
# Bot Configuration
TOKEN=your_telegram_bot_token
ADMIN_ID_LIST=123456,654321
SUPPORT_LINK=https://t.me/your_username

# Agentic Features
OPENROUTER_API_KEY=your_openrouter_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
AGENTIC_MODE=true

# Database
DB_NAME=database.db
DB_ENCRYPTION=false
DB_PASS=

# Payment Processing
WEB3_PROVIDER_URL=https://mainnet.infura.io/v3/your_project_id
KRYPTO_EXPRESS_API_KEY=your_krypto_express_key
KRYPTO_EXPRESS_API_URL=https://kryptoexpress.pro/api
KRYPTO_EXPRESS_API_SECRET=your_secret

# Task Queue
REDIS_HOST=localhost
REDIS_PASSWORD=your_redis_password
CELERY_BROKER_URL=redis://localhost:6379

# Monitoring
PROMETHEUS_ENDPOINT=localhost:9090
LOG_LEVEL=INFO

# Agentic Configuration
MIN_INVENTORY_THRESHOLD=1000
MAX_PURCHASE_BUDGET=500
OPPORTUNITY_CHECK_INTERVAL=3600
PRICING_UPDATE_INTERVAL=1800
```

### 3. Database Setup
```bash
# Initialize database
python -c "from db import init_db; init_db()"

# Run migrations (if using Alembic)
alembic upgrade head
```

### 4. Start Redis
```bash
# Install Redis
sudo apt update
sudo apt install redis-server

# Start Redis
sudo systemctl start redis-server
sudo systemctl enable redis-server

# Test Redis connection
redis-cli ping
```

### 5. Start the Bot
```bash
# Start the main bot
python run.py

# In another terminal, start Celery worker
celery -A bot.celery worker --loglevel=info

# In another terminal, start Celery beat (for scheduled tasks)
celery -A bot.celery beat --loglevel=info
```

## 🐳 Docker Deployment

### 1. Docker Compose Setup
```yaml
# docker-compose.agentic.yml
version: '3.8'

services:
  ai-bot:
    build: .
    environment:
      - TOKEN=${TOKEN}
      - ADMIN_ID_LIST=${ADMIN_ID_LIST}
      - OPENROUTER_API_KEY=${OPENROUTER_API_KEY}
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
      - AGENTIC_MODE=true
      - REDIS_HOST=redis
      - CELERY_BROKER_URL=redis://redis:6379
    depends_on:
      - redis
      - celery-worker
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data

  celery-worker:
    build: .
    command: celery -A bot.celery worker --loglevel=info
    environment:
      - CELERY_BROKER_URL=redis://redis:6379
      - OPENROUTER_API_KEY=${OPENROUTER_API_KEY}
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
    depends_on:
      - redis

  celery-beat:
    build: .
    command: celery -A bot.celery beat --loglevel=info
    environment:
      - CELERY_BROKER_URL=redis://redis:6379
    depends_on:
      - redis

  redis:
    image: redis:alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml

  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana_data:/var/lib/grafana

volumes:
  redis_data:
  grafana_data:
```

### 2. Start with Docker Compose
```bash
# Start all services
docker-compose -f docker-compose.agentic.yml up -d

# Check logs
docker-compose -f docker-compose.agentic.yml logs -f ai-bot

# Stop services
docker-compose -f docker-compose.agentic.yml down
```

## 🔧 Agentic Features Configuration

### 1. Lead Generation Settings
```python
# In services/agentic_sales.py
lead_scoring_weights = {
    'browse_frequency': 0.3,      # Weight for browsing behavior
    'cart_abandonment': 0.25,     # Weight for abandoned carts
    'session_duration': 0.2,      # Weight for session length
    'previous_purchases': 0.15,   # Weight for purchase history
    'engagement_level': 0.1       # Weight for engagement metrics
}
```

### 2. Pricing Optimization
```python
# In services/agentic_orchestrator.py
pricing_config = {
    'min_markup': 0.1,           # Minimum 10% markup
    'max_markup': 0.5,           # Maximum 50% markup
    'competitor_weight': 0.4,    # Weight for competitor pricing
    'demand_weight': 0.3,        # Weight for demand signals
    'cost_weight': 0.3           # Weight for cost considerations
}
```

### 3. Inventory Management
```python
# In services/agentic_orchestrator.py
inventory_config = {
    'min_inventory_threshold': 1000,    # Minimum tokens to maintain
    'max_purchase_budget': 500,         # Maximum USD per purchase
    'restock_lead_time': 3600,          # Time to restock (seconds)
    'demand_prediction_days': 7         # Days to predict demand
}
```

## 📊 Monitoring and Analytics

### 1. Prometheus Configuration
```yaml
# prometheus.yml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'ai-bot'
    static_configs:
      - targets: ['ai-bot:8000']
    metrics_path: '/metrics'

  - job_name: 'redis'
    static_configs:
      - targets: ['redis:6379']
```

### 2. Key Metrics to Monitor
- **Sales Opportunities**: Number of identified leads
- **Conversion Rate**: Percentage of opportunities converted
- **Token Inventory**: Current token levels
- **Payment Success Rate**: Successful payment percentage
- **Response Time**: Bot response latency
- **Error Rate**: System error frequency

### 3. Grafana Dashboards
Access Grafana at `http://localhost:3000` (admin/admin) to view:
- Real-time sales metrics
- Token inventory levels
- Payment processing status
- User engagement analytics

## 🔒 Security Considerations

### 1. API Key Security
```bash
# Store API keys securely
export OPENROUTER_API_KEY="your_key"
export ANTHROPIC_API_KEY="your_key"

# Use environment variables in production
echo "export OPENROUTER_API_KEY=your_key" >> ~/.bashrc
```

### 2. Database Encryption
```python
# Enable database encryption
DB_ENCRYPTION=true
DB_PASS=your_secure_password
```

### 3. Webhook Security
```python
# Verify webhook signatures
WEBHOOK_SECRET_TOKEN=your_secure_token
```

## 🚨 Troubleshooting

### Common Issues

#### 1. Redis Connection Error
```bash
# Check Redis status
sudo systemctl status redis-server

# Restart Redis
sudo systemctl restart redis-server
```

#### 2. Celery Worker Not Starting
```bash
# Check Celery logs
celery -A bot.celery worker --loglevel=debug

# Restart Celery
pkill -f celery
celery -A bot.celery worker --loglevel=info
```

#### 3. OpenRouter API Errors
```bash
# Test OpenRouter connection
curl -H "Authorization: Bearer $OPENROUTER_API_KEY" \
     https://openrouter.ai/api/v1/models
```

#### 4. Payment Processing Issues
```bash
# Check payment processor logs
docker-compose logs payment-processor

# Test payment webhooks
curl -X POST http://localhost:8000/webhook/payment \
     -H "Content-Type: application/json" \
     -d '{"test": "webhook"}'
```

## 📈 Performance Optimization

### 1. Database Optimization
```sql
-- Add indexes for better performance
CREATE INDEX idx_user_telegram_id ON users(telegram_id);
CREATE INDEX idx_payment_status ON payments(status);
CREATE INDEX idx_item_category ON items(category_id);
```

### 2. Caching Strategy
```python
# Redis caching configuration
CACHE_TTL = 3600  # 1 hour
CACHE_PREFIX = "ai_bot:"
```

### 3. Rate Limiting
```python
# Rate limiting configuration
RATE_LIMIT_PER_USER = 100  # requests per hour
RATE_LIMIT_PER_IP = 1000   # requests per hour
```

## 🔄 Updates and Maintenance

### 1. Update Dependencies
```bash
# Update requirements
pip install -r requirements_agentic.txt --upgrade

# Update Docker images
docker-compose pull
docker-compose up -d
```

### 2. Database Backups
```bash
# Create backup
sqlite3 database.db ".backup backup_$(date +%Y%m%d_%H%M%S).db"

# Restore backup
sqlite3 database.db ".restore backup_file.db"
```

### 3. Log Rotation
```bash
# Configure log rotation
sudo logrotate -f /etc/logrotate.d/ai-bot
```

## 📞 Support

For issues and questions:
- **Documentation**: Check the README.md file
- **Issues**: Create an issue on GitHub
- **Discord**: Join our community server
- **Email**: support@yourdomain.com

## 🎉 Success Metrics

Monitor these key performance indicators:

1. **Sales Conversion Rate**: Target >15%
2. **Average Order Value**: Target >$50
3. **Customer Retention Rate**: Target >80%
4. **Payment Success Rate**: Target >95%
5. **Response Time**: Target <2 seconds
6. **Token Inventory Turnover**: Target >3x per month

Your agentic Claude AI token resale bot is now ready to autonomously discover and execute sales opportunities! 🚀
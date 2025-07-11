# AI Token Arbitrage Bot - Deployment Guide

## 🚀 Production Deployment

### Prerequisites
- Linux server (Ubuntu 20.04+ recommended)
- Docker and Docker Compose
- Domain name with SSL certificate
- 2GB+ RAM, 20GB+ storage
- Redis server
- PostgreSQL database (recommended for production)

### Production Environment Setup

#### 1. Server Preparation
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Create application directory
sudo mkdir -p /opt/ai-arbitrage
sudo chown $USER:$USER /opt/ai-arbitrage
cd /opt/ai-arbitrage
```

#### 2. Environment Configuration
```bash
# Clone repository
git clone <your-repo-url> .

# Create production environment file
cp .env.example .env.production

# Edit production configuration
nano .env.production
```

**Production .env.production:**
```env
# Production Configuration
RUNTIME_ENVIRONMENT=prod
WEBAPP_HOST=0.0.0.0
WEBAPP_PORT=8000

# Bot Configuration
TOKEN=your_production_bot_token
ADMIN_ID_LIST=your_telegram_id
WEBHOOK_SECRET_TOKEN=secure_random_string_here
WEBHOOK_PATH=/webhook/bot

# Database (PostgreSQL recommended)
DATABASE_URL=postgresql://user:password@localhost:5432/arbitrage_prod
DB_ENCRYPTION=true
DB_PASS=secure_database_password

# Redis
REDIS_HOST=redis
REDIS_PASSWORD=secure_redis_password

# OpenRouter API
OPENROUTER_API_KEY=sk-or-v1-your-production-key
TOKEN_MARKUP_PERCENTAGE=25
MIN_PROFIT_MARGIN=0.10

# Logging
LOG_LEVEL=INFO
LOG_FILE=/var/log/ai-arbitrage/app.log

# Security
WEBHOOK_SECRET_TOKEN=very_secure_webhook_secret
ALLOWED_HOSTS=your-domain.com,api.your-domain.com
```

#### 3. Docker Production Setup

**docker-compose.prod.yml:**
```yaml
version: '3.8'

services:
  app:
    build: .
    container_name: ai-arbitrage-bot
    restart: unless-stopped
    ports:
      - "8000:8000"
    environment:
      - ENV_FILE=.env.production
    volumes:
      - ./logs:/var/log/ai-arbitrage
      - ./data:/app/data
    depends_on:
      - redis
      - postgres
    networks:
      - arbitrage-network

  redis:
    image: redis:7-alpine
    restart: unless-stopped
    command: redis-server --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis_data:/data
    networks:
      - arbitrage-network

  postgres:
    image: postgres:15
    restart: unless-stopped
    environment:
      POSTGRES_DB: arbitrage_prod
      POSTGRES_USER: arbitrage_user
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - arbitrage-network

  nginx:
    image: nginx:alpine
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - app
    networks:
      - arbitrage-network

volumes:
  redis_data:
  postgres_data:

networks:
  arbitrage-network:
    driver: bridge
```

#### 4. Nginx Configuration

**nginx.conf:**
```nginx
events {
    worker_connections 1024;
}

http {
    upstream bot_app {
        server app:8000;
    }

    server {
        listen 80;
        server_name your-domain.com api.your-domain.com;
        return 301 https://$server_name$request_uri;
    }

    server {
        listen 443 ssl http2;
        server_name your-domain.com api.your-domain.com;

        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;

        # Security headers
        add_header X-Content-Type-Options nosniff;
        add_header X-Frame-Options DENY;
        add_header X-XSS-Protection "1; mode=block";

        # Bot webhook
        location /webhook/ {
            proxy_pass http://bot_app;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # AI Proxy API
        location /ai-proxy/ {
            proxy_pass http://bot_app;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # Rate limiting
            limit_req zone=api burst=10 nodelay;
        }

        # Health check
        location /health {
            proxy_pass http://bot_app;
        }
    }

    # Rate limiting zones
    limit_req_zone $binary_remote_addr zone=api:10m rate=5r/s;
}
```

#### 5. Deployment Commands
```bash
# Build and start production environment
docker-compose -f docker-compose.prod.yml up -d --build

# Check logs
docker-compose logs -f app

# Database migration (if needed)
docker-compose exec app python -c "from db import create_db_and_tables; import asyncio; asyncio.run(create_db_and_tables())"

# Create initial admin packages
docker-compose exec app python -c "
from services.ai_token_service import AITokenService
import asyncio
# Add initial packages
"
```

### Monitoring and Maintenance

#### 1. Health Checks
```bash
# Check service status
docker-compose ps

# Check application health
curl https://your-domain.com/health

# Monitor logs
tail -f logs/app.log
```

#### 2. Backup Procedures
```bash
# Database backup
docker-compose exec postgres pg_dump -U arbitrage_user arbitrage_prod > backup_$(date +%Y%m%d).sql

# Redis backup
docker-compose exec redis redis-cli --rdb /data/backup_$(date +%Y%m%d).rdb
```

#### 3. Update Procedures
```bash
# Update application
git pull
docker-compose -f docker-compose.prod.yml build app
docker-compose -f docker-compose.prod.yml up -d app

# Database migrations (if needed)
docker-compose exec app python migrate.py
```

## 🔧 Development Environment

### Local Development Setup
```bash
# Clone repository
git clone <repo-url>
cd ai-arbitrage-bot

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Setup development environment
cp .env.example .env
# Edit .env with development values

# Start Redis (using Docker)
docker run -d -p 6379:6379 --name redis-dev redis:alpine

# Initialize database
python -c "from db import create_db_and_tables; import asyncio; asyncio.run(create_db_and_tables())"

# Run development server
python run.py
```

### Development Configuration
```env
# Development .env
RUNTIME_ENVIRONMENT=dev
WEBAPP_HOST=localhost
WEBAPP_PORT=5000
NGROK_TOKEN=your_ngrok_token

# Test API keys
OPENROUTER_API_KEY=sk-or-v1-test-key
TOKEN_MARKUP_PERCENTAGE=10  # Lower for testing

# Local database
DB_NAME=arbitrage_dev.db
DB_ENCRYPTION=false

# Local Redis
REDIS_HOST=localhost
REDIS_PASSWORD=

# Logging
LOG_LEVEL=DEBUG
```

## 🧪 Testing Environment

### Test Database Setup
```bash
# Create test database
python -c "
import os
os.environ['DB_NAME'] = 'test_arbitrage.db'
from db import create_db_and_tables
import asyncio
asyncio.run(create_db_and_tables())
"

# Run tests
python -m pytest tests/ -v
```

## 📊 Operational Procedures

### Daily Operations
1. **Monitor Metrics**
   - Check `/token_stats` command
   - Review profit analytics
   - Monitor OpenRouter balance

2. **Package Management**
   - Update pricing based on demand
   - Create new popular model packages
   - Remove expired/unprofitable packages

3. **Customer Support**
   - Respond to support messages via bot
   - Monitor failed transactions
   - Check API key issues

### Weekly Operations
1. **Performance Review**
   - Analyze arbitrage statistics
   - Adjust markup percentages
   - Review customer feedback

2. **System Maintenance**
   - Clean expired allocations
   - Update packages with new models
   - Backup database and logs

### Monthly Operations
1. **Business Analysis**
   - Calculate monthly profit/loss
   - Identify trending AI models
   - Plan capacity expansion

2. **Security Review**
   - Rotate API keys if needed
   - Review access logs
   - Update security configurations

### Emergency Procedures

#### High Error Rate
```bash
# Check application logs
docker-compose logs app | grep ERROR

# Check OpenRouter API status
curl -H "Authorization: Bearer $OPENROUTER_API_KEY" https://openrouter.ai/api/v1/models

# Restart services if needed
docker-compose restart app
```

#### Database Issues
```bash
# Check database connectivity
docker-compose exec postgres pg_isready

# Check database size
docker-compose exec postgres psql -U arbitrage_user -c "\l+"

# Restore from backup if needed
docker-compose exec postgres psql -U arbitrage_user arbitrage_prod < backup_latest.sql
```

#### Payment Processing Issues
```bash
# Check crypto payment status
docker-compose logs app | grep "payment"

# Manual balance adjustment if needed
# (Use admin interface for balance corrections)
```

This deployment guide provides a complete production-ready setup with monitoring, backup procedures, and operational workflows for running your AI token arbitrage business efficiently and securely.
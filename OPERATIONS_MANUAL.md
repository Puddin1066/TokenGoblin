# AI Token Arbitrage Bot - Operations Manual

## 🚀 Quick Start Guide

### 1. Initial Setup
```bash
# Clone and setup
git clone <repository>
cd ai-token-arbitrage-bot

# Copy environment configuration
cp .env.example .env

# Edit configuration with your values
nano .env
```

### 2. Required Environment Variables
```env
# Essential Configuration
TOKEN="your-telegram-bot-token"
ADMIN_ID_LIST="your-telegram-id"
OPENROUTER_API_KEY="sk-or-v1-your-openrouter-key"
WEBHOOK_SECRET_TOKEN="secure-random-string"

# Database
DB_NAME="arbitrage.db"
REDIS_HOST="localhost"
REDIS_PASSWORD="secure-redis-password"

# Arbitrage Settings
TOKEN_MARKUP_PERCENTAGE="25"
MIN_PROFIT_MARGIN="0.10"
BULK_DISCOUNT_THRESHOLD="1000000"
BULK_DISCOUNT_PERCENTAGE="5"
```

### 3. Start the System
```bash
# Development
python run.py

# Production (Docker)
docker-compose -f docker-compose.prod.yml up -d
```

## 🧪 Testing and Validation

### Running Tests
```bash
# Run comprehensive test suite
python tests/run_tests.py

# Expected output:
# ✅ Logging System: PASSED
# ✅ Mock API Functionality: PASSED
# ✅ Database Operations: PASSED
# ... (10 total tests)
# 
# Success Rate: 100.0%
```

### Test Coverage
The test suite validates:
1. **Logging System** - Structured logging and event tracking
2. **Mock API Functionality** - OpenRouter integration simulation
3. **Database Operations** - SQLite/PostgreSQL connectivity
4. **AI Token Models** - Data model validation
5. **Arbitrage Pricing Logic** - Profit calculation algorithms
6. **API Proxy Token Estimation** - Usage calculation accuracy
7. **Configuration Validation** - Environment setup verification
8. **Error Handling** - Failure scenario management
9. **Performance Metrics** - System performance monitoring
10. **Integration Workflow** - End-to-end business process

### Manual Testing Procedures

#### 1. OpenRouter API Connection
```bash
# Test API connectivity
curl -H "Authorization: Bearer $OPENROUTER_API_KEY" \
     https://openrouter.ai/api/v1/models
```

#### 2. Bot Functionality
```
1. Send /start to your bot
2. Navigate to "🤖 AI Tokens"
3. Browse available packages
4. Verify pricing calculations
5. Test purchase flow (with test balance)
```

#### 3. Admin Features
```
1. Access admin menu
2. Check "🤖 AI Token Arbitrage"
3. Review arbitrage statistics
4. Test package creation
5. Verify cleanup operations
```

## 📊 Monitoring and Analytics

### Real-time Monitoring

#### System Health Checks
```bash
# Application health
curl http://localhost:8000/health

# Database connectivity
sqlite3 arbitrage.db ".schema"

# Redis connectivity
redis-cli ping

# Log monitoring
tail -f logs/arbitrage.log | grep ERROR
```

#### Business Metrics
```bash
# Quick stats via bot
/token_stats

# Detailed analytics via admin menu:
# 📊 Arbitrage Stats → View performance metrics
```

### Log Analysis

#### Important Log Categories

**Business Events**
```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "level": "INFO",
  "business_event": true,
  "event_type": "token_package_sold",
  "package_id": 123,
  "user_id": 456,
  "model": "gpt-4",
  "tokens": 100000,
  "revenue": 3.75,
  "profit": 0.75
}
```

**Transactions**
```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "level": "INFO",
  "transaction": true,
  "type": "token_package_purchase",
  "amount": 3.75,
  "user_id": 456,
  "package_id": 123
}
```

**Arbitrage Operations**
```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "level": "INFO",
  "arbitrage": true,
  "operation": "package_sale",
  "model": "gpt-4",
  "tokens": 100000,
  "cost": 3.0,
  "sell_price": 3.75,
  "profit": 0.75,
  "margin_percent": 25.0
}
```

#### Log Queries

**Find High-Value Transactions**
```bash
grep '"amount":[5-9][0-9]*\|"amount":[0-9][0-9][0-9]' logs/arbitrage.log
```

**Monitor Error Rates**
```bash
grep '"level":"ERROR"' logs/arbitrage.log | wc -l
```

**Track API Performance**
```bash
grep '"api_call":true' logs/arbitrage.log | grep '"success":false'
```

## 💰 Business Operations

### Daily Operations

#### Morning Checklist
1. **System Health**: Check error logs from past 24h
2. **OpenRouter Balance**: Verify sufficient credit balance
3. **Popular Models**: Update packages for trending models
4. **Customer Support**: Review any support messages

```bash
# Daily health check script
curl -s http://localhost:8000/health | jq .
grep "ERROR\|CRITICAL" logs/arbitrage.log | tail -20
```

#### Revenue Monitoring
```bash
# Get daily statistics via bot admin
/token_stats

# Or via logs analysis
grep '"transaction":true' logs/arbitrage.log | \
grep "$(date +%Y-%m-%d)" | \
jq -r '.amount' | \
awk '{sum+=$1} END {print "Daily Revenue: $" sum}'
```

### Package Management

#### Creating New Packages
```bash
# Via bot admin command
/create_package gpt-4 100000 "GPT-4 Premium Access - 100k tokens"

# Via admin interface
📦 Manage Packages → ➕ Create Package
```

#### Bulk Package Creation
```json
[
  {
    "model": "gpt-4",
    "tokens": 100000,
    "description": "GPT-4 Access - 100k tokens",
    "category_id": 1,
    "subcategory_id": 1
  },
  {
    "model": "claude-3-sonnet",
    "tokens": 200000,
    "description": "Claude 3 Sonnet - 200k tokens", 
    "category_id": 1,
    "subcategory_id": 2
  }
]
```

### Pricing Optimization

#### Dynamic Pricing Adjustments
```python
# Update markup percentage
# Edit .env file:
TOKEN_MARKUP_PERCENTAGE="30"  # Increase to 30%

# Restart application
docker-compose restart app
```

#### Market Analysis
```bash
# Analyze competitor pricing
curl -H "Authorization: Bearer $OPENROUTER_API_KEY" \
     https://openrouter.ai/api/v1/models | \
     jq '.data[] | {id: .id, prompt: .pricing.prompt, completion: .pricing.completion}'
```

## 🔧 Maintenance Procedures

### Regular Maintenance

#### Weekly Tasks
1. **Database Cleanup**
```bash
# Via admin interface
🧹 Cleanup Expired → Remove inactive tokens
```

2. **Log Rotation**
```bash
# Logs auto-rotate at 50MB, but manual cleanup:
find logs/ -name "*.log.*" -mtime +30 -delete
```

3. **Performance Review**
```bash
# Check slow operations
grep '"performance":true' logs/arbitrage.log | \
grep '"execution_time":[1-9]' | \
jq '{operation: .operation, time: .execution_time}'
```

#### Monthly Tasks
1. **Database Backup**
```bash
# SQLite backup
cp arbitrage.db backup/arbitrage_$(date +%Y%m%d).db

# PostgreSQL backup (if using)
pg_dump arbitrage_prod > backup/arbitrage_$(date +%Y%m%d).sql
```

2. **Security Review**
```bash
# Check failed authentication attempts
grep '"security_event":true' logs/arbitrage.log

# Rotate API keys if needed
# Update OPENROUTER_API_KEY in .env
```

### Troubleshooting

#### Common Issues

**Issue: "Package not available"**
```bash
# Check package status
sqlite3 arbitrage.db "SELECT * FROM ai_token_packages WHERE is_available = 1;"

# Check OpenRouter connectivity
curl -H "Authorization: Bearer $OPENROUTER_API_KEY" \
     https://openrouter.ai/api/v1/models
```

**Issue: "Token validation failed"**
```bash
# Check allocation status
sqlite3 arbitrage.db "SELECT * FROM ai_token_allocations WHERE api_key LIKE 'sk-arb%';"

# Check expiry dates
sqlite3 arbitrage.db "SELECT api_key, expires_at FROM ai_token_allocations WHERE expires_at < datetime('now');"
```

**Issue: High error rate**
```bash
# Check error patterns
grep '"level":"ERROR"' logs/arbitrage.log | tail -10 | jq .

# Common causes:
# 1. OpenRouter API down
# 2. Database connection issues  
# 3. Redis connection problems
# 4. Insufficient OpenRouter balance
```

#### Emergency Procedures

**System Down**
```bash
# Quick restart
docker-compose restart app

# Check critical services
docker-compose ps
curl http://localhost:8000/health
redis-cli ping
```

**Data Recovery**
```bash
# Restore from backup
cp backup/arbitrage_latest.db arbitrage.db

# Or for PostgreSQL
psql arbitrage_prod < backup/arbitrage_latest.sql
```

**OpenRouter API Issues**
```bash
# Check API status
curl -I https://openrouter.ai/api/v1/models

# Switch to backup API (if configured)
# Update OPENROUTER_BASE_URL in .env
```

## 📈 Performance Optimization

### Scaling Strategies

#### Horizontal Scaling
```yaml
# docker-compose.scale.yml
services:
  app:
    deploy:
      replicas: 3
  
  nginx:
    # Load balancer configuration
    volumes:
      - ./nginx-lb.conf:/etc/nginx/nginx.conf
```

#### Database Optimization
```sql
-- Add indexes for performance
CREATE INDEX idx_ai_token_packages_available ON ai_token_packages(is_available);
CREATE INDEX idx_ai_token_allocations_user ON ai_token_allocations(user_id);
CREATE INDEX idx_ai_token_allocations_expires ON ai_token_allocations(expires_at);
```

### Monitoring Alerts

#### Set up monitoring alerts for:
- Error rate > 5%
- Response time > 2 seconds  
- OpenRouter balance < $10
- Daily revenue < $100
- Failed purchases > 10%

## 🔐 Security Best Practices

### API Key Management
- Rotate OpenRouter API keys monthly
- Use different keys for dev/staging/prod
- Monitor API key usage and limits

### Database Security
- Enable encryption for production
- Regular backups with encryption
- Limit database access to application only

### Infrastructure Security  
- Use HTTPS for all endpoints
- Implement rate limiting
- Regular security updates
- Monitor access logs

## 📞 Support and Escalation

### Support Levels

**Level 1: Operational Issues**
- Application restarts
- Configuration changes
- Package management
- User support

**Level 2: Technical Issues**
- Database problems
- API integration issues
- Performance optimization
- Security incidents

**Level 3: Business Critical**
- Data loss scenarios
- Major security breaches
- Extended outages
- Financial discrepancies

### Contact Information
- **Technical Support**: Check logs first, then system documentation
- **Business Issues**: Review analytics and transaction logs
- **Emergency**: Follow incident response procedures

---

This operations manual provides comprehensive guidance for running a profitable AI token arbitrage business. Regular review and updates of procedures ensure optimal performance and customer satisfaction.
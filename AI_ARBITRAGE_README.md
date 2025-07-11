# AI Token Arbitrage Bot

A sophisticated Telegram bot system that enables AI token arbitrage by purchasing tokens from OpenRouter and reselling them to customers worldwide, particularly those in regions with AI access restrictions.

## 🌍 Business Model

### The Opportunity
Many regions worldwide face restrictions accessing advanced AI models due to:
- Geographic limitations imposed by AI providers
- Payment method restrictions 
- Regulatory compliance requirements
- Lack of local support

### Our Solution
This bot operates as an AI token arbitrage system:
1. **Bulk Purchase**: Buy AI tokens at wholesale rates from OpenRouter
2. **Global Distribution**: Resell tokens to customers worldwide via Telegram
3. **Instant Access**: Provide immediate API key delivery for AI model access
4. **Profitable Margins**: Maintain sustainable markup while serving underserved markets

## ⚡ Key Features

### For Customers
- **🌍 Global Access**: Access AI models regardless of geographic location
- **💳 Crypto Payments**: Accept Bitcoin, Ethereum, and major stablecoins
- **⚡ Instant Delivery**: Receive API keys within seconds of payment
- **🔐 Anonymous Purchases**: No KYC requirements
- **📱 Easy Interface**: Simple Telegram bot interaction
- **📊 Usage Tracking**: Monitor token consumption and remaining balance

### For Operators
- **📈 Automated Arbitrage**: Dynamic pricing with configurable markup
- **🎯 Profit Tracking**: Detailed analytics and performance metrics  
- **🔧 Admin Controls**: Comprehensive management tools
- **🛡️ Security**: Token validation and usage enforcement
- **📦 Bulk Management**: Efficiently create and manage token packages
- **🔄 Auto-cleanup**: Automated maintenance of expired allocations

## 🏗️ System Architecture

### Core Components

1. **Telegram Bot Interface**
   - User registration and authentication
   - Shopping cart and purchase flow
   - Token allocation management
   - Admin controls and analytics

2. **OpenRouter Integration**
   - Real-time model pricing and availability
   - Bulk token purchasing
   - API key generation and management
   - Usage tracking and validation

3. **AI Proxy Service**
   - Token-based access control
   - Request validation and rate limiting
   - Usage consumption tracking
   - OpenRouter API proxying

4. **Database Layer**
   - User and purchase management
   - Token allocation tracking
   - Profit and analytics storage
   - Crypto payment processing

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- Redis server
- PostgreSQL/SQLite database
- OpenRouter API account
- Telegram Bot Token

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd AI-Token-Arbitrage-Bot
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure environment**
```bash
cp .env.example .env
# Edit .env with your configuration
```

4. **Essential Configuration**
```env
# Telegram Bot
TOKEN="your-telegram-bot-token"
ADMIN_ID_LIST="your-telegram-id"

# OpenRouter API
OPENROUTER_API_KEY="sk-or-v1-your-api-key"

# Pricing Configuration
TOKEN_MARKUP_PERCENTAGE="25"  # 25% markup
MIN_PROFIT_MARGIN="0.10"      # $0.10 minimum profit

# Database
DB_NAME="arbitrage.db"
REDIS_HOST="localhost"
REDIS_PASSWORD="your-redis-password"
```

5. **Start the bot**
```bash
python run.py
```

## 💰 Pricing Strategy

### Dynamic Pricing Model
- **Base Cost**: Fetched from OpenRouter real-time pricing
- **Markup**: Configurable percentage (default 25%)
- **Minimum Profit**: Ensures minimum profit per transaction
- **Bulk Discounts**: Automatic discounts for large purchases
- **Market Positioning**: Competitive rates for global accessibility

### Example Pricing
```
OpenRouter Cost: $0.003 per 1K tokens
Our Price: $0.00375 per 1K tokens (25% markup)
Profit: $0.00075 per 1K tokens
```

## 🛒 Customer Journey

### 1. Discovery & Registration
- User starts bot with `/start`
- Automatic registration with crypto wallet generation
- Introduction to AI token marketplace

### 2. Package Selection
- Browse available AI models and token packages
- Compare pricing and features
- View detailed package information

### 3. Payment & Purchase
- Add packages to cart
- Pay with cryptocurrency
- Automatic balance updates upon confirmation

### 4. Token Delivery
- Instant API key generation
- Usage instructions and documentation
- Access to proxy endpoints

### 5. Usage & Monitoring
- Use API keys with standard OpenRouter endpoints
- Monitor usage through bot interface
- Track remaining tokens and expiry

## 🔧 Admin Operations

### Package Management
```bash
# Create single package
/create_package gpt-4 100000 "GPT-4 Access - 100k tokens"

# Bulk create from JSON file
# Upload JSON file with package definitions

# Monitor packages
📦 Manage Packages → View current inventory
```

### Analytics & Monitoring
```bash
# Quick stats
/token_stats

# Detailed analytics
📊 Arbitrage Stats → View performance metrics
```

### Maintenance
```bash
# Clean expired allocations
🧹 Cleanup Expired → Remove inactive tokens

# View system health
📊 Analytics & Reports → System overview
```

## 🌐 API Proxy Usage

### For Customers
Once you purchase tokens, use your API key with our proxy:

```bash
curl -X POST https://your-domain.com/ai-proxy/v1/chat/completions \
  -H "Authorization: Bearer sk-arb-your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4",
    "messages": [{"role": "user", "content": "Hello!"}],
    "max_tokens": 100
  }'
```

### Endpoints
- **Chat Completions**: `/ai-proxy/v1/chat/completions`
- **Models List**: `/ai-proxy/v1/models`
- **Auth Check**: `/ai-proxy/v1/auth`
- **Service Info**: `/ai-proxy/`

## 📊 Business Analytics

### Key Metrics
- **Daily/Weekly/Monthly Revenue**
- **Profit Margins by Model**
- **Customer Acquisition Costs**
- **Token Utilization Rates**
- **Geographic Distribution**
- **Model Popularity**

### Performance Tracking
```python
# Get arbitrage stats
stats = await token_service.get_arbitrage_stats(30, session)
print(f"30-day profit: ${stats['total_profit']:.2f}")
print(f"Packages sold: {stats['total_packages_sold']}")
print(f"Average profit per package: ${stats['average_profit_per_package']:.2f}")
```

## 🛡️ Security & Compliance

### Security Features
- **API Key Validation**: Every request validated against database
- **Rate Limiting**: Prevent abuse and ensure fair usage
- **Token Expiry**: Automatic cleanup of expired allocations
- **Usage Tracking**: Detailed logs for audit and support
- **Admin Controls**: Comprehensive management and monitoring

### Compliance Considerations
- **No KYC Required**: Anonymous purchases via cryptocurrency
- **Data Privacy**: Minimal data collection and storage
- **Geographic Agnostic**: Service available worldwide
- **Terms of Service**: Clear usage guidelines and limitations

## 🔧 Customization

### Pricing Configuration
```python
# config.py
TOKEN_MARKUP_PERCENTAGE = 25        # 25% markup
MIN_PROFIT_MARGIN = 0.10           # $0.10 minimum
BULK_DISCOUNT_THRESHOLD = 1000000  # 1M tokens for bulk pricing
BULK_DISCOUNT_PERCENTAGE = 5       # 5% bulk discount
```

### Model Selection
```python
# Add new models to arbitrage
popular_models = [
    "gpt-4", "gpt-3.5-turbo", 
    "claude-3-sonnet", "claude-3-haiku",
    "llama-2-70b", "mixtral-8x7b"
]
```

## 📈 Scaling Strategies

### Horizontal Scaling
- **Multi-bot Support**: Run multiple bot instances
- **Load Balancing**: Distribute traffic across servers
- **Database Sharding**: Scale database for high volume

### Business Growth
- **Market Expansion**: Target specific geographic regions
- **Product Diversification**: Add more AI providers
- **Partnership Programs**: Affiliate and reseller networks
- **Enterprise Packages**: Custom solutions for businesses

## 🐛 Troubleshooting

### Common Issues

**"Package not available"**
- Check OpenRouter API connectivity
- Verify package creation was successful
- Ensure sufficient OpenRouter balance

**"Token validation failed"**
- Confirm API key format and database entry
- Check token expiry and remaining balance
- Verify user permissions and allocations

**"Proxy request failed"**
- Validate OpenRouter API key configuration
- Check network connectivity and firewall
- Review request format and parameters

## 📞 Support

### For Operators
- Review admin documentation
- Check system logs and analytics
- Use built-in diagnostic tools

### For Customers
- Telegram bot help commands
- API documentation and examples
- Support contact through bot interface

## 🚀 Future Enhancements

### Planned Features
- **Multi-provider Support**: Anthropic, Cohere, others
- **Advanced Analytics**: ML-powered demand forecasting
- **Mobile App**: Dedicated iOS/Android applications
- **Subscription Models**: Monthly/annual token packages
- **Referral Program**: Customer acquisition incentives

### Technical Improvements
- **Streaming Support**: Real-time response streaming
- **Advanced Caching**: Reduce API costs through caching
- **Auto-scaling**: Dynamic resource allocation
- **Enhanced Security**: Advanced fraud detection

---

## 🎯 Success Metrics

This AI token arbitrage system is designed to be:
- **Profitable**: Sustainable margins with volume scaling
- **Global**: Serving underserved markets worldwide  
- **Automated**: Minimal manual intervention required
- **Scalable**: Built for growth and expansion
- **Compliant**: Respects regulations and provider terms

Start your AI token arbitrage business today and provide global access to advanced AI capabilities while building a profitable, scalable operation.
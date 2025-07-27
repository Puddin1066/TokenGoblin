# AI Token Implementation - End-to-End Flow

This document describes the complete implementation of the AI token ordering system that enforces the requirements:
- **Only buy specifically requested AI tokens via OpenRouter in amounts ≤ $20**
- **Only deposit crypto received in return for the AI tokens with markup**
- **No speculative or autonomous buying**

## 🏗️ Architecture Overview

### Core Components

1. **`AITokenService`** (`services/ai_token_service.py`)
   - Handles token-based orders
   - Calculates pricing with markup
   - Enforces $20 USD cap
   - Integrates with OpenRouter API

2. **`AITokenPaymentProcessor`** (`processing/ai_token_payment_processor.py`)
   - Processes crypto payments for AI token orders
   - Triggers OpenRouter purchases after payment confirmation
   - Sends delivery notifications

3. **AI Token Handlers** (`handlers/user/ai_tokens.py`)
   - User interface for token ordering
   - Package selection and custom amounts
   - Payment flow management

4. **Updated Agentic Orchestrator** (`services/agentic_orchestrator.py`)
   - **DISABLED** all speculative/autonomous buying
   - Only allows user-initiated purchases

## 🔄 Complete Flow

### 1. User Request Flow
```
User → "🤖 AI Tokens" → Select Package/Custom Amount → View Pricing → Confirm Order
```

### 2. Pricing Calculation
```
Token Count → OpenRouter Pricing → Apply 20% Markup → Check $20 Cap → Convert to Crypto
```

### 3. Payment Flow
```
User Payment → Crypto Payment Service → Payment Confirmation → Token Purchase → Delivery
```

## 📋 Implementation Details

### Token-Based Orders
- Users specify **number of tokens** (not USD amount)
- System calculates USD cost from OpenRouter pricing
- Applies 20% markup
- Converts to crypto for payment

### $20 USD Cap Enforcement
```python
# In AITokenService.calculate_token_order_price()
if total_usd_cost > self.max_usd_order_value:  # $20
    raise ValueError(f"Order value ${total_usd_cost:.2f} exceeds $20 limit")
```

### No Speculative Buying
```python
# In AgenticOrchestrator
self.agentic_operations_enabled = False
self.min_inventory_threshold = 0  # No inventory maintenance
self.max_purchase_budget = 0  # No autonomous purchases
```

### Payment-Triggered Purchases
- Tokens are **only** purchased from OpenRouter after crypto payment is confirmed
- No advance purchasing or inventory management
- Each purchase is tied to a specific user order

## 🛠️ Key Features

### Token Packages
- **Starter**: 1,000 tokens
- **Standard**: 5,000 tokens  
- **Professional**: 10,000 tokens
- **Enterprise**: 20,000 tokens (maximum allowed)

### Pricing Structure
- **Base Cost**: OpenRouter pricing for requested tokens
- **Markup**: 20% on base cost
- **Payment**: USDT TRC20 or BTC
- **Cap**: Maximum $20 USD per order

### Validation Rules
- Minimum: 100 tokens
- Maximum: Based on $20 USD limit
- Payment: Exact crypto amount required
- Network: TRC20 for USDT, mainnet for BTC

## 🔧 Configuration

### Environment Variables
```bash
OPENROUTER_API_KEY=your_openrouter_api_key
KRYPTO_EXPRESS_API_KEY=your_krypto_express_key
KRYPTO_EXPRESS_API_URL=https://kryptoexpress.pro/api
```

### Service Configuration
```python
# In AITokenService
self.max_usd_order_value = 20.0  # $20 cap
self.markup_percentage = 0.20    # 20% markup
self.default_model = 'anthropic/claude-3-sonnet'
```

## 🧪 Testing

Run the test script to verify the implementation:

```bash
python test_ai_token_flow.py
```

This will test:
- Token pricing calculation
- Order validation
- Package availability
- Payment processing
- Complete end-to-end flow

## 📊 Database Schema (Future Implementation)

```sql
CREATE TABLE ai_token_orders (
    order_id VARCHAR(50) PRIMARY KEY,
    user_id INTEGER NOT NULL,
    token_count INTEGER NOT NULL,
    model_id VARCHAR(100) NOT NULL,
    base_usd_cost DECIMAL(10,2) NOT NULL,
    markup_amount DECIMAL(10,2) NOT NULL,
    total_usd_cost DECIMAL(10,2) NOT NULL,
    crypto_type VARCHAR(20) NOT NULL,
    crypto_amount DECIMAL(20,8) NOT NULL,
    payment_id VARCHAR(50) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 🚀 Deployment

### 1. Update Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
cp .env.example .env
# Edit .env with your API keys
```

### 3. Start the Bot
```bash
python run.py
```

## 🔒 Security Features

### Payment Validation
- Exact amount matching required
- Crypto type validation
- Order status verification
- Transaction hash tracking

### Error Handling
- Payment timeout handling
- Failed purchase recovery
- User notification system
- Admin alert system

## 📈 Monitoring

### Key Metrics
- Orders per day
- Payment success rate
- Token delivery success rate
- Revenue per order
- Average order value

### Logging
```python
logger.info(f"Processing AI token payment: {payment_id} for user {user_id}")
logger.error(f"Payment amount mismatch: {amount_usd} vs {order_details['total_usd_cost']}")
```

## 🔄 Future Enhancements

### Planned Features
1. **Database Integration**: Full order tracking and history
2. **Multiple Models**: Support for different AI models
3. **Regional Pricing**: Location-based pricing adjustments
4. **Bulk Orders**: Support for larger token packages
5. **Subscription Model**: Recurring token purchases

### Scalability Considerations
- Redis caching for exchange rates
- Database connection pooling
- Async payment processing
- Horizontal scaling support

## ✅ Compliance Checklist

- [x] **Token-based orders only**
- [x] **$20 USD cap enforced**
- [x] **20% markup applied**
- [x] **No speculative buying**
- [x] **Payment-triggered purchases only**
- [x] **OpenRouter integration**
- [x] **Crypto payment support**
- [x] **User notification system**
- [x] **Admin monitoring**
- [x] **Error handling**
- [x] **Security validation**

## 🆘 Troubleshooting

### Common Issues

1. **OpenRouter API Errors**
   - Check API key configuration
   - Verify network connectivity
   - Check rate limits

2. **Payment Processing Errors**
   - Verify crypto payment service configuration
   - Check blockchain network status
   - Validate payment amounts

3. **Pricing Calculation Errors**
   - Check OpenRouter pricing API
   - Verify exchange rate service
   - Validate markup configuration

### Debug Mode
```python
logging.basicConfig(level=logging.DEBUG)
```

## 📞 Support

For issues or questions:
1. Check the logs for error details
2. Verify configuration settings
3. Test with the provided test script
4. Contact development team with specific error messages 
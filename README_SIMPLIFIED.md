# Simplified Token Resale Platform

## 🚀 Overview

This project has been **transformed from a complex marketplace** into a **streamlined token resale platform**. Users can now purchase popular cryptocurrencies with fiat or crypto payments and receive tokens directly in their wallets.

## ✨ Key Features

- **🪙 Instant Token Delivery** - Tokens sent directly to user's wallet
- **💰 Real-time Pricing** - Live market prices via CoinGecko API
- **🔄 Multiple Payment Methods** - Fiat (credit card) and cryptocurrency
- **📊 Transaction Tracking** - Complete order history and status updates
- **🛡️ Address Validation** - Prevents sending to invalid addresses
- **⚡ Simplified UX** - Clean, focused user interface

## 🏗️ Simplified Architecture

### Before (Complex Marketplace)
```
Multi-chain Deposits → Platform Credits → Shopping Cart → Physical Items → Manual Withdrawals
```

### After (Token Resale Platform)  
```
Payment → Token Purchase (DEX/CEX) → Direct Wallet Transfer
```

## 🔧 Core Components

### Services
- **`TokenResaleService`** - Main business logic
- **`SimplifiedAdminService`** - Admin panel functionality

### Models & Database
- **`Transaction`** - Single table for all orders
- **`TransactionStatus`** - Order status tracking
- **`TransactionRepository`** - Database operations

### User Interface
- **`TokenPurchaseHandler`** - User interaction handlers
- **Simplified Bot Commands** - Buy tokens, view orders

## 🎯 User Flow

1. **Start** - User opens bot, sees welcome screen
2. **Browse** - Click "🪙 Buy Tokens" to see available tokens
3. **Select** - Choose token (BTC, ETH, USDT, USDC, BNB)
4. **Amount** - Enter USD amount to spend ($10-$10,000)
5. **Address** - Provide wallet address for token delivery
6. **Review** - Confirm order details and fees
7. **Pay** - Choose payment method (fiat/crypto)
8. **Receive** - Tokens delivered directly to wallet

## 🛠️ Admin Features

- **📊 Transaction Statistics** - Monitor order volume and status
- **⏳ Pending Orders** - View orders awaiting processing
- **💰 Platform Balance** - Check token inventory and prices
- **🔄 Price Refresh** - Update market rates
- **📈 Daily Summary** - Business analytics

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
cp config.py.example config.py
# Edit config.py with your API keys
```

### 3. Set Up Database
```bash
python -c "from db import create_db_and_tables; import asyncio; asyncio.run(create_db_and_tables())"
```

### 4. Run Bot
```bash
python run.py
```

## 📝 Configuration

### Required API Keys
- **Telegram Bot Token** - Create bot via @BotFather
- **CoinGecko API** - For real-time token prices (free tier available)
- **Payment Processor** - Stripe/PayPal for fiat payments
- **Blockchain Providers** - Infura/Alchemy for token transfers

### Supported Tokens
- **BTC** - Bitcoin
- **ETH** - Ethereum  
- **USDT** - Tether (ERC-20)
- **USDC** - USD Coin (ERC-20)
- **BNB** - Binance Coin

## 🔌 Integration Points

### DEX/CEX Integration (Production)
```python
# Uniswap V3 for decentralized trading
await uniswap_v3.swap_exact_input(usdc_amount, target_token)

# Binance API for centralized trading  
await binance_api.market_buy(token_symbol, usdc_amount)
```

### Blockchain Integration (Production)
```python
# Web3 for Ethereum/ERC-20 transfers
await web3.eth.send_transaction({
    'to': recipient_address,
    'value': token_amount
})

# Bitcoin RPC for Bitcoin transfers
await bitcoin_rpc.send_to_address(address, amount)
```

## 📊 Database Schema

### Transactions Table
```sql
CREATE TABLE transactions (
    id INTEGER PRIMARY KEY,
    user_telegram_id INTEGER NOT NULL,
    payment_method VARCHAR(20) NOT NULL,
    payment_amount FLOAT NOT NULL,
    payment_currency VARCHAR(10) NOT NULL,
    token_symbol VARCHAR(10) NOT NULL,
    token_amount FLOAT NOT NULL,
    recipient_address VARCHAR(100) NOT NULL,
    status ENUM('pending_payment', 'processing', 'completed', 'failed', 'refunded'),
    fees FLOAT NOT NULL,
    tx_hash VARCHAR(100),
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

## 🔒 Security Features

- **Address Validation** - Regex validation for all supported networks
- **Amount Limits** - Min $10, Max $10,000 per transaction
- **Rate Limiting** - Prevents spam and abuse
- **Error Handling** - Graceful failure with user feedback
- **Transaction Monitoring** - Complete audit trail

## 💡 Future Enhancements

### Short Term
- **Payment Gateway Integration** - Stripe, PayPal, crypto processors
- **Real DEX Integration** - Uniswap, PancakeSwap APIs
- **Gas Optimization** - Dynamic fee calculation
- **Multi-language Support** - Localization system

### Long Term  
- **DeFi Yield Farming** - Automated liquidity provision
- **NFT Marketplace** - Expand beyond tokens
- **Staking Services** - Earn rewards on held tokens
- **Mobile App** - React Native companion app

## 📈 Benefits Over Previous System

| Aspect | Old Marketplace | New Token Platform |
|--------|----------------|-------------------|
| **Complexity** | 15+ files, 1000+ lines | 5 files, 300 lines |
| **User Flow** | 5+ steps, complex | 3 steps, simple |
| **Settlement** | Manual admin process | Instant on-chain |
| **Custody Risk** | High (stored funds) | Minimal (flow-through) |
| **Maintenance** | High complexity | Low complexity |
| **Scalability** | Limited by inventory | Unlimited (DEX liquidity) |

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Support

- **Telegram**: [@your_support_bot](https://t.me/your_support_bot)
- **Email**: support@tokenresale.example
- **Documentation**: [Wiki](https://github.com/your-repo/wiki)

---

**Built with ❤️ for the decentralized future**
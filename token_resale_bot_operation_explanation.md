# Token Resale Bot Operation Explanation

## Overview

The "AiogramShopBot" is a sophisticated digital goods marketplace bot that operates via Telegram. Despite the name suggesting "token resale," this bot actually manages the sale of digital goods/items (which could be considered "tokens") rather than cryptocurrency tokens. The bot accepts multiple cryptocurrency payments and automates the entire sales process.

## Core Architecture

### 1. **Tech Stack**
- **Framework**: Aiogram 3 (Python Telegram Bot framework)
- **Database**: SQLite with optional SQLCipher encryption
- **Payment Processing**: Multiple cryptocurrency APIs + KryptoExpress integration
- **Web Framework**: FastAPI for webhook handling
- **Storage**: Redis for session management and throttling
- **Deployment**: Docker with optional Caddy reverse proxy

### 2. **Key Components**

#### A. **Bot Core** (`bot.py`, `run.py`)
- **FastAPI Application**: Handles Telegram webhooks and payment processing callbacks
- **Aiogram Dispatcher**: Routes messages and callback queries to appropriate handlers
- **Error Handling**: Comprehensive error tracking with admin notifications
- **Startup/Shutdown**: Webhook management and admin notifications

#### B. **User Management System** (`services/user.py`, `models/user.py`)
- **User Registration**: Automatic on first `/start` command
- **Wallet Generation**: Each user gets unique crypto addresses for multiple currencies
- **Balance Tracking**: 
  - `top_up_amount`: Total deposited funds
  - `consume_records`: Total spent funds
  - Available balance = `top_up_amount - consume_records`

#### C. **Cryptocurrency Payment System**

##### Payment Processing (`crypto_api/CryptoApiManager.py`)
- **Supported Cryptocurrencies**: BTC, LTC, SOL, USDT (TRC20/ERC20), USDC (ERC20)
- **Address Generation**: Uses HD wallet derivation for unique addresses per user
- **Balance Monitoring**: Polls blockchain APIs to detect new deposits
- **APIs Used**:
  - **Bitcoin**: mempool.space API
  - **Litecoin**: BlockCypher API
  - **Solana**: Solana.fm API
  - **Tron (USDT TRC20)**: TronGrid API
  - **Ethereum (USDT/USDC ERC20)**: Ethplorer API

##### KryptoExpress Integration (`processing/processing.py`)
- **Alternative Payment Processor**: Handles payment requests via external service
- **Webhook Processing**: Receives payment confirmations securely
- **HMAC Security**: Validates incoming webhook signatures
- **Payment States**: Tracks pending, paid, and expired payments

## 3. **Core Workflows**

### A. **User Registration & Wallet Setup**

```
1. User sends /start command
2. Bot creates user record with unique Telegram ID
3. System generates unique crypto addresses for each supported currency
4. User gets access to main menu with shop categories
5. Cart is initialized for the user
```

### B. **Inventory Management** (`services/item.py`)

#### Item Structure
- **Categories**: Top-level organization (e.g., "Gaming", "Software")
- **Subcategories**: Second-level organization (e.g., "Steam Games", "Adobe Tools")
- **Items**: Individual digital goods with:
  - `private_data`: The actual content delivered to buyer
  - `price`: Cost in fiat currency
  - `description`: Public description
  - `is_sold`: Sale status flag
  - `is_new`: New item flag for announcements

#### Admin Functions
- **Bulk Import**: JSON/TXT file upload for inventory
- **Category Management**: Create/delete categories and subcategories
- **Stock Monitoring**: Real-time inventory tracking
- **Pricing**: Dynamic pricing per item

### C. **Shopping & Cart System** (`services/cart.py`)

#### Cart Management
```
1. User browses categories → subcategories → items
2. User selects quantity and adds to cart
3. Cart stores: category_id, subcategory_id, quantity
4. Real-time price calculation and stock validation
5. Cart persists between sessions
```

#### Purchase Flow
```
1. User reviews cart with total price
2. System validates:
   - Sufficient balance
   - Item availability
   - Stock quantities
3. On confirmation:
   - Items marked as sold
   - User balance decremented
   - Purchase history created
   - Items delivered via private message
   - Cart cleared
```

### D. **Payment Processing Workflow**

#### Traditional Crypto Payments
```
1. User selects cryptocurrency in "Top Up Balance"
2. System generates unique payment request
3. User sends crypto to provided address
4. CryptoApiManager polls blockchain APIs
5. On confirmed transaction:
   - User balance updated
   - Deposit record created
   - Admin notification sent
   - User notification sent
```

#### KryptoExpress Payments
```
1. User initiates payment via KryptoExpress
2. System creates payment request with API
3. User completes payment externally
4. KryptoExpress sends webhook to bot
5. Bot validates HMAC signature
6. Payment marked as complete
7. User balance updated
```

### E. **Admin Management System** (`services/admin.py`)

#### Core Admin Functions
- **User Management**: Balance adjustments, refunds, user lookup
- **Inventory Control**: Add/remove items, category management
- **Analytics**: Sales reports, user statistics, deposit tracking
- **Announcements**: Broadcast messages, restocking alerts
- **System Monitoring**: Database backups, error tracking

#### Notification System
- **New Purchase Alerts**: Real-time sale notifications
- **Deposit Confirmations**: Payment processing updates
- **System Errors**: Critical error reporting with stack traces
- **Refund Processing**: Automated refund confirmations

## 4. **Advanced Features**

### A. **Multibot Support** (`multibot.py`)
- **Manager Bot**: Controls multiple child bots
- **Dynamic Bot Creation**: Add new bots via `/add TOKEN` command
- **Shared Infrastructure**: Common database and services
- **Independent Operation**: Each bot operates independently

### B. **Security Features**
- **Database Encryption**: Optional SQLCipher encryption
- **HMAC Verification**: Secure webhook validation
- **Rate Limiting**: Redis-based throttling
- **Admin Authentication**: ID-based access control
- **Input Validation**: Comprehensive data sanitization

### C. **Internationalization**
- **Multi-language Support**: JSON-based localization
- **Currency Support**: Multiple fiat currencies (USD, EUR, GBP, etc.)
- **Dynamic Text**: Runtime language switching

## 5. **Database Schema**

### Core Tables
- **users**: User accounts and balances
- **categories/subcategories**: Product organization
- **items**: Individual digital goods
- **cart/cart_items**: Shopping cart system
- **buys/buy_items**: Purchase history
- **deposits**: Cryptocurrency deposit tracking
- **payments**: Payment processing records

### Relationships
```
User → Cart → CartItems
User → Buys → BuyItems → Items
User → Deposits
User → Payments
Categories → Subcategories → Items
```

## 6. **Revenue Model**

The bot operates as a digital marketplace where:
1. **Admins** upload digital goods (software keys, accounts, etc.)
2. **Users** purchase items with cryptocurrency
3. **Automatic Delivery** via private messages
4. **No Transaction Fees** - direct peer-to-peer sales
5. **Instant Settlement** - no payment processing delays

## 7. **Deployment & Scaling**

### Development Mode
- **ngrok Integration**: Automatic tunnel setup for webhooks
- **Local Development**: SQLite with optional encryption
- **Hot Reload**: FastAPI development server

### Production Mode
- **Docker Deployment**: Containerized application
- **Caddy Reverse Proxy**: Automatic HTTPS certificates
- **Redis Caching**: Session management and rate limiting
- **Health Monitoring**: Automatic admin notifications

## 8. **Use Cases**

This bot is ideal for:
- **Digital Product Sales**: Software licenses, game keys, accounts
- **Cryptocurrency Commerce**: Direct crypto-to-goods transactions
- **Automated Marketplaces**: Minimal manual intervention required
- **Multi-vendor Platforms**: Support for multiple bot instances
- **Global Sales**: Cryptocurrency removes geographic limitations

## Conclusion

The "token resale bot" is actually a comprehensive digital goods marketplace that leverages cryptocurrency payments for automated, global commerce. Its architecture supports high-volume transactions with minimal manual intervention, making it suitable for various digital commerce applications.

The system's strength lies in its automation - from payment processing to inventory management to customer delivery - creating a seamless experience for both buyers and sellers in the digital goods market.
# AiogramShopBot Repository Analysis

## Overview

**AiogramShopBot** is a sophisticated Telegram bot designed for automated sales of digital goods with cryptocurrency payment integration. Built on **Aiogram 3** and **SQLAlchemy**, it supports multiple cryptocurrencies including Bitcoin (BTC), Litecoin (LTC), Solana (SOL), and stablecoins in TRC20 and ERC20 networks.

## Architecture Overview

### Core Technologies
- **Backend Framework**: Aiogram 3 (Python Telegram Bot framework)
- **Database**: SQLite with optional SQLCipher encryption
- **ORM**: SQLAlchemy 2.0 (async support)
- **Web Framework**: FastAPI for webhook handling
- **Caching/Storage**: Redis for session storage and throttling
- **Deployment**: Docker with Docker Compose

### Key Components

#### 1. **Entry Points**
- `run.py`: Main application entry point
- `bot.py`: Bot configuration and FastAPI webhook setup
- `multibot.py`: Experimental multi-bot management system

#### 2. **Configuration Management**
- `config.py`: Environment variable loading and validation
- `.env`: Environment configuration file
- Supports development (ngrok) and production (Caddy reverse proxy) modes

#### 3. **Database Layer**
- `db.py`: Database connection and session management
- `models/`: SQLAlchemy model definitions
- Supports both regular SQLite and encrypted SQLCipher databases

#### 4. **Handler System**
Organized into three main categories:
- `handlers/user/`: User-facing bot commands (catalog, profile, cart)
- `handlers/admin/`: Administrative functions (inventory, analytics, user management)
- `handlers/common/`: Shared functionality

#### 5. **Business Logic Services**
- `services/`: Core business logic implementation
- `processing/`: Payment processing and webhook handling
- `crypto_api/`: Cryptocurrency API integration

#### 6. **Middleware System**
- `middleware/database.py`: Database session management
- `middleware/throttling_middleware.py`: Rate limiting and anti-spam

## Core Functionality

### User Features
1. **Registration**: Automatic user creation with unique mnemonic phrases for crypto address generation
2. **Product Catalog**: Hierarchical browsing (Categories → Subcategories → Products)
3. **Shopping Cart**: Add/remove items before purchase
4. **Cryptocurrency Payments**: Support for BTC, LTC, SOL, USDT (TRC20/ERC20)
5. **Purchase History**: Track all previous purchases
6. **Balance Management**: Top-up via cryptocurrency deposits

### Admin Features
1. **Inventory Management**: Add/remove products via JSON or TXT file upload
2. **User Management**: Add/reduce user balances, process refunds
3. **Analytics**: Sales statistics, user metrics, deposit tracking
4. **Announcements**: Broadcast messages to all users
5. **Database Backup**: Export database files
6. **Real-time Notifications**: New purchase and deposit alerts

### Payment Processing
- **Address Generation**: Unique crypto addresses per user using BIP-84 (BTC/LTC) and BIP-44 (USDT TRC20)
- **Balance Tracking**: Automatic balance updates on confirmed transactions
- **Multi-currency Support**: Handles various cryptocurrencies and stablecoins
- **External API Integration**: Uses KryptoExpress for payment processing

## Database Schema

### Key Models
- **User**: User profiles with crypto addresses and balances
- **Item**: Product catalog with categories, pricing, and inventory
- **Cart/CartItem**: Shopping cart functionality
- **Buy/BuyItem**: Purchase history and transaction records
- **Deposit**: Cryptocurrency deposit tracking
- **Category/Subcategory**: Product organization hierarchy

### Database Features
- **Encryption**: Optional SQLCipher encryption for sensitive data
- **Relationships**: Proper foreign key constraints and relationships
- **Async Support**: Full async/await support for database operations

## Deployment Architecture

### Development Mode
- Uses ngrok for local development tunneling
- Automatic HTTPS certificate handling
- Environment variable: `RUNTIME_ENVIRONMENT=dev`

### Production Mode
- Caddy reverse proxy with automatic TLS
- Docker Compose orchestration
- Redis for session management and throttling
- Environment variable: `RUNTIME_ENVIRONMENT=prod`

### Container Services
1. **Bot Service**: Main application container
2. **Redis Service**: Session storage and caching
3. **Caddy Service**: Reverse proxy with automatic HTTPS

## Security Features

### Data Protection
- **Database Encryption**: Optional SQLCipher encryption
- **Webhook Security**: Secret token validation for Telegram webhooks
- **Admin Authentication**: Multi-admin support with ID-based access control
- **Rate Limiting**: Redis-based throttling middleware

### Cryptocurrency Security
- **HD Wallets**: Hierarchical deterministic wallet generation
- **Unique Addresses**: One mnemonic phrase per user
- **Transaction Validation**: Confirmation requirements before balance updates

## Internationalization
- **Localization Support**: `l10n/` directory for language files
- **Multi-language**: Currently supports English and German
- **Extensible**: Easy to add new languages via JSON configuration

## Advanced Features

### Multibot System (Experimental)
- **Multiple Bots**: Manage multiple bot instances from one deployment
- **Dynamic Bot Addition**: Add new bots via `/add $BOT_TOKEN` command
- **Shared Infrastructure**: Common database and services

### File Upload System
- **Product Import**: Support for JSON and TXT file formats
- **Bulk Operations**: Mass product additions and updates
- **Flexible Schema**: Category-based product organization

### Analytics Dashboard
- **Sales Metrics**: Revenue tracking by time periods
- **User Analytics**: Registration and activity statistics
- **Deposit Tracking**: Cryptocurrency deposit monitoring
- **Export Capabilities**: Database backup and export features

## API Integration

### External Services
- **KryptoExpress**: Payment processing API
- **Ethplorer**: ERC20 token balance checking
- **Cryptocurrency APIs**: Real-time balance and transaction monitoring

### Webhook System
- **Telegram Webhooks**: Secure webhook processing with FastAPI
- **Payment Callbacks**: Cryptocurrency payment confirmations
- **Error Handling**: Comprehensive error reporting to administrators

## Development Workflow

### Project Structure
```
├── handlers/          # Bot command handlers
├── models/           # Database models
├── services/         # Business logic
├── middleware/       # Request middleware
├── crypto_api/       # Cryptocurrency integration
├── processing/       # Payment processing
├── l10n/            # Localization files
├── utils/           # Utility functions
└── enums/           # Enum definitions
```

### Key Design Patterns
- **Router-based Architecture**: Modular command handling
- **Service Layer Pattern**: Business logic separation
- **Repository Pattern**: Data access abstraction
- **Middleware Pattern**: Request/response processing

## Configuration Management

### Environment Variables
The system requires 20+ environment variables covering:
- **Bot Configuration**: Token, admin IDs, webhook settings
- **Database Settings**: Encryption, connection parameters
- **Payment Integration**: API keys and URLs
- **Deployment**: Runtime environment, networking

### Flexible Deployment
- **Docker Support**: Full containerization with docker-compose
- **Local Development**: Easy setup with ngrok integration
- **Production Ready**: Caddy reverse proxy with automatic TLS

## Monitoring and Logging

### Error Handling
- **Global Exception Handling**: Comprehensive error catching
- **Admin Notifications**: Real-time error reporting to administrators
- **Stack Trace Logging**: Detailed error information

### Performance Monitoring
- **Redis Metrics**: Session and cache performance
- **Database Monitoring**: Query performance and connection pooling
- **Webhook Analytics**: Processing time and success rates

This repository represents a production-ready e-commerce bot with enterprise-level features including cryptocurrency payments, admin management, analytics, and robust security measures.
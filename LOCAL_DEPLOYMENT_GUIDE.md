# TokenGoblin Local Deployment Guide

## Overview
TokenGoblin is a Telegram bot for selling digital goods with cryptocurrency payment support. This guide will help you deploy it locally.

## Prerequisites

1. **Python 3.12+**
2. **Redis Server**
3. **Telegram Bot Token** (get from @BotFather)
4. **Optional: Ngrok** (for webhook testing)

## Step 1: Environment Setup

Create a `.env` file in the root directory with the following variables:

```bash
# Bot Configuration
TOKEN=your_telegram_bot_token_here
ADMIN_ID_LIST=123456789,987654321
SUPPORT_LINK=https://t.me/your_username

# Database Configuration
DB_NAME=database.db
DB_ENCRYPTION=false
DB_PASS=

# Webhook Configuration
WEBHOOK_PATH=/
WEBAPP_HOST=localhost
WEBAPP_PORT=5000
WEBHOOK_SECRET_TOKEN=your_secret_token_here

# Redis Configuration
REDIS_HOST=localhost
REDIS_PASSWORD=your_redis_password_here

# Development Configuration
NGROK_TOKEN=your_ngrok_token_here
PAGE_ENTRIES=8
BOT_LANGUAGE=en
MULTIBOT=false
CURRENCY=USD
RUNTIME_ENVIRONMENT=dev

# Crypto Payment Configuration
KRYPTO_EXPRESS_API_KEY=your_krypto_express_api_key_here
KRYPTO_EXPRESS_API_URL=https://kryptoexpress.pro/api
KRYPTO_EXPRESS_API_SECRET=your_krypto_express_secret_here

# Optional: Agentic Mode (AI features)
AGENTIC_MODE=false
OPENROUTER_API_KEY=
ANTHROPIC_API_KEY=

# Optional: ETHPlorer for ERC20 tokens
ETHPLORER_API_KEY=
```

## Step 2: Install Dependencies

```bash
# Install Python dependencies
pip install -r requirements.txt

# If you want to use database encryption (Linux only)
pip install sqlcipher3
```

## Step 3: Start Redis

### Option A: Using Docker
```bash
docker run -d --name redis -p 6379:6379 redis:latest redis-server --requirepass your_redis_password_here
```

### Option B: Install Redis locally
```bash
# macOS
brew install redis
brew services start redis

# Ubuntu/Debian
sudo apt-get install redis-server
sudo systemctl start redis-server
```

## Step 4: Get Telegram Bot Token

1. Open Telegram and search for @BotFather
2. Send `/newbot`
3. Follow the instructions to create your bot
4. Copy the token and add it to your `.env` file

## Step 5: Configure Admin Access

1. Get your Telegram ID by messaging @userinfobot
2. Add your ID to the `ADMIN_ID_LIST` in `.env`
3. Add other admin IDs separated by commas

## Step 6: Run the Bot

### Development Mode (with Ngrok)
```bash
# Install ngrok if you haven't
# Download from https://ngrok.com/download

# Start ngrok tunnel
ngrok http 5000

# Copy the HTTPS URL and update your bot webhook
# Then run the bot
python run.py
```

### Production Mode (direct webhook)
```bash
# Set RUNTIME_ENVIRONMENT=prod in .env
python run.py
```

## Step 7: Test the Bot

1. Find your bot on Telegram
2. Send `/start`
3. You should see the main menu with categories, profile, etc.

## Docker Deployment (Alternative)

If you prefer using Docker:

```bash
# Build and run with docker-compose
docker-compose up --build
```

## Key Features to Test

### User Features:
- **Registration**: Send `/start` to register
- **Browse Categories**: Navigate through product categories
- **Add to Cart**: Add items to shopping cart
- **Purchase**: Complete purchases with crypto payments
- **Profile**: View purchase history and balance

### Admin Features:
- **Inventory Management**: Add/edit products
- **User Management**: View and manage users
- **Analytics**: View sales statistics
- **Announcements**: Send messages to all users

## Troubleshooting

### Common Issues:

1. **Redis Connection Error**
   - Ensure Redis is running
   - Check Redis password in `.env`

2. **Webhook Error**
   - Verify bot token is correct
   - Check webhook URL is accessible
   - Ensure HTTPS is used for webhooks

3. **Database Error**
   - Check file permissions for database directory
   - Ensure SQLite is properly installed

4. **Crypto Payment Issues**
   - Verify KryptoExpress API credentials
   - Check network connectivity

## Development Tips

1. **Logs**: Check console output for detailed error messages
2. **Database**: The SQLite database will be created automatically
3. **Hot Reload**: The bot supports hot reloading during development
4. **Testing**: Use testnet cryptocurrencies for testing payments

## Next Steps

1. **Add Products**: Use admin panel to add digital goods
2. **Configure Payments**: Set up crypto payment providers
3. **Customize**: Modify language files in `l10n/` directory
4. **Scale**: Consider using PostgreSQL for production

## Support

- Check the main README.md for detailed documentation
- Review the code structure in `handlers/` and `services/` directories
- Test all features thoroughly before going live 
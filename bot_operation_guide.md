# Bot Operation Guide - Token Resale Platform

## 🤖 How the Bot Operates

The transformed bot operates as a **streamlined token resale platform** with a simple, focused architecture designed for instant cryptocurrency purchases and direct wallet delivery.

## 🚀 Bot Startup & Architecture

### 1. **Initialization Process** (`bot.py`)
```python
# Bot components initialization
redis = Redis(host=config.REDIS_HOST, password=config.REDIS_PASSWORD)
bot = Bot(config.TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=RedisStorage(redis))
app = FastAPI()  # Web server for webhooks
```

### 2. **Startup Sequence**
1. **Database initialization** - Creates transaction tables
2. **Webhook setup** - Registers Telegram webhook URL
3. **Admin notification** - Alerts admins that bot is online
4. **Router registration** - Sets up command and callback handlers

### 3. **Core Components**
- **FastAPI server** - Handles Telegram webhooks
- **Redis storage** - Manages user session states
- **SQLite/PostgreSQL** - Stores transaction records
- **Aiogram dispatcher** - Routes messages and callbacks

## 🎯 User Interaction Flow

### **Step 1: Bot Start** (`/start` command)
```
User sends: /start
Bot responds with:
┌─────────────────────────────────────────┐
│ 🪙 Welcome to Token Resale Platform!   │
│                                         │
│ ✅ Buy popular tokens instantly         │
│ ✅ Direct delivery to your wallet       │
│ ✅ Real-time market prices              │
│ ✅ Secure & fast transactions           │
│                                         │
│ [🪙 Buy Tokens] [📊 My Orders]         │
│ [❓ FAQ] [🆘 Help]                      │
└─────────────────────────────────────────┘
```

**Backend Process:**
- Creates user record if first time
- Shows simplified main menu
- Conditionally shows admin menu for authorized users

### **Step 2: Token Selection** (`🪙 Buy Tokens`)
```python
# Handler: @main_router.message(F.text == "🪙 Buy Tokens")
async def buy_tokens(message: types.Message):
    await TokenPurchaseHandler.show_token_menu(message, None)
```

**Bot displays:**
```
🪙 Token Purchase Platform

Select a token to purchase:
✅ Instant delivery to your wallet
✅ Real-time market prices  
✅ 2% service fee + gas costs

[BTC - $43,250.00]
[ETH - $2,650.00]
[USDT - $1.00]
[USDC - $1.00]
[BNB - $315.00]
```

**Backend Process:**
- Fetches live prices from CoinGecko API
- Displays supported tokens with current rates
- Creates inline keyboard with callback data

### **Step 3: Amount Entry** (User clicks token)
```python
# Handler: @main_router.callback_query(F.data.startswith("select_token:"))
async def handle_token_selection(callback: types.CallbackQuery):
    await TokenPurchaseHandler.select_token(callback, None)
```

**Bot displays:**
```
💰 Purchase BTC

Current price: $43,250.00

Enter the amount you want to spend (in USD):
Example: 100 (for $100 worth of tokens)

⚠️ Minimum: $10
⚠️ Maximum: $10,000

[❌ Cancel]
```

**Backend Process:**
- Stores selected token in user session state
- Sets FSM state to `entering_amount`
- Waits for user text input

### **Step 4: Address Input** (User enters amount)
```python
# Handler: TokenPurchaseHandler.enter_amount()
# Triggered by: User types "100"
```

**Bot displays:**
```
📍 Wallet Address

Enter your BTC wallet address where you want to receive the tokens:

⚠️ Make sure the address is correct!
⚠️ We cannot recover tokens sent to wrong addresses

[❌ Cancel]
```

**Backend Process:**
- Validates amount ($10-$10,000 range)
- Stores amount in session state
- Sets FSM state to `entering_address`

### **Step 5: Order Confirmation** (User enters address)
```python
# Handler: TokenPurchaseHandler.enter_address()
# Triggered by: User types "bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh"
```

**Bot displays:**
```
📋 Order Summary

Token: BTC
Payment: $100.00 USD
Token Amount: 0.002312 BTC
Service Fee: $2.00
Recipient: bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh

✅ Confirm to proceed with payment

[✅ Confirm Order] [❌ Cancel]
```

**Backend Process:**
- Validates address format using regex
- Calculates token amount after fees
- Shows complete order summary
- Sets FSM state to `confirming_order`

### **Step 6: Payment Selection** (User confirms order)
```python
# Handler: @main_router.callback_query(F.data == "confirm_order")
async def handle_order_confirmation(callback: types.CallbackQuery):
    await TokenPurchaseHandler.confirm_order(callback, None)
```

**Bot displays:**
```
✅ Order Created!

Order ID: 12345
Amount: $100.00 USD
Tokens: 0.002312 BTC

Choose your payment method:
[💳 Pay with Card] [₿ Pay with Crypto]
[📊 Check Status]
```

**Backend Process:**
- Creates transaction record in database
- Generates unique order ID
- Provides payment options
- Clears FSM state

## 📊 Transaction Management

### **Database Operation** (`models/transaction.py`)
```sql
INSERT INTO transactions (
    user_telegram_id,     -- 123456789
    payment_method,       -- 'fiat'
    payment_amount,       -- 100.00
    payment_currency,     -- 'USD'
    token_symbol,         -- 'BTC'
    token_amount,         -- 0.002312
    recipient_address,    -- 'bc1qxy2k...'
    status,              -- 'pending_payment'
    fees,                -- 2.00
    created_at           -- 2024-01-15 10:30:00
);
```

### **Status Tracking**
```
pending_payment → processing → completed
                            ↘ failed
```

## 🔄 Payment Processing Flow

### **Current Implementation** (Demo/Development)
```python
# services/token_resale.py
async def _purchase_tokens(token_symbol: str, amount: float) -> bool:
    # Simulate token purchase
    await asyncio.sleep(1)  # Simulate API call
    return True  # Demo: assume success

async def _transfer_tokens(token_symbol: str, amount: float, address: str) -> str:
    # Simulate blockchain transfer  
    await asyncio.sleep(2)  # Simulate transaction time
    return f"0x{'a' * 64}"  # Mock transaction hash
```

### **Production Integration Points**
```python
# DEX Integration (Uniswap V3)
await uniswap_v3.swap_exact_input(
    token_in="USDC",
    token_out=token_symbol,
    amount_in=usdc_amount,
    amount_out_minimum=min_tokens,
    recipient=platform_wallet
)

# Blockchain Transfer (Web3)
tx_hash = await web3.eth.send_transaction({
    'from': platform_wallet,
    'to': recipient_address,
    'value': web3.toWei(token_amount, 'ether'),
    'gas': 21000
})
```

## 🛠️ Admin Operations

### **Admin Menu Access**
```python
# Available to users in config.ADMIN_ID_LIST
if telegram_id in config.ADMIN_ID_LIST:
    keyboard.append([admin_menu_button])
```

### **Admin Functions** (`services/admin_simplified.py`)
- **📊 Transaction Stats** - Monitor order volume
- **⏳ Pending Orders** - View processing queue  
- **💰 Platform Balance** - Check token inventory
- **🔄 Refresh Prices** - Update market rates
- **📈 Daily Summary** - Business analytics

## ⚙️ Technical Architecture

### **Message Routing**
```python
main_router = Router()

# Command handlers
@main_router.message(Command(commands=["start", "help"]))

# Text button handlers  
@main_router.message(F.text == "🪙 Buy Tokens")
@main_router.message(F.text == "📊 My Orders")

# Callback handlers
@main_router.callback_query(F.data.startswith("select_token:"))
@main_router.callback_query(F.data == "confirm_order")
```

### **Middleware Stack**
```python
# Applied to all messages and callbacks
main_router.message.middleware(throttling_middleware)      # Rate limiting
main_router.callback_query.middleware(throttling_middleware)
main_router.message.middleware(DBSessionMiddleware())      # Database sessions
main_router.callback_query.middleware(DBSessionMiddleware())
```

### **State Management** (FSM)
```python
class TokenPurchaseStates(StatesGroup):
    selecting_token = State()    # After token selection
    entering_amount = State()    # Waiting for USD amount
    entering_address = State()   # Waiting for wallet address  
    confirming_order = State()   # Showing order summary
```

### **Error Handling**
```python
@main_router.error(F.update.message.as_("message"))
async def error_handler(event: ErrorEvent, message: Message):
    await message.answer("Oops, something went wrong!")
    # Send detailed error to admins
    await NotificationService.send_to_admins(traceback_str, None)
```

## 🔐 Security Features

### **Input Validation**
- **Amount limits**: $10 minimum, $10,000 maximum
- **Address validation**: Regex patterns for each token type
- **Rate limiting**: Prevents spam and abuse
- **User authentication**: Telegram user ID verification

### **Error Recovery**
- **Graceful failures**: User-friendly error messages
- **Admin notifications**: Critical errors sent to admin chat
- **State cleanup**: FSM state cleared on errors
- **Transaction rollback**: Database consistency maintained

## 📱 User Experience Features

### **Real-time Feedback**
- ✅ **Instant responses** to button clicks
- ⏳ **Loading indicators** for API calls
- 📊 **Progress tracking** through order states
- 🔔 **Status notifications** for order updates

### **Intuitive Navigation**
- 🏠 **Persistent main menu** always accessible
- ❌ **Cancel buttons** in every step
- 🔄 **Back navigation** through order flow
- 📱 **Mobile-optimized** keyboard layouts

### **Clear Information Display**
- 💰 **Real-time pricing** from CoinGecko
- 📋 **Detailed order summaries** before confirmation
- 📊 **Transaction history** with clear status indicators
- ⚠️ **Warning messages** for important actions

## 🚀 Bot Deployment

### **Webhook Mode** (Production)
```python
# bot.py - FastAPI server receives Telegram updates
@app.post(config.WEBHOOK_PATH)
async def webhook(request: Request):
    update_data = await request.json()
    await dp.feed_webhook_update(bot, update_data)
```

### **Polling Mode** (Development)
```python
# Alternative for local development
await dp.start_polling(bot)
```

### **Multi-bot Support** (Optional)
```python
# multibot.py - Support multiple bot instances
if config.MULTIBOT:
    main_multibot(main_router)
```

---

## 🎯 **Summary: How It Works**

The bot operates as a **conversational interface** for token purchases:

1. **User starts** → Bot shows token menu
2. **User selects token** → Bot asks for amount  
3. **User enters amount** → Bot asks for wallet address
4. **User provides address** → Bot shows order summary
5. **User confirms** → Bot creates order and shows payment options
6. **Payment processed** → Bot updates status and delivers tokens

The entire flow is **stateful** (using FSM), **validated** (input checking), **persistent** (database storage), and **user-friendly** (clear messaging and error handling).

**Result: A simple, fast, and secure way to buy tokens directly through Telegram!** 🚀
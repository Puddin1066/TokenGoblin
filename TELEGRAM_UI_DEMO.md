# 🤖 TokenGoblin Telegram UI Demo

## 📱 How the Telegram UI Looks and Operates

### 🏠 **Main Menu Interface**

When users start the bot with `/start`, they see this main menu:

```
┌─────────────────────────────────────┐
│ 🤖 Welcome to TokenGoblin Bot!     │
│                                     │
│ 🗂️ All categories    👤 My profile │
│ ❓ FAQ              🆘 Help        │
│ 🛒 Cart                           │
│ 🔑 Admin Menu                     │
└─────────────────────────────────────┘
```

### 🗂️ **Category Navigation**

Users can browse products through a hierarchical menu:

```
┌─────────────────────────────────────┐
│ 📦 Available Categories             │
│                                     │
│ 🎮 Gaming                          │
│ 💻 Software                        │
│ 📚 Ebooks                          │
│ 🎬 Entertainment                   │
│                                     │
│ ⬅️ Previous    ➡️ Next             │
└─────────────────────────────────────┘
```

### 📦 **Subcategory Selection**

When a category is selected:

```
┌─────────────────────────────────────┐
│ 🎮 Gaming                          │
│                                     │
│ 📦 Game Keys | Price: $59.99 | Qty: 25 │
│ 📦 Accounts  | Price: $29.99 | Qty: 50 │
│ 📦 DLC       | Price: $19.99 | Qty: 100│
│                                     │
│ ⬅️ Back to categories              │
└─────────────────────────────────────┘
```

### 🛒 **Product Selection & Cart**

Users can select quantity and add to cart:

```
┌─────────────────────────────────────┐
│ 🎮 Cyberpunk 2077 Game Key         │
│ Price: $59.99                      │
│ Description: Digital game key for   │
│ Cyberpunk 2077                     │
│ Quantity available: 25              │
│                                     │
│ Select quantity:                    │
│ [1] [2] [3] [4] [5]               │
│                                     │
│ 🛒 Add to Cart    ⬅️ Back          │
└─────────────────────────────────────┘
```

### 👤 **User Profile Interface**

The profile section shows balance and options:

```
┌─────────────────────────────────────┐
│ 👤 Your Profile                     │
│ ID: 123456789                      │
│                                     │
│ Your balance in USD:                │
│ $150.00                            │
│                                     │
│ ➕ Top Up Balance                   │
│ 🧾 Purchase History                 │
│ 🔄 Refresh Balance                  │
└─────────────────────────────────────┘
```

### 💰 **Payment Interface**

Crypto payment options:

```
┌─────────────────────────────────────┐
│ 💵 Choose a top-up method:         │
│                                     │
│ ₿ BTC                              │
│ Ł LTC                              │
│ SOL                                │
│ ETH                                │
│ USDT TRC-20                        │
│ USDT ERC-20                        │
│                                     │
│ ⬅️ Back to profile                 │
└─────────────────────────────────────┘
```

## 🤖 **AI Token Resale Focus**

### 🎯 **Modified Main Menu for AI Tokens**

```
┌─────────────────────────────────────┐
│ 🤖 Claude AI Token Store           │
│                                     │
│ 🧠 AI Models       👤 My Profile   │
│ 💰 Buy Tokens      🛒 Cart         │
│ 📊 Usage Stats     🆘 Help         │
│ 🔑 Admin Panel                     │
└─────────────────────────────────────┘
```

### 🧠 **AI Model Categories**

```
┌─────────────────────────────────────┐
│ 🧠 Claude AI Models                │
│                                     │
│ 📦 Claude 3 Sonnet | $0.015/token │
│ 📦 Claude 3 Opus   | $0.015/token │
│ 📦 Claude 3 Haiku  | $0.00025/token│
│                                     │
│ ⬅️ Previous    ➡️ Next             │
└─────────────────────────────────────┘
```

### 💰 **Token Purchase Interface**

```
┌─────────────────────────────────────┐
│ 🧠 Claude 3 Sonnet                 │
│ Price: $0.015 per token            │
│ Description: High-performance AI    │
│ model for complex tasks             │
│ Available tokens: 1,000,000        │
│                                     │
│ Select token amount:                │
│ [100] [500] [1000] [5000] [10000] │
│                                     │
│ 🛒 Buy Tokens    ⬅️ Back           │
└─────────────────────────────────────┘
```

### 📊 **AI Usage Dashboard**

```
┌─────────────────────────────────────┐
│ 📊 Your AI Usage Stats             │
│                                     │
│ 🧠 Claude 3 Sonnet: 2,500 tokens  │
│ 🧠 Claude 3 Opus: 500 tokens      │
│ 🧠 Claude 3 Haiku: 10,000 tokens  │
│                                     │
│ 💰 Total Spent: $45.25            │
│ 📈 This Month: $12.50             │
│                                     │
│ 🔄 Refresh Stats    ⬅️ Back        │
└─────────────────────────────────────┘
```

## 🔧 **How to Focus on AI Token Resale**

### 1. **Modify Categories**

Update the database to have AI-focused categories:

```python
# Sample AI categories
categories = [
    "Claude AI Models",
    "GPT Models", 
    "Specialized AI",
    "Bulk Packages"
]

subcategories = [
    "Claude 3 Sonnet",
    "Claude 3 Opus", 
    "Claude 3 Haiku",
    "GPT-4 Turbo",
    "GPT-3.5 Turbo"
]
```

### 2. **Update Localization**

Modify `l10n/en.json` for AI-focused text:

```json
{
  "user": {
    "all_categories": "🧠 AI Models",
    "my_profile": "👤 My Profile",
    "cart": "🛒 Cart",
    "top_up_balance_button": "💰 Buy Tokens",
    "purchase_history_button": "📊 Usage History"
  }
}
```

### 3. **Customize Product Descriptions**

```python
# AI token product examples
ai_products = [
    {
        "category": "Claude AI Models",
        "subcategory": "Claude 3 Sonnet", 
        "description": "High-performance AI model for complex reasoning tasks",
        "price": 0.015,
        "private_data": "Claude 3 Sonnet API Key: claude-3-sonnet-xxxxx"
    },
    {
        "category": "Claude AI Models",
        "subcategory": "Claude 3 Haiku",
        "description": "Fast and efficient AI model for quick responses", 
        "price": 0.00025,
        "private_data": "Claude 3 Haiku API Key: claude-3-haiku-xxxxx"
    }
]
```

### 4. **Add AI-Specific Features**

```python
# Add to run.py or create new handler
@main_router.message(F.text == "📊 Usage Stats")
async def ai_usage_stats(message: types.message):
    """Show AI token usage statistics"""
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="🧠 Claude Usage", callback_data="claude_stats")
    keyboard.button(text="💰 Token Balance", callback_data="token_balance")
    keyboard.button(text="📈 Usage Trends", callback_data="usage_trends")
    
    await message.answer(
        "📊 **AI Token Usage Dashboard**\n\n"
        "Track your AI model usage and spending:\n"
        "• Token consumption by model\n"
        "• Cost analysis and trends\n"
        "• Usage recommendations\n\n"
        "Select an option:",
        reply_markup=keyboard.as_markup()
    )
```

## 🎨 **UI Customization Options**

### **Theme Customization**

```python
# Custom emojis and branding
AI_THEME = {
    "main_menu": "🧠 AI Token Store",
    "categories": "🤖 AI Models", 
    "profile": "👤 My AI Profile",
    "cart": "🛒 Token Cart",
    "payment": "💰 Buy Tokens"
}
```

### **Enhanced Features**

1. **Token Balance Display**: Show available tokens per model
2. **Usage Analytics**: Track token consumption patterns
3. **Auto-Refill**: Automatic token purchase when low
4. **Bulk Discounts**: Volume pricing for large purchases
5. **Usage Alerts**: Notifications when approaching limits

### **Admin Panel for AI Tokens**

```
┌─────────────────────────────────────┐
│ 🔑 AI Token Admin Panel            │
│                                     │
│ 📊 Token Analytics                 │
│ 🧠 Model Management                │
│ 💰 Pricing Control                 │
│ 📦 Inventory Management             │
│ 👥 User Management                 │
│ 📢 Announcements                   │
└─────────────────────────────────────┘
```

## 🚀 **Implementation Steps**

### 1. **Database Setup**
```bash
# Add AI-specific categories and products
python -c "
from models.category import Category
from models.subcategory import Subcategory
from models.item import Item
# Add AI categories and products
"
```

### 2. **Update Configuration**
```env
# .env file
AGENTIC_MODE=true
OPENROUTER_API_KEY=your_key
ANTHROPIC_API_KEY=your_key
```

### 3. **Customize UI Text**
```bash
# Edit l10n/en.json for AI-focused language
```

### 4. **Add AI Features**
```bash
# Run with agentic features
python run_agentic.py
```

## 📱 **User Experience Flow**

1. **User starts bot** → Sees AI-focused welcome
2. **Browses AI models** → Selects Claude 3 Sonnet
3. **Chooses token amount** → 1000 tokens for $15
4. **Makes payment** → Crypto payment processing
5. **Receives API key** → Immediate access to tokens
6. **Tracks usage** → Monitor consumption in profile

The bot can be **completely transformed** from a general digital goods marketplace into a **specialized AI token resale platform** by simply updating the categories, products, and UI text while maintaining all the existing e-commerce functionality. 
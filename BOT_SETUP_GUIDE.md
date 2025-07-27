# 🤖 Bot Setup Guide

## 📋 **Step 1: Get Your Bot Token**

1. **Open Telegram** and search for `@BotFather`
2. **Send `/newbot`** to create a new bot
3. **Choose a name** for your bot (e.g., "My Token Store")
4. **Choose a username** (must end in 'bot', e.g., "mytokenstore_bot")
5. **Copy the token** that BotFather gives you (looks like: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`)

## 🔧 **Step 2: Update Your .env File**

Replace the placeholder token with your real token:

```bash
# Edit your .env file
nano .env

# Or use this command to update the token:
# sed -i '' 's/your_telegram_bot_token_here/YOUR_ACTUAL_TOKEN_HERE/' .env
```

**Example .env file:**
```env
# Bot Configuration
TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
ADMIN_ID_LIST=YOUR_TELEGRAM_ID
SUPPORT_LINK=https://t.me/your_username

# ... rest of the file stays the same
```

## 🆔 **Step 3: Get Your Telegram ID**

1. **Send a message** to @userinfobot on Telegram
2. **Copy your ID** (it's a number like `123456789`)
3. **Update ADMIN_ID_LIST** in your .env file

## 🚀 **Step 4: Test Your Bot**

### **Option A: Local Testing (Recommended)**
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the bot
python run.py

# 3. Test in Telegram
# Send /start to your bot
```

### **Option B: With ngrok for Webhook Testing**
```bash
# 1. Install ngrok
brew install ngrok

# 2. Start ngrok
ngrok http 5000

# 3. Copy the HTTPS URL (e.g., https://abc123.ngrok.io)

# 4. Update your .env file
WEBHOOK_URL=https://abc123.ngrok.io/

# 5. Run the bot
python run.py
```

## 🧪 **Step 5: Test the Bot**

1. **Open Telegram**
2. **Search for your bot** (using the username you created)
3. **Send `/start`** to your bot
4. **You should see the main menu** with buttons

## 🔍 **Troubleshooting**

### **If the bot doesn't respond:**
```bash
# Check if the bot is running
ps aux | grep python

# Check the logs
tail -f bot.log

# Test the token
curl "https://api.telegram.org/bot/YOUR_TOKEN/getMe"
```

### **If you get "Unauthorized" error:**
- Double-check your token is correct
- Make sure there are no extra spaces
- Verify the token with BotFather

### **If webhook doesn't work:**
- Use ngrok for local development
- Or use polling mode instead of webhooks

## 🎯 **Quick Commands**

```bash
# Update token (replace YOUR_TOKEN with actual token)
sed -i '' 's/your_telegram_bot_token_here/YOUR_TOKEN/' .env

# Update admin ID (replace YOUR_ID with your Telegram ID)
sed -i '' 's/123456789/YOUR_ID/' .env

# Test the bot
python run.py

# Test with AI features
python run_agentic.py
```

## 📱 **Expected Bot Interface**

After setup, your bot should show:
```
🤖 Welcome to TokenGoblin Bot!

🗂️ All categories    👤 My profile
❓ FAQ              🆘 Help
🛒 Cart
🔑 Admin Menu
```

## 🎉 **Success Indicators**

✅ **Bot responds to /start**
✅ **Main menu appears with buttons**
✅ **No error messages in console**
✅ **Admin notifications work** (if you're an admin)

## 🚨 **Security Notes**

- **Never share your bot token** publicly
- **Keep your .env file secure**
- **Use different tokens for development and production**
- **Regularly rotate your tokens**

## 📞 **Need Help?**

If you encounter issues:
1. Check the console output for error messages
2. Verify your token with BotFather
3. Test the token with the Telegram API
4. Check your internet connection 
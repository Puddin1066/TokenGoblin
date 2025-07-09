# 🧠 Claude Token Resale System

A comprehensive Claude token **resale infrastructure** targeted at AI researchers, featuring:

1. **Telegram Bot** - Claude token vending with payment processing
2. **Gist Generator** - Personalized GitHub Gist pages from CSV data
3. **Email Campaign Builder** - Localized email outreach system

---

## 📁 Repository Structure

```
/bot/               → Claude token vending bot (Aiogram v3)
/gist_generator/    → Markdown page generator from CSV
/email_campaign/    → Localized email copy generator
.env.example        → Required configuration variables
README.md           → Setup and usage documentation
```

---

## 🚀 Quick Start

### 1. Clone and Setup
```bash
git clone <repository-url>
cd claude-token-resale
cp .env.example .env
# Edit .env with your configuration
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the Bot
```bash
python run.py
```

---

## 🤖 Telegram Bot Features

### Deep Link Support
The bot accepts deep links with payload format:
```
https://t.me/ClaudeVendBot?start=campaignID|email|abstract_snippet
```

### Payment Methods
- **Telegram Payments** (INR, RUB)
- **Cryptocurrency** (TON, BTC, LTC via static wallets)

### Commands
- `/start <payload>` - Initialize with campaign data
- `/balance` - Check token balance
- `/usage` - View usage history

### Workflow
1. User clicks deep link with research paper context
2. Bot shows personalized message with paper abstract
3. User purchases tokens via Telegram Payments or crypto
4. Bot credits tokens via OpenRouter API
5. CRM sync via webhook

---

## 📝 Gist Generator

### Input Format
CSV file with columns:
```
name,email,country,abstract_snippet,campaignID,language
```

### Usage
```bash
python gist_generator/generator.py leads.csv
```

### Output
- Individual `gist_<email>.md` files
- Localized content (EN/RU/ZH)
- Optional GitHub upload

### Sample Output
```markdown
# 🧠 Claude Token Access – For Dr. Li Wei

Your research on:
> "Prompt Optimization Methods for Large Language Models"

…suggests you could benefit from Claude 3's reasoning capabilities.

🚀 Buy token access instantly:
🔗 https://t.me/ClaudeVendBot?start=camp99|liwei@tsinghua.edu.cn|Prompt+Optimization+Methods

This page was generated automatically for researchers in the AI field.
```

---

## 📧 Email Campaign Generator

### Usage
```bash
python email_campaign/generator.py leads.csv
```

### Output
Individual `.txt` files with:
- Localized subject lines
- Personalized email bodies
- Deep link integration

### Sample Email
```
Subject: Claude Token Access for "Prompt Optimization Methods"

Hi Dr. Li Wei,

We came across your recent work on "Prompt Optimization Methods for Large Language Models".

If you want to try Claude 3 for research, we offer prepaid token packs accessible via Telegram:

🔗 https://t.me/ClaudeVendBot?start=camp99|liwei@tsinghua.edu.cn|Prompt+Optimization+Methods

Best,
ClaudeToken Team
```

---

## ⚙️ Configuration

### Required Environment Variables

```env
# Bot Configuration
BOT_TOKEN=your_telegram_bot_token
WEBHOOK_SECRET_TOKEN=your_webhook_secret

# OpenRouter Integration
OPENROUTER_KEY=your_openrouter_api_key

# Payment Processing
PAYMENTS_PROVIDER_TOKEN=your_telegram_payments_token

# Database
DATABASE_URL=sqlite:///claude_tokens.db

# CRM Integration
WEBHOOK_URL=https://your-crm.com/webhook

# GitHub Integration (Optional)
GITHUB_PAT=your_github_personal_access_token

# Email Configuration (Optional)
SMTP_USER=your_email@domain.com
SMTP_PASS=your_email_password
EMAIL_FROM=ClaudeToken Team <noreply@domain.com>
```

---

## 🔧 Advanced Usage

### Custom Localization
Add new language files in `l10n/` directory:
- `l10n/ru.json` - Russian localization
- `l10n/zh.json` - Chinese localization

### Database Management
The bot uses SQLAlchemy with support for:
- SQLite (default)
- PostgreSQL
- MySQL

### Webhook Integration
Bot sends POST requests to `WEBHOOK_URL` with:
```json
{
  "email": "researcher@university.edu",
  "campaignID": "camp99",
  "action": "purchase",
  "tokens": 10000,
  "timestamp": "2024-01-01T00:00:00Z"
}
```

---

## 🎯 Deep Link Examples

### Basic Usage
```
https://t.me/ClaudeVendBot?start=camp99|liwei@tsinghua.edu.cn|Prompt+Optimization+Methods
```

### URL Encoded
```
https://t.me/ClaudeVendBot?start=camp99%7Cliwei%40tsinghua.edu.cn%7CPrompt%2BOptimization%2BMethods
```

### Multiple Campaigns
```
https://t.me/ClaudeVendBot?start=camp_ai2024|researcher@mit.edu|Neural+Architecture+Search
https://t.me/ClaudeVendBot?start=camp_nlp2024|prof@stanford.edu|Transformer+Architectures
```

---

## 🌐 Localization Support

### Supported Languages
- **English** (en) - Default
- **Russian** (ru) - For Russian researchers
- **Chinese** (zh) - For Chinese researchers

### Language Detection
Based on CSV `language` column:
- `en` → English content
- `ru` → Russian greeting + English content
- `zh` → Chinese greeting + English content

---

## 📊 Analytics & Monitoring

### Bot Analytics
- User registration tracking
- Purchase conversion rates
- Token usage statistics
- Revenue per campaign

### CRM Integration
Automatic sync of:
- Lead engagement
- Purchase events
- Token balances
- Campaign performance

---

## 🔒 Security Features

- **Webhook Security** - Secret token validation
- **Database Encryption** - SQLCipher support
- **Rate Limiting** - Redis-based throttling
- **Payment Security** - Telegram Payments integration

---

## 🛠️ Development

### Project Structure
```
├── bot/
│   ├── handlers/          # Message handlers
│   ├── models/           # Database models
│   ├── services/         # Business logic
│   └── utils/            # Utility functions
├── gist_generator/
│   ├── generator.py      # Main generator
│   ├── templates/        # Markdown templates
│   └── localization/     # Language files
├── email_campaign/
│   ├── generator.py      # Email generator
│   ├── templates/        # Email templates
│   └── localization/     # Language files
└── l10n/                 # Bot localization
```

### Running Tests
```bash
python -m pytest tests/
```

### Docker Deployment
```bash
docker-compose up -d
```

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Create Pull Request

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

---

## 🔗 Links

- **Demo Bot**: [@ClaudeVendBot](https://t.me/ClaudeVendBot)
- **Support**: [Contact Developer](https://t.me/support)
- **Documentation**: [Full Docs](https://docs.example.com)

---

*This system is designed for educational and research purposes. Please ensure compliance with local laws and OpenRouter's terms of service.*
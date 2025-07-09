"""
Email templates for different languages
"""

EMAIL_TEMPLATES = {
    "en": {
        "subject": 'Claude Token Access for "{abstract_snippet}"',
        "body": """Hi Dr. {name},

We came across your recent work on "{abstract_snippet}".

If you want to try Claude 3 for research, we offer prepaid token packs accessible via Telegram:

🔗 {deep_link}

Claude tokens give you instant access to:
• Advanced reasoning for complex problems
• Long-context understanding for research papers
• Multi-language support for international work
• Reliable AI assistance for academic tasks

Pricing:
• 10,000 tokens = $5.00 USD
• 50,000 tokens = $20.00 USD
• 100,000 tokens = $35.00 USD

Payment via Telegram is secure and instant. Cryptocurrency options also available.

Best regards,
ClaudeToken Team

---
This email was sent to researchers in AI/ML. If you prefer not to receive these emails, please reply with "UNSUBSCRIBE"."""
    },
    "ru": {
        "subject": 'Доступ к токенам Claude для "{abstract_snippet}"',
        "body": """Здравствуйте, д-р {name},

Мы ознакомились с вашей недавней работой по теме "{abstract_snippet}".

Если вы хотите попробовать Claude 3 для исследований, мы предлагаем предоплаченные пакеты токенов, доступные через Telegram:

🔗 {deep_link}

Токены Claude дают вам мгновенный доступ к:
• Продвинутым рассуждениям для сложных задач
• Пониманию длинного контекста для исследовательских работ
• Многоязыковой поддержке для международной работы
• Надежной помощи ИИ для академических задач

Цены:
• 10,000 токенов = $5.00 USD
• 50,000 токенов = $20.00 USD
• 100,000 токенов = $35.00 USD

Оплата через Telegram безопасна и мгновенна. Также доступны варианты с криптовалютой.

С наилучшими пожеланиями,
Команда ClaudeToken

---
Это письмо было отправлено исследователям в области ИИ/ML. Если вы предпочитаете не получать эти письма, пожалуйста, ответьте "UNSUBSCRIBE"."""
    },
    "zh": {
        "subject": '关于"{abstract_snippet}"的Claude代币访问',
        "body": """您好，{name}博士，

我们注意到您最近关于"{abstract_snippet}"的工作。

如果您想尝试Claude 3进行研究，我们提供通过Telegram访问的预付费代币包：

🔗 {deep_link}

Claude代币为您提供即时访问：
• 复杂问题的高级推理
• 研究论文的长上下文理解
• 国际工作的多语言支持
• 学术任务的可靠AI协助

价格：
• 10,000代币 = $5.00 USD
• 50,000代币 = $20.00 USD
• 100,000代币 = $35.00 USD

通过Telegram支付安全且即时。也可使用加密货币选项。

此致敬礼，
ClaudeToken团队

---
此邮件发送给AI/ML研究人员。如果您不希望收到这些邮件，请回复"UNSUBSCRIBE"。"""
    }
}


def get_email_template(language: str = "en") -> dict:
    """Get email template for specific language"""
    return EMAIL_TEMPLATES.get(language, EMAIL_TEMPLATES["en"])
"""
Localization texts for gist generator
"""

LOCALIZATION_TEXTS = {
    "en": {
        "greeting": "",  # No additional greeting for English
        "research_context": "Your research on:",
        "claude_benefit": "suggests you could benefit from Claude 3's reasoning capabilities.",
        "get_instant_access": "Get Instant Access",
        "buy_now": "Buy Claude Tokens Now",
        "about_tokens": "About Claude Tokens",
        "pricing": "Pricing",
        "secure_payment": "Secure Payment",
        "perfect_for_research": "Perfect for Research",
        "generated_automatically": "This page was generated automatically for researchers in the AI field."
    },
    "ru": {
        "greeting": """👋 Привет из команды ClaudeToken!

Мы заметили вашу работу в области искусственного интеллекта и хотели бы предложить вам доступ к Claude 3 для ваших исследований.""",
        "research_context": "Ваше исследование на тему:",
        "claude_benefit": "показывает, что вы могли бы извлечь пользу из возможностей рассуждения Claude 3.",
        "get_instant_access": "Получить мгновенный доступ",
        "buy_now": "Купить токены Claude сейчас",
        "about_tokens": "О токенах Claude",
        "pricing": "Цены",
        "secure_payment": "Безопасная оплата",
        "perfect_for_research": "Идеально для исследований",
        "generated_automatically": "Эта страница была автоматически создана для исследователей в области ИИ."
    },
    "zh": {
        "greeting": """👋 来自ClaudeToken团队的问候！

我们注意到您在人工智能领域的工作，想为您的研究提供Claude 3的访问权限。""",
        "research_context": "您关于以下主题的研究:",
        "claude_benefit": "表明您可以从Claude 3的推理能力中受益。",
        "get_instant_access": "立即获取访问权限",
        "buy_now": "立即购买Claude代币",
        "about_tokens": "关于Claude代币",
        "pricing": "定价",
        "secure_payment": "安全支付",
        "perfect_for_research": "完美适合研究",
        "generated_automatically": "此页面是为AI领域的研究人员自动生成的。"
    }
}


def get_text(key: str, language: str = "en") -> str:
    """Get localized text by key and language"""
    return LOCALIZATION_TEXTS.get(language, LOCALIZATION_TEXTS["en"]).get(key, key)
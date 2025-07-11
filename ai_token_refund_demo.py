#!/usr/bin/env python3
"""
AI Token Refund & Frictionless Sales Demo

Demonstrates practical approaches to:
1. AI token refund policies
2. Frictionless purchase experience
3. Self-improving sales optimization
"""

import asyncio
from datetime import datetime, timedelta
from typing import Dict, List
from dataclasses import dataclass
from enum import Enum
import json

class TokenType(Enum):
    GPT4 = "gpt-4"
    CLAUDE = "claude-3"
    DALLE = "dall-e-3"

class RefundReason(Enum):
    UNUSED = "unused_tokens"
    TECHNICAL_ISSUE = "technical_issue"
    QUALITY_ISSUE = "quality_issue"
    FIRST_TIME_USER = "first_time_dissatisfaction"

@dataclass
class TokenPackage:
    name: str
    token_type: TokenType
    quantity: int
    price: float
    description: str

@dataclass
class Customer:
    id: str
    name: str
    total_spent: float
    purchase_count: int
    satisfaction_score: float

@dataclass
class Purchase:
    id: str
    customer_id: str
    package: TokenPackage
    purchase_time: datetime
    tokens_used: int
    tokens_remaining: int
    satisfaction_rating: float = 0.0

class AITokenRefundSystem:
    """Smart refund system for AI tokens"""
    
    def __init__(self):
        self.purchases: Dict[str, Purchase] = {}
        self.customers: Dict[str, Customer] = {}
        
    def calculate_refund_rate(self, purchase: Purchase, customer: Customer, reason: RefundReason) -> float:
        """Calculate smart refund rate based on usage, customer value, and reason"""
        
        # Base refund rates by reason
        base_rates = {
            RefundReason.UNUSED: 1.0,           # 100% for unused tokens
            RefundReason.TECHNICAL_ISSUE: 1.0,  # 100% for technical issues
            RefundReason.QUALITY_ISSUE: 0.5,    # 50% for quality issues
            RefundReason.FIRST_TIME_USER: 0.5   # 50% for first-time dissatisfaction
        }
        
        base_rate = base_rates.get(reason, 0.3)
        
        # Usage-based adjustments
        usage_percentage = (purchase.tokens_used / purchase.package.quantity) * 100
        
        if usage_percentage < 5:
            usage_multiplier = 1.0      # Barely used
        elif usage_percentage < 25:
            usage_multiplier = 0.75     # Lightly used
        elif usage_percentage < 50:
            usage_multiplier = 0.5      # Moderately used
        else:
            usage_multiplier = 0.25     # Heavily used
        
        # Customer value adjustments
        if customer.total_spent > 1000:
            customer_multiplier = 1.2   # High-value customer
        elif customer.total_spent > 100:
            customer_multiplier = 1.1   # Regular customer
        else:
            customer_multiplier = 1.0   # New customer
        
        # Time-based adjustments
        hours_since_purchase = (datetime.now() - purchase.purchase_time).total_seconds() / 3600
        
        if hours_since_purchase < 1:
            time_multiplier = 1.1       # Within 1 hour
        elif hours_since_purchase < 24:
            time_multiplier = 1.0       # Within 24 hours
        else:
            time_multiplier = 0.8       # After 24 hours
        
        # Calculate final refund rate
        refund_rate = base_rate * usage_multiplier * customer_multiplier * time_multiplier
        
        # Cap at 100%
        return min(1.0, refund_rate)
    
    def generate_refund_offer(self, purchase: Purchase, customer: Customer, reason: RefundReason) -> Dict:
        """Generate smart refund offer with alternatives"""
        
        refund_rate = self.calculate_refund_rate(purchase, customer, reason)
        refund_amount = purchase.package.price * refund_rate
        
        # Generate alternatives
        alternatives = []
        
        if refund_rate < 0.6:
            # Offer bonus tokens instead
            bonus_tokens = int(purchase.package.quantity * 0.3)
            alternatives.append({
                "type": "bonus_tokens",
                "offer": f"Keep your {purchase.package.quantity:,} tokens + get {bonus_tokens:,} bonus tokens",
                "value": f"${purchase.package.price * 0.3:.2f} extra value"
            })
        
        if refund_rate < 0.8:
            # Offer account credit
            credit_amount = purchase.package.price * 0.6
            alternatives.append({
                "type": "account_credit", 
                "offer": f"${credit_amount:.2f} credit for future AI token purchases",
                "value": "Never expires, use on any package"
            })
        
        return {
            "refund_approved": refund_rate > 0.1,
            "refund_rate": refund_rate,
            "refund_amount": refund_amount,
            "alternatives": alternatives,
            "recommendation": self._get_refund_recommendation(refund_rate, alternatives)
        }
    
    def _get_refund_recommendation(self, refund_rate: float, alternatives: List[Dict]) -> str:
        """Get smart recommendation for the customer"""
        
        if refund_rate >= 0.8:
            return "We recommend processing the refund - you deserve great AI experiences!"
        elif refund_rate >= 0.5:
            return "We can offer a partial refund or consider our bonus alternatives below."
        elif alternatives:
            return "Instead of a small refund, we recommend our bonus offers for better value!"
        else:
            return "Let's find a way to improve your AI experience - our support team will help."


class FrictionlessAITokenExperience:
    """Demonstrates frictionless AI token purchase and usage"""
    
    def __init__(self):
        self.packages = {
            "gpt4_starter": TokenPackage(
                name="GPT-4 Starter Pack",
                token_type=TokenType.GPT4,
                quantity=10000,
                price=19.99,
                description="Perfect for trying GPT-4 - 20 articles or 50 code snippets"
            ),
            "gpt4_pro": TokenPackage(
                name="GPT-4 Professional", 
                token_type=TokenType.GPT4,
                quantity=50000,
                price=79.99,
                description="For serious AI work - 100+ articles or 200+ code files"
            ),
            "claude_creative": TokenPackage(
                name="Claude Creative Bundle",
                token_type=TokenType.CLAUDE,
                quantity=25000,
                price=49.99,
                description="Advanced reasoning and creative writing"
            )
        }
    
    async def instant_purchase_flow(self, customer_name: str, package_id: str) -> Dict:
        """Simulate ultra-frictionless purchase experience"""
        
        package = self.packages.get(package_id)
        if not package:
            return {"error": "Package not found"}
        
        # Instant purchase processing
        purchase_id = f"purchase_{hash(customer_name + package_id)}"
        api_key = f"sk-ai-{hash(customer_name)}123"
        
        # Instant delivery
        delivery_result = {
            "success": True,
            "purchase_id": purchase_id,
            "customer_name": customer_name,
            "package": package.name,
            "tokens_delivered": package.quantity,
            "api_key": api_key,
            "endpoint": f"https://api.ai-tokens.com/v1/{package.token_type.value}",
            "dashboard_url": f"https://dashboard.ai-tokens.com/{purchase_id}",
            "estimated_value": f"${package.price * 2:.2f} worth of AI capabilities",
            "instant_access": True,
            "satisfaction_guarantee": "50% refund if not satisfied within 24 hours"
        }
        
        return delivery_result
    
    def generate_personalized_message(self, customer_name: str, package: TokenPackage, customer_type: str = "new") -> str:
        """Generate personalized sales message"""
        
        if customer_type == "power_user":
            return f"""
🎯 **Perfect for {customer_name}!**

**{package.name}** - {package.quantity:,} tokens for ${package.price}

⚡ **Instant delivery** - API key in your DMs within 30 seconds
🎯 **Your workflow**: {package.description}
📊 **Usage tracking** - Monitor every token in real-time
🔄 **Satisfaction guarantee** - 50% refund within 24 hours

💡 **Pro tip**: Start with complex prompts - you know what you're doing!
"""
        
        elif customer_type == "regular":
            return f"""
🌟 **Welcome back, {customer_name}!**

Based on your usage, **{package.name}** is perfect for you:

✅ **{package.quantity:,} tokens** - {package.description}
💰 **${package.price}** - 2x value compared to pay-per-use
🚀 **Instant access** - Start using immediately
📈 **Perfect for scaling** your AI projects

🎁 **Loyalty bonus**: Extra support and priority access!
"""
        
        else:  # new user
            return f"""
🚀 **Welcome to AI Tokens, {customer_name}!**

**{package.name}** - Perfect for getting started:

🎯 **What you get**: {package.description}
💰 **Price**: ${package.price} (save 50% vs pay-per-use)
⚡ **Instant setup** - Working in under 60 seconds
🛡️ **Risk-free** - 50% refund guarantee

💡 **Getting started tip**: Try simple prompts first, then get creative!
"""


class AgenticSalesOptimizer:
    """Self-improving sales agent that learns from customer behavior"""
    
    def __init__(self):
        self.conversion_data = {}
        self.customer_patterns = {}
        self.a_b_test_results = {}
    
    def analyze_customer_behavior(self, customer_id: str, interaction_data: Dict) -> Dict:
        """Analyze customer behavior to improve sales approach"""
        
        # Track customer patterns
        if customer_id not in self.customer_patterns:
            self.customer_patterns[customer_id] = {
                "interactions": 0,
                "conversions": 0,
                "preferred_messaging": "value_focused",
                "price_sensitivity": "medium",
                "decision_speed": "medium"
            }
        
        patterns = self.customer_patterns[customer_id]
        patterns["interactions"] += 1
        
        # Learn from this interaction
        if interaction_data.get("converted"):
            patterns["conversions"] += 1
            
        if interaction_data.get("price_objection"):
            patterns["price_sensitivity"] = "high"
            
        if interaction_data.get("quick_decision"):
            patterns["decision_speed"] = "fast"
        elif interaction_data.get("slow_decision"):
            patterns["decision_speed"] = "slow"
        
        # Calculate conversion rate
        conversion_rate = patterns["conversions"] / patterns["interactions"]
        
        return {
            "customer_id": customer_id,
            "conversion_rate": conversion_rate,
            "total_interactions": patterns["interactions"],
            "insights": self._generate_insights(patterns),
            "recommended_approach": self._recommend_approach(patterns)
        }
    
    def _generate_insights(self, patterns: Dict) -> List[str]:
        """Generate insights from customer patterns"""
        
        insights = []
        
        conversion_rate = patterns["conversions"] / max(patterns["interactions"], 1)
        
        if conversion_rate > 0.7:
            insights.append("High-converting customer - direct approach works well")
        elif conversion_rate > 0.3:
            insights.append("Moderate conversion - try social proof and urgency")
        else:
            insights.append("Low conversion - focus on value and risk reduction")
        
        if patterns["price_sensitivity"] == "high":
            insights.append("Price-sensitive - emphasize value and ROI")
        
        if patterns["decision_speed"] == "fast":
            insights.append("Quick decision maker - use urgency and scarcity")
        elif patterns["decision_speed"] == "slow":
            insights.append("Deliberate decision maker - provide detailed info")
        
        return insights
    
    def _recommend_approach(self, patterns: Dict) -> str:
        """Recommend best sales approach based on patterns"""
        
        conversion_rate = patterns["conversions"] / max(patterns["interactions"], 1)
        
        if patterns["price_sensitivity"] == "high":
            return "value_focused"
        elif conversion_rate < 0.3:
            return "social_proof"
        elif patterns["decision_speed"] == "fast":
            return "urgency_focused"
        else:
            return "value_focused"


# Demo the complete system
async def demo_ai_token_system():
    """Demonstrate the complete AI token system with refunds and frictionless sales"""
    
    print("🤖 AI Token Refund & Frictionless Sales Demo")
    print("=" * 60)
    
    # Initialize systems
    refund_system = AITokenRefundSystem()
    sales_system = FrictionlessAITokenExperience()
    sales_optimizer = AgenticSalesOptimizer()
    
    # Create sample customer
    customer = Customer(
        id="cust_123",
        name="Alex Developer",
        total_spent=150.0,
        purchase_count=2,
        satisfaction_score=4.2
    )
    
    print(f"\n👤 Customer: {customer.name}")
    print(f"   💰 Total spent: ${customer.total_spent}")
    print(f"   📊 Satisfaction: {customer.satisfaction_score}/5.0")
    
    # Demo 1: Frictionless Purchase
    print(f"\n🛒 DEMO 1: Frictionless Purchase Experience")
    print("-" * 40)
    
    # Show personalized message
    package = sales_system.packages["gpt4_pro"]
    message = sales_system.generate_personalized_message(customer.name, package, "regular")
    print(message)
    
    # Process instant purchase
    purchase_result = await sales_system.instant_purchase_flow(customer.name, "gpt4_pro")
    
    if purchase_result["success"]:
        print(f"✅ Purchase completed in <30 seconds!")
        print(f"🔑 API Key: {purchase_result['api_key']}")
        print(f"📊 Dashboard: {purchase_result['dashboard_url']}")
    
    # Demo 2: Smart Refund System
    print(f"\n🔄 DEMO 2: Smart Refund Analysis")
    print("-" * 40)
    
    # Create purchase record
    purchase = Purchase(
        id=purchase_result["purchase_id"],
        customer_id=customer.id,
        package=package,
        purchase_time=datetime.now() - timedelta(hours=2),  # 2 hours ago
        tokens_used=2500,  # Used 5% of tokens
        tokens_remaining=47500
    )
    
    # Test different refund scenarios
    scenarios = [
        (RefundReason.UNUSED, "Customer used <5% of tokens"),
        (RefundReason.QUALITY_ISSUE, "Customer not satisfied with quality"),
        (RefundReason.TECHNICAL_ISSUE, "Technical problems prevented usage"),
        (RefundReason.FIRST_TIME_USER, "First-time user dissatisfaction")
    ]
    
    for reason, description in scenarios:
        refund_offer = refund_system.generate_refund_offer(purchase, customer, reason)
        
        print(f"\n📋 Scenario: {description}")
        print(f"   💰 Refund Rate: {refund_offer['refund_rate']:.1%}")
        print(f"   💵 Refund Amount: ${refund_offer['refund_amount']:.2f}")
        print(f"   📝 Recommendation: {refund_offer['recommendation']}")
        
        if refund_offer['alternatives']:
            print(f"   🎁 Alternative offers:")
            for alt in refund_offer['alternatives']:
                print(f"     • {alt['offer']} ({alt['value']})")
    
    # Demo 3: Self-Improving Sales Agent
    print(f"\n🧠 DEMO 3: Self-Improving Sales Agent")
    print("-" * 40)
    
    # Simulate customer interactions
    interactions = [
        {"converted": True, "quick_decision": True},
        {"converted": False, "price_objection": True},
        {"converted": True, "slow_decision": True},
        {"converted": False, "price_objection": True}
    ]
    
    for i, interaction in enumerate(interactions):
        analysis = sales_optimizer.analyze_customer_behavior(customer.id, interaction)
        
        print(f"\nInteraction {i+1}:")
        print(f"   📊 Conversion Rate: {analysis['conversion_rate']:.1%}")
        print(f"   💡 Insights: {', '.join(analysis['insights'])}")
        print(f"   🎯 Recommended Approach: {analysis['recommended_approach']}")
    
    # Show final recommendations
    print(f"\n🎯 FINAL SYSTEM RECOMMENDATIONS")
    print("=" * 60)
    print("✅ AI Token Refunds: Use smart, usage-based refund rates")
    print("✅ Frictionless Sales: Instant delivery with API keys")
    print("✅ Self-Improving: Learn from each customer interaction")
    print("✅ Customer-Centric: Focus on satisfaction and value")
    print("✅ Risk Mitigation: Offer alternatives before refunds")
    
    return {
        "refund_system": refund_system,
        "sales_system": sales_system,
        "sales_optimizer": sales_optimizer
    }


if __name__ == "__main__":
    # Run the complete demo
    asyncio.run(demo_ai_token_system())
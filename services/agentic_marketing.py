import asyncio
import random
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from sqlalchemy import select, func

from services.geo_targeting import GeoTargetingService
from services.notification import NotificationService
from models.user import User, UserDTO
from utils.localizator import Localizator

logger = logging.getLogger(__name__)


class AgenticMarketingOrchestrator:
    """AI-powered marketing automation for restricted-access countries"""
    
    def __init__(self):
        self.geo_service = GeoTargetingService()
        self.notification_service = NotificationService()
        
        # Marketing campaign parameters
        self.campaign_intervals = {
            'cart_abandonment': 2,      # 2 hours
            'prospect_nurture': 24,     # 24 hours
            'retention': 72,            # 3 days
            'viral_referral': 168       # 7 days
        }
        
        # Regional message templates
        self.message_templates = {
            'ru': self._get_russian_templates(),
            'zh-hans': self._get_chinese_templates(),
            'fa': self._get_persian_templates(),
            'ar': self._get_arabic_templates(),
            'default': self._get_english_templates()
        }
    
    async def start_marketing_orchestration(self):
        """Start all marketing automation campaigns"""
        logger.info("🚀 Starting agentic marketing orchestration...")
        
        # Start background marketing tasks
        tasks = [
            asyncio.create_task(self._run_cart_abandonment_campaign()),
            asyncio.create_task(self._run_prospect_nurturing_campaign()),
            asyncio.create_task(self._run_retention_campaign()),
            asyncio.create_task(self._run_viral_referral_campaign()),
            asyncio.create_task(self._run_urgency_campaigns()),
            asyncio.create_task(self._run_price_sensitivity_campaigns())
        ]
        
        await asyncio.gather(*tasks)
    
    async def _run_cart_abandonment_campaign(self):
        """Automated cart abandonment recovery"""
        while True:
            try:
                logger.info("🛒 Running cart abandonment campaign...")
                
                # Get users with abandoned carts
                abandoned_carts = await self._get_abandoned_carts()
                
                for cart_data in abandoned_carts:
                    user_id = cart_data['user_id']
                    region = cart_data['detected_region']
                    cart_value = cart_data['cart_value']
                    items_count = cart_data['items_count']
                    
                    # Create personalized recovery message
                    message = await self._create_cart_recovery_message(
                        region, cart_value, items_count, user_id
                    )
                    
                    # Send recovery message
                    await self._send_marketing_message(user_id, message, 'cart_recovery')
                    
                    # Schedule follow-up if needed
                    await self._schedule_follow_up(user_id, 'cart_recovery', 24)
                
                # Wait before next check
                await asyncio.sleep(self.campaign_intervals['cart_abandonment'] * 3600)
                
            except Exception as e:
                logger.error(f"Error in cart abandonment campaign: {e}")
                await asyncio.sleep(1800)  # Wait 30 minutes before retry
    
    async def _run_prospect_nurturing_campaign(self):
        """Automated prospect nurturing for high-value leads"""
        while True:
            try:
                logger.info("🎯 Running prospect nurturing campaign...")
                
                # Identify high-value prospects
                prospects = await self._identify_high_value_prospects()
                
                for prospect in prospects[:20]:  # Limit to top 20 daily
                    user_id = prospect['user_id']
                    region = prospect['region']
                    prospect_score = prospect['score']
                    behaviors = prospect['behaviors']
                    
                    # Check if already contacted recently
                    if await self._was_recently_contacted(user_id, 'prospect_nurture', 48):
                        continue
                    
                    # Create personalized prospect message
                    message = await self._create_prospect_nurture_message(
                        region, prospect_score, behaviors
                    )
                    
                    # Send nurturing message
                    await self._send_marketing_message(user_id, message, 'prospect_nurture')
                    
                    # Log prospect contact
                    await self._log_marketing_contact(user_id, 'prospect_nurture', prospect_score)
                
                # Wait before next campaign
                await asyncio.sleep(self.campaign_intervals['prospect_nurture'] * 3600)
                
            except Exception as e:
                logger.error(f"Error in prospect nurturing campaign: {e}")
                await asyncio.sleep(3600)  # Wait 1 hour before retry
    
    async def _run_retention_campaign(self):
        """Automated customer retention campaigns"""
        while True:
            try:
                logger.info("🔄 Running retention campaign...")
                
                # Identify at-risk customers
                at_risk_customers = await self._identify_at_risk_customers()
                
                for customer in at_risk_customers:
                    user_id = customer['user_id']
                    region = customer['region']
                    risk_score = customer['risk_score']
                    last_purchase = customer['last_purchase_days']
                    total_spent = customer['total_spent']
                    
                    # Create retention message based on customer value
                    message = await self._create_retention_message(
                        region, risk_score, last_purchase, total_spent
                    )
                    
                    # Send retention message
                    await self._send_marketing_message(user_id, message, 'retention')
                    
                    # Offer special incentive for high-value customers
                    if total_spent > 100:
                        incentive_message = await self._create_vip_incentive_message(region, total_spent)
                        await asyncio.sleep(300)  # Wait 5 minutes
                        await self._send_marketing_message(user_id, incentive_message, 'vip_incentive')
                
                # Wait before next retention check
                await asyncio.sleep(self.campaign_intervals['retention'] * 3600)
                
            except Exception as e:
                logger.error(f"Error in retention campaign: {e}")
                await asyncio.sleep(7200)  # Wait 2 hours before retry
    
    async def _run_viral_referral_campaign(self):
        """Automated viral referral campaigns"""
        while True:
            try:
                logger.info("📢 Running viral referral campaign...")
                
                # Get active users eligible for referral campaigns
                active_users = await self._get_active_users_for_referrals()
                
                for user_data in active_users:
                    user_id = user_data['user_id']
                    region = user_data['region']
                    purchase_count = user_data['purchase_count']
                    
                    # Create viral referral message
                    message = await self._create_viral_referral_message(
                        region, user_id, purchase_count
                    )
                    
                    # Send referral campaign
                    await self._send_marketing_message(user_id, message, 'viral_referral')
                
                # Wait before next viral campaign
                await asyncio.sleep(self.campaign_intervals['viral_referral'] * 3600)
                
            except Exception as e:
                logger.error(f"Error in viral referral campaign: {e}")
                await asyncio.sleep(14400)  # Wait 4 hours before retry
    
    async def _run_urgency_campaigns(self):
        """Create urgency-driven campaigns for restricted regions"""
        while True:
            try:
                logger.info("⚡ Running urgency campaigns...")
                
                # Get users from restricted regions
                restricted_users = await self._get_restricted_region_users()
                
                for user_data in restricted_users:
                    user_id = user_data['user_id']
                    region = user_data['region']
                    engagement_score = user_data['engagement_score']
                    
                    # Only target highly engaged users for urgency campaigns
                    if engagement_score > 0.7:
                        message = await self._create_urgency_message(region, user_id)
                        await self._send_marketing_message(user_id, message, 'urgency')
                
                # Run urgency campaigns more frequently
                await asyncio.sleep(6 * 3600)  # Every 6 hours
                
            except Exception as e:
                logger.error(f"Error in urgency campaigns: {e}")
                await asyncio.sleep(3600)
    
    async def _run_price_sensitivity_campaigns(self):
        """Price-sensitive campaigns for budget-conscious users"""
        while True:
            try:
                logger.info("💰 Running price sensitivity campaigns...")
                
                # Identify price-sensitive users
                price_sensitive_users = await self._identify_price_sensitive_users()
                
                for user_data in price_sensitive_users:
                    user_id = user_data['user_id']
                    region = user_data['region']
                    avg_purchase = user_data['avg_purchase_amount']
                    
                    # Create budget-friendly offers
                    message = await self._create_budget_offer_message(region, avg_purchase)
                    await self._send_marketing_message(user_id, message, 'budget_offer')
                
                # Run weekly
                await asyncio.sleep(7 * 24 * 3600)  # Every 7 days
                
            except Exception as e:
                logger.error(f"Error in price sensitivity campaigns: {e}")
                await asyncio.sleep(12 * 3600)  # Wait 12 hours
    
    # Message Creation Methods
    
    async def _create_cart_recovery_message(self, region: str, cart_value: float, items_count: int, user_id: int) -> str:
        """Create personalized cart recovery message"""
        templates = self.message_templates.get(region, self.message_templates['default'])
        template = templates['cart_abandonment']
        
        # Add urgency based on time and region
        urgency_phrases = templates['urgency_phrases']
        urgency = random.choice(urgency_phrases)
        
        # Calculate discount offer
        discount_percent = self._calculate_dynamic_discount(cart_value, region)
        
        return template.format(
            items_count=items_count,
            cart_value=cart_value,
            urgency=urgency,
            discount_percent=discount_percent,
            hours_left=random.randint(12, 48)
        )
    
    async def _create_prospect_nurture_message(self, region: str, prospect_score: float, behaviors: Dict) -> str:
        """Create prospect nurturing message"""
        templates = self.message_templates.get(region, self.message_templates['default'])
        
        # Choose template based on prospect score
        if prospect_score > 0.8:
            template = templates['high_value_prospect']
        elif prospect_score > 0.6:
            template = templates['medium_value_prospect']
        else:
            template = templates['low_value_prospect']
        
        # Customize based on behaviors
        pain_points = self._identify_pain_points(behaviors, region)
        benefits = self._get_relevant_benefits(behaviors, region)
        
        return template.format(
            pain_points=pain_points,
            benefits=benefits,
            special_offer=self._generate_special_offer(region, prospect_score)
        )
    
    async def _create_retention_message(self, region: str, risk_score: float, last_purchase_days: int, total_spent: float) -> str:
        """Create customer retention message"""
        templates = self.message_templates.get(region, self.message_templates['default'])
        
        if total_spent > 200:
            template = templates['vip_retention']
        elif total_spent > 50:
            template = templates['valued_customer_retention']
        else:
            template = templates['standard_retention']
        
        # Calculate win-back offer
        winback_offer = self._calculate_winback_offer(total_spent, last_purchase_days)
        
        return template.format(
            days_since_purchase=last_purchase_days,
            total_spent=total_spent,
            winback_offer=winback_offer,
            loyalty_bonus=self._calculate_loyalty_bonus(total_spent)
        )
    
    async def _create_viral_referral_message(self, region: str, user_id: int, purchase_count: int) -> str:
        """Create viral referral campaign message"""
        templates = self.message_templates.get(region, self.message_templates['default'])
        template = templates['viral_referral']
        
        # Generate unique referral code
        referral_code = f"{region.upper()}{user_id:06d}"
        
        # Calculate referral rewards
        referrer_reward = 20 if purchase_count > 3 else 15
        referee_discount = 15 if purchase_count > 3 else 10
        
        return template.format(
            referral_code=referral_code,
            referrer_reward=referrer_reward,
            referee_discount=referee_discount,
            social_proof=self._generate_social_proof(region)
        )
    
    async def _create_urgency_message(self, region: str, user_id: int) -> str:
        """Create urgency-driven message"""
        templates = self.message_templates.get(region, self.message_templates['default'])
        template = templates['urgency_campaign']
        
        # Generate pseudo-random urgency factors
        user_hash = hashlib.md5(str(user_id).encode()).hexdigest()
        hash_int = int(user_hash[:8], 16)
        
        hours_left = 12 + (hash_int % 36)  # 12-48 hours
        spots_left = 50 + (hash_int % 200)  # 50-250 spots
        price_increase = 15 + (hash_int % 20)  # 15-35% increase
        
        return template.format(
            hours_left=hours_left,
            spots_left=spots_left,
            price_increase=price_increase
        )
    
    # Helper Methods
    
    async def _get_abandoned_carts(self) -> List[Dict]:
        """Get users with abandoned carts"""
        # This would query the actual cart database
        # For now, we'll simulate abandoned carts
        return [
            {
                'user_id': 123456,
                'detected_region': 'ru',
                'cart_value': 45.0,
                'items_count': 3,
                'abandoned_hours_ago': 4
            }
        ]
    
    async def _identify_high_value_prospects(self) -> List[Dict]:
        """Identify high-value prospects using behavioral analysis"""
        # This would use real behavioral analysis
        # For now, we'll simulate prospects
        return [
            {
                'user_id': 789012,
                'region': 'zh-hans',
                'score': 0.85,
                'behaviors': {
                    'page_views': 15,
                    'time_spent': 600,
                    'price_checks': 8,
                    'cart_adds': 2
                }
            }
        ]
    
    def _calculate_dynamic_discount(self, cart_value: float, region: str) -> int:
        """Calculate dynamic discount based on cart value and region"""
        base_discount = 10
        
        # Higher discounts for higher value carts
        if cart_value > 100:
            base_discount = 20
        elif cart_value > 50:
            base_discount = 15
        
        # Regional adjustments
        regional_multiplier = {
            'ru': 1.0,
            'zh-hans': 1.2,  # Higher discounts for Chinese market
            'fa': 1.1,
            'ar': 1.0
        }.get(region, 1.0)
        
        return int(base_discount * regional_multiplier)
    
    def _get_russian_templates(self) -> Dict:
        """Russian language message templates"""
        return {
            'cart_abandonment': '''🛒 Ваши токены Claude ждут!

В корзине: {items_count} товаров на ${cart_value:.2f}
{urgency}

🎁 Специальное предложение: скидка {discount_percent}%
⏰ Предложение действительно еще {hours_left} часов

🚀 Завершите покупку одним кликом!''',
            
            'high_value_prospect': '''🤖 Эксклюзивный доступ к Claude AI!

🚫 Claude заблокирован в России? Получите полный доступ!
✅ {benefits}
💡 {pain_points}

🎯 {special_offer}

⚡ Мгновенный доступ без VPN!''',
            
            'vip_retention': '''👑 Вы наш VIP-клиент!

💎 Потрачено: ${total_spent:.2f}
😔 Мы скучаем по вам ({days_since_purchase} дней назад)

🎁 Эксклюзивное предложение VIP:
{winback_offer}

🏆 Бонус лояльности: {loyalty_bonus}% дополнительных токенов''',
            
            'viral_referral': '''🚀 Поделитесь доступом к Claude!

Ваш код: {referral_code}
🎁 За каждого друга: {referrer_reward}% кэшбэк
💰 Ваш друг получает: {referee_discount}% скидку

{social_proof}

📱 Поделиться: t.me/claude_bot?start={referral_code}''',
            
            'urgency_campaign': '''⚠️ СРОЧНО: Цены растут!

📈 Через {hours_left}ч цены увеличатся на {price_increase}%
🔥 Осталось мест: {spots_left}
💎 Зафиксируйте текущую цену СЕЙЧАС!

🚀 Claude токены по старой цене!''',
            
            'urgency_phrases': [
                '⏰ Время ограничено!',
                '🔥 Не упустите шанс!',
                '⚡ Последний день акции!',
                '🎯 Эксклюзивное предложение!'
            ]
        }
    
    def _get_chinese_templates(self) -> Dict:
        """Chinese language message templates"""
        return {
            'cart_abandonment': '''🛒 您的Claude代币在等待！

购物车：{items_count}件商品，价值${cart_value:.2f}
{urgency}

🎁 特别优惠：{discount_percent}%折扣
⏰ 优惠仅剩{hours_left}小时

🚀 一键完成购买！''',
            
            'high_value_prospect': '''🤖 Claude AI独家访问！

🚫 无法访问Claude？获得完整权限！
✅ {benefits}
💡 {pain_points}

🎯 {special_offer}

⚡ 无需翻墙即时访问！''',
            
            'vip_retention': '''👑 您是我们的VIP客户！

💎 累计消费：${total_spent:.2f}
😔 我们想念您（{days_since_purchase}天前）

🎁 VIP专属优惠：
{winback_offer}

🏆 忠诚奖励：额外{loyalty_bonus}%代币''',
            
            'viral_referral': '''🚀 与朋友分享Claude访问！

您的推荐码：{referral_code}
🎁 每推荐一位：{referrer_reward}%返现
💰 朋友享受：{referee_discount}%折扣

{social_proof}

📱 分享链接：t.me/claude_bot?start={referral_code}''',
            
            'urgency_campaign': '''⚠️ 紧急：价格即将上调！

📈 {hours_left}小时后涨价{price_increase}%
🔥 剩余名额：{spots_left}
💎 立即锁定当前价格！

🚀 以旧价获得Claude代币！''',
            
            'urgency_phrases': [
                '⏰ 时间有限！',
                '🔥 机不可失！',
                '⚡ 最后一天！',
                '🎯 独家优惠！'
            ]
        }
    
    def _get_persian_templates(self) -> Dict:
        """Persian language message templates"""
        return {
            'cart_abandonment': '''🛒 توکن‌های Claude شما منتظرند!

سبد خرید: {items_count} آیتم به ارزش ${cart_value:.2f}
{urgency}

🎁 پیشنهاد ویژه: {discount_percent}% تخفیف
⏰ {hours_left} ساعت باقی‌مانده

🚀 خرید با یک کلیک!''',
            
            'high_value_prospect': '''🤖 دسترسی اختصاصی به Claude AI!

🚫 Claude مسدود است؟ دسترسی کامل بگیرید!
✅ {benefits}
💡 {pain_points}

🎯 {special_offer}

⚡ دسترسی فوری بدون فیلترشکن!''',
            
            'urgency_campaign': '''⚠️ فوری: قیمت‌ها در حال افزایش!

📈 {hours_left} ساعت دیگر قیمت {price_increase}% افزایش می‌یابد
🔥 ظرفیت باقی‌مانده: {spots_left}
💎 همین حالا قیمت فعلی را ثابت کنید!

🚀 توکن‌های Claude با قیمت قدیم!''',
            
            'urgency_phrases': [
                '⏰ زمان محدود!',
                '🔥 فرصت را از دست ندهید!',
                '⚡ آخرین روز!',
                '🎯 پیشنهاد انحصاری!'
            ]
        }
    
    def _get_arabic_templates(self) -> Dict:
        """Arabic language message templates"""
        return {
            'cart_abandonment': '''🛒 رموز Claude الخاصة بك في الانتظار!

السلة: {items_count} عناصر بقيمة ${cart_value:.2f}
{urgency}

🎁 عرض خاص: خصم {discount_percent}%
⏰ {hours_left} ساعة متبقية

🚀 اكمل الشراء بنقرة واحدة!''',
            
            'urgency_campaign': '''⚠️ عاجل: الأسعار ترتفع!

📈 خلال {hours_left} ساعة ستزداد الأسعار {price_increase}%
🔥 المقاعد المتبقية: {spots_left}
💎 احجز السعر الحالي الآن!

🚀 رموز Claude بالسعر القديم!''',
            
            'urgency_phrases': [
                '⏰ وقت محدود!',
                '🔥 لا تفوت الفرصة!',
                '⚡ اليوم الأخير!',
                '🎯 عرض حصري!'
            ]
        }
    
    def _get_english_templates(self) -> Dict:
        """English language message templates (fallback)"""
        return {
            'cart_abandonment': '''🛒 Your Claude tokens are waiting!

Cart: {items_count} items worth ${cart_value:.2f}
{urgency}

🎁 Special offer: {discount_percent}% discount
⏰ {hours_left} hours remaining

🚀 Complete purchase with one click!''',
            
            'urgency_campaign': '''⚠️ URGENT: Prices rising!

📈 In {hours_left}h prices increase by {price_increase}%
🔥 Spots remaining: {spots_left}
💎 Lock in current price NOW!

🚀 Claude tokens at old price!''',
            
            'urgency_phrases': [
                '⏰ Limited time!',
                '🔥 Don\'t miss out!',
                '⚡ Last day!',
                '🎯 Exclusive offer!'
            ]
        }
    
    async def _send_marketing_message(self, user_id: int, message: str, campaign_type: str):
        """Send marketing message to user"""
        try:
            await NotificationService.send_to_user(message, user_id)
            logger.info(f"Sent {campaign_type} message to user {user_id}")
        except Exception as e:
            logger.error(f"Failed to send marketing message to {user_id}: {e}")
    
    async def _was_recently_contacted(self, user_id: int, campaign_type: str, hours: int) -> bool:
        """Check if user was recently contacted"""
        # This would check a marketing contacts database
        # For now, we'll simulate with basic logic
        return False
    
    async def _log_marketing_contact(self, user_id: int, campaign_type: str, metadata: float):
        """Log marketing contact for analytics"""
        logger.info(f"Marketing contact logged: user={user_id}, type={campaign_type}, score={metadata}")
        # This would store in analytics database
import asyncio
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging
from aiogram.types import Update, User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from sqlalchemy import select, func

from models.user import UserDTO
from services.notification import NotificationService

logger = logging.getLogger(__name__)


class GeoTargetingService:
    """Advanced geo-targeting for restricted-access countries"""
    
    def __init__(self):
        self.target_regions = {
            'ru': {
                'name': 'Russia',
                'languages': ['ru', 'ru-ru'],
                'pricing_multiplier': 2.5,
                'preferred_crypto': 'USDT_TRC20',
                'timezone_indicators': ['Europe/Moscow', 'Asia/Vladivostok'],
                'currency_display': 'RUB'
            },
            'zh-hans': {
                'name': 'China',
                'languages': ['zh', 'zh-cn', 'zh-hans'],
                'pricing_multiplier': 3.0,
                'preferred_crypto': 'USDT_TRC20',
                'timezone_indicators': ['Asia/Shanghai', 'Asia/Beijing'],
                'currency_display': 'CNY'
            },
            'fa': {
                'name': 'Iran',
                'languages': ['fa', 'fa-ir'],
                'pricing_multiplier': 2.8,
                'preferred_crypto': 'BTC',
                'timezone_indicators': ['Asia/Tehran'],
                'currency_display': 'USD'
            },
            'ar': {
                'name': 'Middle East',
                'languages': ['ar', 'ar-sa'],
                'pricing_multiplier': 2.2,
                'preferred_crypto': 'BTC',
                'timezone_indicators': ['Asia/Riyadh', 'Asia/Dubai'],
                'currency_display': 'USD'
            }
        }
    
    async def detect_user_region(self, user: User, session: AsyncSession | Session) -> str:
        """Detect user's region based on multiple signals"""
        signals = await self._analyze_user_signals(user, session)
        
        # Weight different signals
        region_scores = {}
        
        for region_code, region_data in self.target_regions.items():
            score = 0.0
            
            # Language signal (high weight)
            if signals.get('language_code'):
                if any(lang in signals['language_code'].lower() 
                      for lang in region_data['languages']):
                    score += 0.4
            
            # Behavioral signals
            if signals.get('prefers_crypto') == region_data['preferred_crypto']:
                score += 0.2
            
            # Timing patterns (activity during regional business hours)
            if signals.get('business_hours_match', {}).get(region_code, False):
                score += 0.2
            
            # Payment inquiry patterns
            if signals.get('payment_inquiries', {}).get(region_data['preferred_crypto'], False):
                score += 0.1
            
            # Urgency indicators (common in restricted regions)
            if signals.get('urgency_score', 0) > 0.7:
                score += 0.1
            
            region_scores[region_code] = score
        
        # Return region with highest score, or 'default' if none significant
        if region_scores:
            best_region = max(region_scores.items(), key=lambda x: x[1])
            if best_region[1] > 0.3:  # Minimum confidence threshold
                return best_region[0]
        
        return 'default'
    
    async def _analyze_user_signals(self, user: User, session: AsyncSession | Session) -> Dict:
        """Analyze various user signals for geo-detection"""
        signals = {
            'language_code': user.language_code,
            'user_id': user.id,
            'username': user.username
        }
        
        # Get user interaction history
        user_activity = await self._get_user_activity(user.id, session)
        
        # Analyze activity timing patterns
        signals['business_hours_match'] = await self._analyze_timing_patterns(user_activity)
        
        # Analyze payment preferences
        signals['payment_inquiries'] = await self._analyze_payment_inquiries(user.id, session)
        
        # Calculate urgency score
        signals['urgency_score'] = await self._calculate_urgency_score(user_activity)
        
        # Detect crypto preferences
        signals['prefers_crypto'] = await self._detect_crypto_preference(user.id, session)
        
        return signals
    
    async def _get_user_activity(self, user_id: int, session: AsyncSession | Session) -> List[Dict]:
        """Get user activity from database"""
        try:
            # This would query actual user interaction logs
            # For now, we'll simulate based on existing data
            from models.user import User
            from models.buy import Buy
            
            # Get user's purchase history and activity
            stmt = select(User).where(User.telegram_id == user_id)
            user_result = await session.execute(stmt) if isinstance(session, AsyncSession) else session.execute(stmt)
            user_record = user_result.scalar_one_or_none()
            
            if not user_record:
                return []
            
            # Get purchase history for timing analysis
            buy_stmt = select(Buy).where(Buy.buyer_id == user_record.id)
            buy_result = await session.execute(buy_stmt) if isinstance(session, AsyncSession) else session.execute(buy_stmt)
            purchases = buy_result.scalars().all()
            
            activity = []
            for purchase in purchases:
                activity.append({
                    'timestamp': purchase.created_at,
                    'activity_type': 'purchase',
                    'value': float(purchase.total_price)
                })
            
            return activity
            
        except Exception as e:
            logger.error(f"Error getting user activity: {e}")
            return []
    
    async def _analyze_timing_patterns(self, activity: List[Dict]) -> Dict:
        """Analyze user activity timing patterns"""
        if not activity:
            return {}
        
        # Group activity by hour of day
        hour_counts = {}
        for act in activity:
            hour = act['timestamp'].hour
            hour_counts[hour] = hour_counts.get(hour, 0) + 1
        
        # Check if activity aligns with regional business hours
        region_matches = {}
        
        # Russian business hours (9 AM - 6 PM Moscow time)
        russian_hours = list(range(9, 18))
        ru_matches = sum(hour_counts.get(h, 0) for h in russian_hours)
        region_matches['ru'] = ru_matches > len(activity) * 0.6
        
        # Chinese business hours (9 AM - 6 PM Beijing time)
        chinese_hours = list(range(9, 18))
        zh_matches = sum(hour_counts.get(h, 0) for h in chinese_hours)
        region_matches['zh-hans'] = zh_matches > len(activity) * 0.6
        
        # Iranian business hours (8 AM - 5 PM Tehran time)
        iranian_hours = list(range(8, 17))
        fa_matches = sum(hour_counts.get(h, 0) for h in iranian_hours)
        region_matches['fa'] = fa_matches > len(activity) * 0.6
        
        return region_matches
    
    async def _analyze_payment_inquiries(self, user_id: int, session: AsyncSession | Session) -> Dict:
        """Analyze user's payment method inquiries"""
        # This would analyze chat logs for payment method mentions
        # For MVP, we'll use simpler heuristics
        
        # Simulate payment preference detection
        user_hash = hashlib.md5(str(user_id).encode()).hexdigest()
        hash_int = int(user_hash[:8], 16)
        
        inquiries = {}
        
        # Users ending in certain digits prefer certain methods
        if hash_int % 3 == 0:
            inquiries['USDT_TRC20'] = True
        elif hash_int % 3 == 1:
            inquiries['BTC'] = True
        else:
            inquiries['ETH'] = True
        
        return inquiries
    
    async def _calculate_urgency_score(self, activity: List[Dict]) -> float:
        """Calculate user urgency score (0.0 to 1.0)"""
        if not activity:
            return 0.5
        
        # Recent activity increases urgency
        now = datetime.now()
        recent_activity = [a for a in activity 
                          if (now - a['timestamp']).days <= 7]
        
        urgency_factors = []
        
        # Frequency factor
        if len(recent_activity) > 5:
            urgency_factors.append(0.3)
        elif len(recent_activity) > 2:
            urgency_factors.append(0.2)
        else:
            urgency_factors.append(0.1)
        
        # Recency factor
        if recent_activity and (now - recent_activity[-1]['timestamp']).hours < 24:
            urgency_factors.append(0.3)
        else:
            urgency_factors.append(0.1)
        
        # Value factor (higher value purchases indicate urgency)
        if recent_activity:
            avg_value = sum(a.get('value', 0) for a in recent_activity) / len(recent_activity)
            if avg_value > 50:
                urgency_factors.append(0.4)
            elif avg_value > 20:
                urgency_factors.append(0.3)
            else:
                urgency_factors.append(0.2)
        else:
            urgency_factors.append(0.1)
        
        return min(sum(urgency_factors), 1.0)
    
    async def _detect_crypto_preference(self, user_id: int, session: AsyncSession | Session) -> str:
        """Detect user's cryptocurrency preference"""
        # Simple heuristic based on user patterns
        user_hash = hashlib.md5(str(user_id).encode()).hexdigest()
        hash_int = int(user_hash[:8], 16)
        
        # Distribute preferences based on hash
        if hash_int % 10 < 6:  # 60% prefer USDT TRC20 (popular in China/Russia)
            return 'USDT_TRC20'
        elif hash_int % 10 < 8:  # 20% prefer BTC
            return 'BTC'
        else:  # 20% prefer ETH
            return 'ETH'
    
    async def apply_regional_pricing(self, base_price: float, region: str) -> Dict:
        """Apply region-specific pricing"""
        region_data = self.target_regions.get(region, {'pricing_multiplier': 2.0})
        multiplier = region_data['pricing_multiplier']
        
        regional_price = base_price * multiplier
        
        return {
            'base_price': base_price,
            'regional_price': regional_price,
            'multiplier': multiplier,
            'region': region,
            'currency_display': region_data.get('currency_display', 'USD'),
            'justification': f"Premium pricing for restricted access regions"
        }
    
    async def get_regional_payment_methods(self, region: str) -> List[str]:
        """Get preferred payment methods for region"""
        region_data = self.target_regions.get(region, {})
        preferred = region_data.get('preferred_crypto', 'USDT_TRC20')
        
        # Return ordered list with preferred method first
        all_methods = ['USDT_TRC20', 'BTC', 'ETH']
        if preferred in all_methods:
            methods = [preferred] + [m for m in all_methods if m != preferred]
        else:
            methods = all_methods
        
        return methods
    
    async def log_regional_detection(self, user_id: int, detected_region: str, confidence: float):
        """Log regional detection for analytics"""
        logger.info(f"User {user_id} detected as region '{detected_region}' with confidence {confidence:.2f}")
        
        # This could be expanded to store in analytics database
        # await self._store_detection_analytics(user_id, detected_region, confidence)
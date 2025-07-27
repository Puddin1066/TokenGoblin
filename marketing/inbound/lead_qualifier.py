import asyncio
import logging
from typing import Dict, List, Any
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class LeadQualificationEngine:
    """Lead qualification and scoring engine"""
    
    def __init__(self):
        self.qualification_criteria = {
            'engagement_score': 0.3,
            'purchase_intent': 0.25,
            'budget_capacity': 0.2,
            'decision_authority': 0.15,
            'timeline': 0.1
        }
        
        self.lead_sources = {
            'content_download': 0.8,
            'webinar_registration': 0.9,
            'demo_request': 0.95,
            'social_engagement': 0.6,
            'email_subscription': 0.5,
            'organic_search': 0.4,
            'referral': 0.7,
            'paid_ad': 0.6
        }
        
        # Behavioral scoring weights
        self.behavior_weights = {
            'page_views': 0.2,
            'time_spent': 0.25,
            'cart_adds': 0.3,
            'purchase_history': 0.15,
            'social_shares': 0.1
        }
    
    async def qualify_lead(self, lead_data: Dict) -> Dict[str, Any]:
        """Qualify a lead based on multiple criteria"""
        try:
            # Calculate qualification score
            score = await self._calculate_qualification_score(lead_data)
            
            # Determine lead grade
            grade = await self._determine_lead_grade(score)
            
            # Generate personalized recommendations
            recommendations = await self._generate_recommendations(lead_data, score)
            
            # Calculate estimated value
            estimated_value = await self._estimate_lead_value(lead_data, score)
            
            return {
                'lead_id': lead_data.get('id'),
                'user_id': lead_data.get('user_id'),
                'qualification_score': score,
                'grade': grade,
                'recommendations': recommendations,
                'next_actions': await self._suggest_next_actions(grade),
                'estimated_value': estimated_value,
                'qualification_factors': await self._get_qualification_factors(lead_data),
                'risk_factors': await self._identify_risk_factors(lead_data),
                'opportunity_factors': await self._identify_opportunity_factors(lead_data)
            }
            
        except Exception as e:
            logger.error(f"Error qualifying lead: {e}")
            return {'error': str(e)}
    
    async def _calculate_qualification_score(self, lead_data: Dict) -> float:
        """Calculate lead qualification score"""
        score = 0.0
        
        # Engagement score
        engagement_activities = lead_data.get('engagement_activities', [])
        engagement_score = min(len(engagement_activities) * 0.1, 1.0)
        score += engagement_score * self.qualification_criteria['engagement_score']
        
        # Purchase intent
        intent_signals = lead_data.get('intent_signals', [])
        intent_score = min(len(intent_signals) * 0.2, 1.0)
        score += intent_score * self.qualification_criteria['purchase_intent']
        
        # Budget capacity
        budget_indicator = lead_data.get('budget_indicator', 0)
        budget_score = min(budget_indicator / 1000, 1.0)  # Normalize to 0-1
        score += budget_score * self.qualification_criteria['budget_capacity']
        
        # Decision authority
        authority_level = lead_data.get('authority_level', 'user')
        authority_scores = {'user': 0.3, 'manager': 0.7, 'decision_maker': 1.0}
        authority_score = authority_scores.get(authority_level, 0.3)
        score += authority_score * self.qualification_criteria['decision_authority']
        
        # Timeline
        timeline_days = lead_data.get('timeline_days', 30)
        timeline_score = max(0, (30 - timeline_days) / 30)  # Closer timeline = higher score
        score += timeline_score * self.qualification_criteria['timeline']
        
        # Source bonus
        source = lead_data.get('source', 'organic_search')
        source_bonus = self.lead_sources.get(source, 0.5)
        score += source_bonus * 0.1  # 10% bonus for high-quality sources
        
        return min(score, 1.0)  # Cap at 1.0
    
    async def _determine_lead_grade(self, score: float) -> str:
        """Determine lead grade based on score"""
        if score >= 0.8:
            return 'A'
        elif score >= 0.6:
            return 'B'
        elif score >= 0.4:
            return 'C'
        else:
            return 'D'
    
    async def _generate_recommendations(self, lead_data: Dict, score: float) -> List[str]:
        """Generate personalized recommendations for lead nurturing"""
        recommendations = []
        
        if score < 0.4:
            recommendations.extend([
                'Send educational content about AI tokens',
                'Offer free consultation call',
                'Provide cost comparison calculator',
                'Share industry best practices',
                'Invite to upcoming webinar'
            ])
        elif score < 0.6:
            recommendations.extend([
                'Share relevant case studies',
                'Offer demo of token packages',
                'Send personalized pricing quote',
                'Provide ROI calculator',
                'Schedule discovery call'
            ])
        else:
            recommendations.extend([
                'Schedule sales call',
                'Send detailed proposal',
                'Offer exclusive early access',
                'Provide custom pricing',
                'Arrange technical consultation'
            ])
        
        # Add region-specific recommendations
        region = lead_data.get('region', 'en')
        if region in ['ru', 'zh-hans', 'fa', 'ar']:
            recommendations.append('Provide localized content and support')
        
        return recommendations
    
    async def _suggest_next_actions(self, grade: str) -> List[str]:
        """Suggest next actions based on lead grade"""
        actions = {
            'A': [
                'Immediate sales outreach',
                'Send detailed proposal',
                'Schedule executive demo',
                'Provide custom pricing',
                'Arrange technical consultation'
            ],
            'B': [
                'Schedule discovery call',
                'Send case studies',
                'Offer demo',
                'Provide ROI analysis',
                'Follow up with personalized content'
            ],
            'C': [
                'Send educational content',
                'Offer consultation call',
                'Provide cost calculator',
                'Share industry insights',
                'Invite to webinar'
            ],
            'D': [
                'Send welcome sequence',
                'Provide educational resources',
                'Offer free consultation',
                'Share industry best practices',
                'Build awareness through content'
            ]
        }
        
        return actions.get(grade, actions['D'])
    
    async def _estimate_lead_value(self, lead_data: Dict, score: float) -> float:
        """Estimate lead value based on various factors"""
        base_value = 100.0  # Base value for any lead
        
        # Score multiplier
        score_multiplier = 1 + (score * 2)  # 1x to 3x based on score
        
        # Budget indicator multiplier
        budget_indicator = lead_data.get('budget_indicator', 0)
        budget_multiplier = 1 + (budget_indicator / 10000)  # 1x to 2x based on budget
        
        # Authority multiplier
        authority_level = lead_data.get('authority_level', 'user')
        authority_multipliers = {'user': 1.0, 'manager': 1.5, 'decision_maker': 2.0}
        authority_multiplier = authority_multipliers.get(authority_level, 1.0)
        
        # Source multiplier
        source = lead_data.get('source', 'organic_search')
        source_multiplier = self.lead_sources.get(source, 0.5) + 0.5  # 0.5 to 1.5
        
        estimated_value = base_value * score_multiplier * budget_multiplier * authority_multiplier * source_multiplier
        
        return round(estimated_value, 2)
    
    async def _get_qualification_factors(self, lead_data: Dict) -> Dict[str, float]:
        """Get detailed qualification factors"""
        factors = {}
        
        # Engagement factor
        engagement_activities = lead_data.get('engagement_activities', [])
        factors['engagement'] = min(len(engagement_activities) * 0.1, 1.0)
        
        # Intent factor
        intent_signals = lead_data.get('intent_signals', [])
        factors['intent'] = min(len(intent_signals) * 0.2, 1.0)
        
        # Budget factor
        budget_indicator = lead_data.get('budget_indicator', 0)
        factors['budget'] = min(budget_indicator / 1000, 1.0)
        
        # Authority factor
        authority_level = lead_data.get('authority_level', 'user')
        authority_scores = {'user': 0.3, 'manager': 0.7, 'decision_maker': 1.0}
        factors['authority'] = authority_scores.get(authority_level, 0.3)
        
        # Timeline factor
        timeline_days = lead_data.get('timeline_days', 30)
        factors['timeline'] = max(0, (30 - timeline_days) / 30)
        
        return factors
    
    async def _identify_risk_factors(self, lead_data: Dict) -> List[str]:
        """Identify risk factors for the lead"""
        risk_factors = []
        
        # Low engagement risk
        engagement_activities = lead_data.get('engagement_activities', [])
        if len(engagement_activities) < 2:
            risk_factors.append('Low engagement activity')
        
        # Budget constraints
        budget_indicator = lead_data.get('budget_indicator', 0)
        if budget_indicator < 100:
            risk_factors.append('Limited budget capacity')
        
        # Authority level risk
        authority_level = lead_data.get('authority_level', 'user')
        if authority_level == 'user':
            risk_factors.append('Low decision authority')
        
        # Timeline risk
        timeline_days = lead_data.get('timeline_days', 30)
        if timeline_days > 90:
            risk_factors.append('Long purchase timeline')
        
        # Source risk
        source = lead_data.get('source', 'organic_search')
        if source in ['organic_search', 'email_subscription']:
            risk_factors.append('Low-intent source')
        
        return risk_factors
    
    async def _identify_opportunity_factors(self, lead_data: Dict) -> List[str]:
        """Identify opportunity factors for the lead"""
        opportunity_factors = []
        
        # High engagement opportunity
        engagement_activities = lead_data.get('engagement_activities', [])
        if len(engagement_activities) >= 5:
            opportunity_factors.append('High engagement activity')
        
        # Strong budget
        budget_indicator = lead_data.get('budget_indicator', 0)
        if budget_indicator > 1000:
            opportunity_factors.append('Strong budget capacity')
        
        # Decision maker
        authority_level = lead_data.get('authority_level', 'user')
        if authority_level == 'decision_maker':
            opportunity_factors.append('Decision maker')
        
        # Urgent timeline
        timeline_days = lead_data.get('timeline_days', 30)
        if timeline_days <= 30:
            opportunity_factors.append('Urgent timeline')
        
        # High-intent source
        source = lead_data.get('source', 'organic_search')
        if source in ['demo_request', 'webinar_registration']:
            opportunity_factors.append('High-intent source')
        
        # Strong intent signals
        intent_signals = lead_data.get('intent_signals', [])
        if len(intent_signals) >= 3:
            opportunity_factors.append('Strong purchase intent')
        
        return opportunity_factors
    
    async def calculate_behavioral_score(self, user_behavior: Dict) -> float:
        """Calculate behavioral score based on user behavior"""
        score = 0.0
        
        # Page views
        page_views = user_behavior.get('page_views', 0)
        page_view_score = min(page_views / 10, 1.0)  # Normalize to 0-1
        score += page_view_score * self.behavior_weights['page_views']
        
        # Time spent
        time_spent = user_behavior.get('time_spent', 0)
        time_score = min(time_spent / 600, 1.0)  # 10 minutes = 1.0
        score += time_score * self.behavior_weights['time_spent']
        
        # Cart additions
        cart_adds = user_behavior.get('cart_adds', 0)
        cart_score = min(cart_adds / 3, 1.0)  # 3+ cart adds = 1.0
        score += cart_score * self.behavior_weights['cart_adds']
        
        # Purchase history
        purchase_history = user_behavior.get('purchase_history', [])
        purchase_score = min(len(purchase_history) / 2, 1.0)  # 2+ purchases = 1.0
        score += purchase_score * self.behavior_weights['purchase_history']
        
        # Social shares
        social_shares = user_behavior.get('social_shares', 0)
        social_score = min(social_shares / 2, 1.0)  # 2+ shares = 1.0
        score += social_score * self.behavior_weights['social_shares']
        
        return min(score, 1.0)
    
    async def update_lead_score(self, lead_id: int, new_activities: List[Dict], new_signals: List[Dict]) -> float:
        """Update lead score based on new activities and signals"""
        # This would typically update the lead in the database
        # For now, we'll simulate the score update
        
        # Calculate new score based on additional activities
        activity_score = len(new_activities) * 0.05
        signal_score = len(new_signals) * 0.1
        
        # This would be added to the existing score
        score_increase = activity_score + signal_score
        
        logger.info(f"Updated lead {lead_id} score with increase of {score_increase}")
        
        return score_increase
    
    async def get_lead_segmentation(self, lead_data: Dict) -> Dict[str, Any]:
        """Segment lead based on various criteria"""
        segmentation = {
            'by_grade': lead_data.get('grade', 'D'),
            'by_region': lead_data.get('region', 'en'),
            'by_source': lead_data.get('source', 'organic_search'),
            'by_authority': lead_data.get('authority_level', 'user'),
            'by_budget': self._get_budget_segment(lead_data.get('budget_indicator', 0)),
            'by_timeline': self._get_timeline_segment(lead_data.get('timeline_days', 30))
        }
        
        return segmentation
    
    def _get_budget_segment(self, budget_indicator: float) -> str:
        """Get budget segment"""
        if budget_indicator >= 1000:
            return 'enterprise'
        elif budget_indicator >= 500:
            return 'mid-market'
        elif budget_indicator >= 100:
            return 'small-business'
        else:
            return 'startup'
    
    def _get_timeline_segment(self, timeline_days: int) -> str:
        """Get timeline segment"""
        if timeline_days <= 7:
            return 'immediate'
        elif timeline_days <= 30:
            return 'short-term'
        elif timeline_days <= 90:
            return 'medium-term'
        else:
            return 'long-term' 
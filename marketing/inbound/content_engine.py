import asyncio
import logging
from typing import Dict, List, Any
from datetime import datetime, timedelta
from openai import AsyncOpenAI
import config

logger = logging.getLogger(__name__)


class ContentGenerationEngine:
    """AI-powered content generation engine for inbound marketing"""
    
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=config.OPENROUTER_API_KEY,
            base_url="https://openrouter.ai/api/v1"
        )
        self.content_types = {
            'blog_posts': self._generate_blog_posts,
            'social_media': self._generate_social_content,
            'educational': self._generate_educational_content,
            'case_studies': self._generate_case_studies,
            'newsletters': self._generate_newsletters
        }
        
        # Target keywords for SEO
        self.target_keywords = [
            'AI tokens', 'OpenRouter', 'AI cost optimization',
            'cryptocurrency payments', 'AI development',
            'token purchasing', 'AI API costs', 'Claude AI',
            'AI token management', 'cost-effective AI'
        ]
    
    async def generate_content_calendar(self, target_audience: str, days: int = 30) -> Dict[str, List[Dict]]:
        """Generate AI-powered content calendar for specified period"""
        try:
            logger.info(f"Generating content calendar for {target_audience} over {days} days")
            
            # Identify trending topics
            trending_topics = await self._identify_trending_topics(target_audience)
            
            # Generate content plan
            content_plan = {
                'blog_posts': await self._generate_blog_posts(trending_topics, days),
                'social_content': await self._generate_social_content(trending_topics, days),
                'educational_content': await self._generate_educational_content(days),
                'case_studies': await self._generate_case_studies(days),
                'newsletters': await self._generate_newsletters(days)
            }
            
            logger.info(f"Generated content calendar with {sum(len(v) for v in content_plan.values())} content pieces")
            return content_plan
            
        except Exception as e:
            logger.error(f"Error generating content calendar: {e}")
            return {}
    
    async def _identify_trending_topics(self, target_audience: str) -> List[str]:
        """Identify trending topics in AI/crypto space"""
        prompt = f"""
        Identify the top 10 trending topics in AI and cryptocurrency that would interest {target_audience}.
        Focus on topics related to:
        - AI token usage and optimization
        - Cost-effective AI development
        - Cryptocurrency payments for AI services
        - OpenRouter and AI API usage
        - AI development best practices
        - Claude AI applications
        - Token management strategies
        
        Return only the topic names, one per line.
        """
        
        try:
            response = await self.client.chat.completions.create(
                model="anthropic/claude-3-sonnet",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500
            )
            
            topics = response.choices[0].message.content.strip().split('\n')
            return [topic.strip() for topic in topics if topic.strip()]
        except Exception as e:
            logger.error(f"Error identifying trending topics: {e}")
            # Fallback topics
            return [
                "AI Token Cost Optimization",
                "Claude AI Integration",
                "Cryptocurrency Payments for AI",
                "OpenRouter API Best Practices",
                "AI Development Cost Management"
            ]
    
    async def _generate_blog_posts(self, topics: List[str], days: int) -> List[Dict]:
        """Generate blog post outlines and content"""
        blog_posts = []
        
        # Generate 1 blog post every 3 days
        posts_needed = max(1, days // 3)
        
        for i, topic in enumerate(topics[:posts_needed]):
            try:
                post = await self._create_blog_post(topic, i + 1)
                blog_posts.append(post)
            except Exception as e:
                logger.error(f"Error generating blog post for topic {topic}: {e}")
        
        return blog_posts
    
    async def _create_blog_post(self, topic: str, post_number: int) -> Dict:
        """Create a complete blog post"""
        prompt = f"""
        Create a comprehensive blog post about "{topic}" for AI developers and crypto enthusiasts.
        
        Structure:
        1. Introduction (hook the reader)
        2. Problem statement (why this matters)
        3. Solution overview (how AI tokens help)
        4. Step-by-step guide (practical implementation)
        5. Cost analysis (token pricing and ROI)
        6. Conclusion (call to action)
        
        Include:
        - SEO keywords naturally: {', '.join(self.target_keywords)}
        - Practical examples
        - Cost-benefit analysis
        - Call to action for TokenGoblin
        - Word count: 1500-2000 words
        
        Write in an engaging, professional tone.
        """
        
        try:
            response = await self.client.chat.completions.create(
                model="anthropic/claude-3-sonnet",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=3000
            )
            
            content = response.choices[0].message.content
            
            return {
                'title': f"{topic} - Complete Guide for AI Developers",
                'content': content,
                'type': 'blog_post',
                'post_number': post_number,
                'created_at': datetime.now(),
                'target_keywords': await self._extract_keywords(topic),
                'seo_score': await self._calculate_seo_score(content),
                'readability_score': await self._calculate_readability_score(content),
                'estimated_reading_time': len(content.split()) // 200,  # 200 words per minute
                'status': 'draft'
            }
        except Exception as e:
            logger.error(f"Error creating blog post: {e}")
            return {
                'title': f"{topic} - Complete Guide",
                'content': f"Blog post about {topic} would be generated here.",
                'type': 'blog_post',
                'post_number': post_number,
                'created_at': datetime.now(),
                'target_keywords': [],
                'seo_score': 0.0,
                'readability_score': 0.0,
                'estimated_reading_time': 5,
                'status': 'draft'
            }
    
    async def _generate_social_content(self, topics: List[str], days: int) -> List[Dict]:
        """Generate social media content"""
        social_posts = []
        
        # Generate 2 social posts per day
        posts_needed = days * 2
        
        post_types = ['tip', 'question', 'case_study', 'promotion', 'educational']
        
        for i in range(posts_needed):
            topic = topics[i % len(topics)]
            post_type = post_types[i % len(post_types)]
            
            try:
                post = await self._create_social_post(topic, post_type, i + 1)
                social_posts.append(post)
            except Exception as e:
                logger.error(f"Error generating social post: {e}")
        
        return social_posts
    
    async def _create_social_post(self, topic: str, post_type: str, post_number: int) -> Dict:
        """Create social media post"""
        prompts = {
            'tip': f"💡 Pro tip: {topic} - Here's how to optimize your AI costs with tokens...",
            'question': f"🤔 Question: How do you currently handle {topic}? Share your experience!",
            'case_study': f"📊 Case Study: How one developer saved 40% on AI costs using tokens for {topic}",
            'promotion': f"🚀 Ready to optimize {topic}? Get started with TokenGoblin's AI tokens today!",
            'educational': f"📚 Learn: {topic} - Essential guide for AI developers"
        }
        
        content = prompts.get(post_type, f"Interesting content about {topic}")
        
        return {
            'content': content,
            'type': f'social_{post_type}',
            'post_number': post_number,
            'platform': 'telegram',
            'created_at': datetime.now(),
            'topic': topic,
            'engagement_score': 0.0,
            'status': 'draft'
        }
    
    async def _generate_educational_content(self, days: int) -> List[Dict]:
        """Generate educational content"""
        educational_topics = [
            "AI Token Management Best Practices",
            "Understanding Claude AI Pricing",
            "Cryptocurrency Payments for AI Services",
            "OpenRouter API Integration",
            "Cost Optimization Strategies"
        ]
        
        educational_content = []
        
        for i, topic in enumerate(educational_topics):
            try:
                content = await self._create_educational_content(topic, i + 1)
                educational_content.append(content)
            except Exception as e:
                logger.error(f"Error generating educational content: {e}")
        
        return educational_content
    
    async def _create_educational_content(self, topic: str, content_number: int) -> Dict:
        """Create educational content piece"""
        prompt = f"""
        Create educational content about "{topic}" for AI developers.
        
        Include:
        - Clear explanations
        - Step-by-step instructions
        - Best practices
        - Common mistakes to avoid
        - Practical examples
        
        Format as a comprehensive guide.
        """
        
        try:
            response = await self.client.chat.completions.create(
                model="anthropic/claude-3-sonnet",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=2000
            )
            
            return {
                'title': f"Educational Guide: {topic}",
                'content': response.choices[0].message.content,
                'type': 'educational',
                'content_number': content_number,
                'created_at': datetime.now(),
                'target_keywords': await self._extract_keywords(topic),
                'status': 'draft'
            }
        except Exception as e:
            logger.error(f"Error creating educational content: {e}")
            return {
                'title': f"Educational Guide: {topic}",
                'content': f"Educational content about {topic}",
                'type': 'educational',
                'content_number': content_number,
                'created_at': datetime.now(),
                'target_keywords': [],
                'status': 'draft'
            }
    
    async def _generate_case_studies(self, days: int) -> List[Dict]:
        """Generate case studies"""
        case_study_topics = [
            "Startup Saves 60% on AI Costs",
            "Enterprise AI Token Management",
            "Developer Success Story",
            "Cost Optimization Case Study"
        ]
        
        case_studies = []
        
        for i, topic in enumerate(case_study_topics):
            try:
                case_study = await self._create_case_study(topic, i + 1)
                case_studies.append(case_study)
            except Exception as e:
                logger.error(f"Error generating case study: {e}")
        
        return case_studies
    
    async def _create_case_study(self, topic: str, case_number: int) -> Dict:
        """Create a case study"""
        prompt = f"""
        Create a compelling case study about "{topic}".
        
        Include:
        - Problem statement
        - Solution implemented
        - Results achieved
        - ROI metrics
        - Lessons learned
        
        Make it engaging and data-driven.
        """
        
        try:
            response = await self.client.chat.completions.create(
                model="anthropic/claude-3-sonnet",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=2000
            )
            
            return {
                'title': f"Case Study: {topic}",
                'content': response.choices[0].message.content,
                'type': 'case_study',
                'case_number': case_number,
                'created_at': datetime.now(),
                'status': 'draft'
            }
        except Exception as e:
            logger.error(f"Error creating case study: {e}")
            return {
                'title': f"Case Study: {topic}",
                'content': f"Case study about {topic}",
                'type': 'case_study',
                'case_number': case_number,
                'created_at': datetime.now(),
                'status': 'draft'
            }
    
    async def _generate_newsletters(self, days: int) -> List[Dict]:
        """Generate newsletter content"""
        newsletters = []
        
        # Generate 1 newsletter per week
        newsletters_needed = max(1, days // 7)
        
        for i in range(newsletters_needed):
            try:
                newsletter = await self._create_newsletter(i + 1)
                newsletters.append(newsletter)
            except Exception as e:
                logger.error(f"Error generating newsletter: {e}")
        
        return newsletters
    
    async def _create_newsletter(self, newsletter_number: int) -> Dict:
        """Create newsletter content"""
        prompt = f"""
        Create a newsletter for AI developers and crypto enthusiasts.
        
        Include:
        - Industry updates
        - AI token tips
        - Cost optimization advice
        - Success stories
        - Call to action
        
        Make it engaging and valuable.
        """
        
        try:
            response = await self.client.chat.completions.create(
                model="anthropic/claude-3-sonnet",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1500
            )
            
            return {
                'title': f"AI Token Newsletter #{newsletter_number}",
                'content': response.choices[0].message.content,
                'type': 'newsletter',
                'newsletter_number': newsletter_number,
                'created_at': datetime.now(),
                'status': 'draft'
            }
        except Exception as e:
            logger.error(f"Error creating newsletter: {e}")
            return {
                'title': f"AI Token Newsletter #{newsletter_number}",
                'content': f"Newsletter content #{newsletter_number}",
                'type': 'newsletter',
                'newsletter_number': newsletter_number,
                'created_at': datetime.now(),
                'status': 'draft'
            }
    
    async def _extract_keywords(self, topic: str) -> List[str]:
        """Extract relevant keywords from topic"""
        # Simple keyword extraction - in production, use more sophisticated NLP
        keywords = []
        for keyword in self.target_keywords:
            if keyword.lower() in topic.lower():
                keywords.append(keyword)
        
        # Add topic-specific keywords
        keywords.extend([topic, 'AI', 'tokens', 'optimization'])
        
        return list(set(keywords))
    
    async def _calculate_seo_score(self, content: str) -> float:
        """Calculate SEO score for content"""
        score = 0.0
        
        # Check for target keywords
        content_lower = content.lower()
        for keyword in self.target_keywords:
            if keyword.lower() in content_lower:
                score += 1.0
        
        # Normalize score
        score = min(score / len(self.target_keywords) * 10, 10.0)
        
        return score
    
    async def _calculate_readability_score(self, content: str) -> float:
        """Calculate readability score"""
        # Simple readability calculation
        words = content.split()
        sentences = content.split('.')
        
        if len(sentences) == 0 or len(words) == 0:
            return 5.0
        
        avg_sentence_length = len(words) / len(sentences)
        
        # Flesch Reading Ease approximation
        if avg_sentence_length <= 10:
            return 9.0
        elif avg_sentence_length <= 15:
            return 7.0
        elif avg_sentence_length <= 20:
            return 5.0
        else:
            return 3.0 
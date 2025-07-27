import asyncio
import logging
from typing import Dict, List, Any
from openai import AsyncOpenAI
import config

logger = logging.getLogger(__name__)


class SEOOptimizer:
    """SEO optimization engine for content"""
    
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=config.OPENROUTER_API_KEY,
            base_url="https://openrouter.ai/api/v1"
        )
        self.target_keywords = [
            'AI tokens', 'OpenRouter', 'AI cost optimization',
            'cryptocurrency payments', 'AI development',
            'token purchasing', 'AI API costs', 'Claude AI',
            'AI token management', 'cost-effective AI'
        ]
        
        # SEO scoring weights
        self.seo_weights = {
            'keyword_density': 0.3,
            'title_optimization': 0.2,
            'meta_description': 0.15,
            'readability': 0.15,
            'content_structure': 0.1,
            'internal_linking': 0.1
        }
    
    async def optimize_content(self, content: str, target_keywords: List[str] = None) -> Dict[str, Any]:
        """Optimize content for SEO"""
        try:
            if target_keywords is None:
                target_keywords = self.target_keywords
            
            # Analyze current content
            analysis = await self._analyze_content(content, target_keywords)
            
            # Generate optimization suggestions
            suggestions = await self._generate_optimization_suggestions(analysis)
            
            # Create optimized version
            optimized_content = await self._create_optimized_content(content, suggestions)
            
            # Calculate final SEO score
            final_seo_score = await self._calculate_final_seo_score(optimized_content, target_keywords)
            
            return {
                'original_content': content,
                'optimized_content': optimized_content,
                'keyword_density': analysis['keyword_density'],
                'readability_score': analysis['readability_score'],
                'suggestions': suggestions,
                'seo_score': final_seo_score,
                'improvement_percentage': self._calculate_improvement_percentage(
                    analysis.get('seo_score', 0), final_seo_score
                )
            }
            
        except Exception as e:
            logger.error(f"Error optimizing content: {e}")
            return {'error': str(e)}
    
    async def _analyze_content(self, content: str, keywords: List[str]) -> Dict:
        """Analyze content for SEO metrics"""
        prompt = f"""
        Analyze this content for SEO optimization:
        
        Content: {content[:1000]}...
        
        Target keywords: {', '.join(keywords)}
        
        Provide analysis in JSON format:
        {{
            "keyword_density": {{
                "keyword": "density_percentage"
            }},
            "readability_score": "score_out_of_10",
            "content_length": "word_count",
            "missing_keywords": ["list_of_missing_keywords"],
            "suggestions": ["list_of_improvement_suggestions"],
            "seo_score": "score_out_of_10"
        }}
        """
        
        try:
            response = await self.client.chat.completions.create(
                model="anthropic/claude-3-sonnet",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1000
            )
            
            # Parse JSON response
            import json
            try:
                return json.loads(response.choices[0].message.content)
            except:
                return self._fallback_analysis(content, keywords)
        except Exception as e:
            logger.error(f"Error analyzing content: {e}")
            return self._fallback_analysis(content, keywords)
    
    def _fallback_analysis(self, content: str, keywords: List[str]) -> Dict:
        """Fallback analysis when AI analysis fails"""
        content_lower = content.lower()
        word_count = len(content.split())
        
        # Calculate keyword density
        keyword_density = {}
        for keyword in keywords:
            keyword_lower = keyword.lower()
            count = content_lower.count(keyword_lower)
            density = (count / word_count * 100) if word_count > 0 else 0
            keyword_density[keyword] = round(density, 2)
        
        # Calculate readability (simple Flesch approximation)
        sentences = content.split('.')
        avg_sentence_length = word_count / len(sentences) if sentences else 0
        
        if avg_sentence_length <= 10:
            readability_score = 9.0
        elif avg_sentence_length <= 15:
            readability_score = 7.0
        elif avg_sentence_length <= 20:
            readability_score = 5.0
        else:
            readability_score = 3.0
        
        # Find missing keywords
        missing_keywords = [kw for kw in keywords if kw.lower() not in content_lower]
        
        return {
            'keyword_density': keyword_density,
            'readability_score': readability_score,
            'content_length': word_count,
            'missing_keywords': missing_keywords,
            'suggestions': [
                'Add more target keywords naturally',
                'Improve content structure with headings',
                'Add meta description',
                'Include internal links'
            ],
            'seo_score': 6.0
        }
    
    async def _generate_optimization_suggestions(self, analysis: Dict) -> List[str]:
        """Generate specific optimization suggestions"""
        prompt = f"""
        Based on this SEO analysis, provide specific optimization suggestions:
        
        Analysis: {analysis}
        
        Provide 5 specific, actionable suggestions to improve SEO performance.
        Focus on:
        1. Keyword optimization
        2. Content structure
        3. Readability improvements
        4. Call-to-action optimization
        5. User engagement
        
        Return as a numbered list.
        """
        
        try:
            response = await self.client.chat.completions.create(
                model="anthropic/claude-3-sonnet",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500
            )
            
            return response.choices[0].message.content.strip().split('\n')
        except Exception as e:
            logger.error(f"Error generating optimization suggestions: {e}")
            return [
                "Add more target keywords naturally throughout the content",
                "Improve content structure with clear headings and subheadings",
                "Add a compelling meta description",
                "Include relevant internal and external links",
                "Optimize for readability and user engagement"
            ]
    
    async def _create_optimized_content(self, content: str, suggestions: List[str]) -> str:
        """Create optimized version of content"""
        prompt = f"""
        Optimize this content based on the following suggestions:
        
        Original content: {content}
        
        Optimization suggestions:
        {chr(10).join(f"- {suggestion}" for suggestion in suggestions)}
        
        Create an optimized version that:
        1. Incorporates the suggestions naturally
        2. Maintains the original message and tone
        3. Improves SEO without keyword stuffing
        4. Enhances readability and engagement
        
        Return only the optimized content.
        """
        
        try:
            response = await self.client.chat.completions.create(
                model="anthropic/claude-3-sonnet",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=3000
            )
            
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error creating optimized content: {e}")
            return content  # Return original if optimization fails
    
    async def _calculate_final_seo_score(self, content: str, keywords: List[str]) -> float:
        """Calculate final SEO score for optimized content"""
        score = 0.0
        
        # Keyword density score
        content_lower = content.lower()
        word_count = len(content.split())
        
        keyword_score = 0.0
        for keyword in keywords:
            keyword_lower = keyword.lower()
            count = content_lower.count(keyword_lower)
            density = (count / word_count * 100) if word_count > 0 else 0
            if 0.5 <= density <= 2.5:  # Optimal keyword density
                keyword_score += 1.0
            elif density > 0:  # Some presence
                keyword_score += 0.5
        
        score += (keyword_score / len(keywords)) * self.seo_weights['keyword_density'] * 10
        
        # Readability score
        sentences = content.split('.')
        avg_sentence_length = word_count / len(sentences) if sentences else 0
        
        if avg_sentence_length <= 15:
            readability_score = 8.0
        elif avg_sentence_length <= 20:
            readability_score = 6.0
        else:
            readability_score = 4.0
        
        score += readability_score * self.seo_weights['readability']
        
        # Content structure score
        if any(heading in content for heading in ['#', '##', '###', '**', '__']):
            score += 8.0 * self.seo_weights['content_structure']
        
        # Internal linking score
        if 'http' in content or 'www' in content:
            score += 7.0 * self.seo_weights['internal_linking']
        
        return min(score, 10.0)  # Cap at 10
    
    def _calculate_improvement_percentage(self, original_score: float, final_score: float) -> float:
        """Calculate improvement percentage"""
        if original_score == 0:
            return 100.0
        
        improvement = ((final_score - original_score) / original_score) * 100
        return max(improvement, 0.0)
    
    async def optimize_title(self, title: str, target_keywords: List[str]) -> Dict[str, Any]:
        """Optimize title for SEO"""
        prompt = f"""
        Optimize this title for SEO:
        
        Original title: {title}
        Target keywords: {', '.join(target_keywords)}
        
        Create an optimized title that:
        1. Includes target keywords naturally
        2. Is compelling and clickable
        3. Stays under 60 characters
        4. Maintains the original message
        
        Return only the optimized title.
        """
        
        try:
            response = await self.client.chat.completions.create(
                model="anthropic/claude-3-sonnet",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=100
            )
            
            optimized_title = response.choices[0].message.content.strip()
            
            return {
                'original_title': title,
                'optimized_title': optimized_title,
                'character_count': len(optimized_title),
                'keyword_inclusion': any(kw.lower() in optimized_title.lower() for kw in target_keywords)
            }
        except Exception as e:
            logger.error(f"Error optimizing title: {e}")
            return {
                'original_title': title,
                'optimized_title': title,
                'character_count': len(title),
                'keyword_inclusion': False
            }
    
    async def generate_meta_description(self, content: str, target_keywords: List[str]) -> str:
        """Generate SEO-optimized meta description"""
        prompt = f"""
        Generate an SEO-optimized meta description for this content:
        
        Content: {content[:500]}...
        Target keywords: {', '.join(target_keywords)}
        
        Requirements:
        1. Include target keywords naturally
        2. Stay under 160 characters
        3. Be compelling and descriptive
        4. Include a call to action
        
        Return only the meta description.
        """
        
        try:
            response = await self.client.chat.completions.create(
                model="anthropic/claude-3-sonnet",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Error generating meta description: {e}")
            return f"Learn about {target_keywords[0] if target_keywords else 'AI tokens'} and optimize your AI development costs."
    
    async def suggest_content_structure(self, content: str) -> List[str]:
        """Suggest content structure improvements"""
        prompt = f"""
        Analyze this content and suggest structural improvements:
        
        Content: {content[:1000]}...
        
        Suggest improvements for:
        1. Headings and subheadings
        2. Content organization
        3. Paragraph structure
        4. Call-to-action placement
        5. Visual elements
        
        Return as a numbered list.
        """
        
        try:
            response = await self.client.chat.completions.create(
                model="anthropic/claude-3-sonnet",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500
            )
            
            return response.choices[0].message.content.strip().split('\n')
        except Exception as e:
            logger.error(f"Error suggesting content structure: {e}")
            return [
                "Add clear headings and subheadings",
                "Organize content into logical sections",
                "Use bullet points for better readability",
                "Include a clear call-to-action",
                "Add relevant images or diagrams"
            ] 
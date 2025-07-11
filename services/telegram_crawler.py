"""
Telegram Crawler Service for automated prospect discovery
"""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any
from telethon import TelegramClient, events
from telethon.tl.functions.messages import GetHistoryRequest
from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.types import ChannelParticipantsSearch, User
from telethon.errors import FloodWaitError, ChannelPrivateError, ChatAdminRequiredError

from config import config
from models.prospect import Prospect, ProspectDTO
from services.database import DatabaseService
from services.lead_qualification import LeadQualificationService

logger = logging.getLogger(__name__)


class TelegramCrawler:
    """Service for crawling Telegram groups and finding prospects"""
    
    def __init__(self):
        self.client = TelegramClient(
            f"{config.system.data_dir}/sessions/crawler",
            config.telegram.api_id,
            config.telegram.api_hash
        )
        self.db_service = DatabaseService()
        self.lead_qualifier = LeadQualificationService()
        
        # Rate limiting
        self.daily_contact_limit = config.marketing.daily_prospect_limit
        self.messages_per_hour = config.marketing.messages_per_hour
        self.last_contact_time = datetime.now()
        self.contacts_today = 0
        
        # Target groups
        self.target_groups = config.marketing.target_groups
        
        # AI/ML keywords for qualification
        self.ai_keywords = [
            'AI', 'ML', 'machine learning', 'deep learning', 'neural network',
            'OpenAI', 'GPT', 'chatbot', 'NLP', 'artificial intelligence',
            'developer', 'engineer', 'startup', 'founder', 'CTO', 'tech lead',
            'data science', 'python', 'tensorflow', 'pytorch', 'hugging face',
            'LLM', 'transformer', 'API', 'bot development', 'automation'
        ]
        
        # Exclusion keywords
        self.exclude_keywords = [
            'spam', 'scam', 'fake', 'bot', 'promotional', 'advertisement',
            'selling', 'buy now', 'crypto pump', 'investment scheme'
        ]
    
    async def start(self):
        """Start the Telegram crawler"""
        if not config.features.enable_telegram_crawler:
            logger.info("Telegram crawler disabled in configuration")
            return
            
        try:
            await self.client.start(phone=config.telegram.phone_number)
            logger.info("Telegram crawler started successfully")
        except Exception as e:
            logger.error(f"Failed to start Telegram crawler: {e}")
            raise
    
    async def stop(self):
        """Stop the Telegram crawler"""
        await self.client.disconnect()
        logger.info("Telegram crawler stopped")
    
    async def crawl_groups(self) -> List[ProspectDTO]:
        """Crawl target groups for potential prospects"""
        if not await self.check_rate_limits():
            logger.warning("Rate limits exceeded, skipping crawl")
            return []
        
        all_prospects = []
        
        for group_name in self.target_groups:
            try:
                logger.info(f"Crawling group: {group_name}")
                prospects = await self.crawl_single_group(group_name)
                all_prospects.extend(prospects)
                
                # Rate limiting between groups
                await asyncio.sleep(60)  # 1 minute between groups
                
            except Exception as e:
                logger.error(f"Error crawling group {group_name}: {e}")
                continue
        
        logger.info(f"Found {len(all_prospects)} prospects across all groups")
        return all_prospects
    
    async def crawl_single_group(self, group_name: str) -> List[ProspectDTO]:
        """Crawl a single group for prospects"""
        try:
            # Get group entity
            group = await self.client.get_entity(group_name)
            
            # Get participants
            participants = await self.get_group_participants(group)
            
            # Qualify prospects
            qualified_prospects = []
            for participant in participants:
                if await self.qualify_participant(participant, group_name):
                    prospect_dto = await self.create_prospect_dto(participant, group_name)
                    qualified_prospects.append(prospect_dto)
            
            logger.info(f"Qualified {len(qualified_prospects)} prospects from {group_name}")
            return qualified_prospects
            
        except ChannelPrivateError:
            logger.error(f"Cannot access private group: {group_name}")
            return []
        except ChatAdminRequiredError:
            logger.error(f"Admin privileges required for group: {group_name}")
            return []
        except Exception as e:
            logger.error(f"Error crawling group {group_name}: {e}")
            return []
    
    async def get_group_participants(self, group) -> List[User]:
        """Get participants from a group"""
        try:
            participants = []
            offset = 0
            limit = 100
            
            while True:
                result = await self.client(GetParticipantsRequest(
                    channel=group,
                    filter=ChannelParticipantsSearch(''),
                    offset=offset,
                    limit=limit,
                    hash=0
                ))
                
                if not result.users:
                    break
                
                participants.extend([u for u in result.users if isinstance(u, User)])
                offset += limit
                
                # Rate limiting
                await asyncio.sleep(5)
                
                # Limit to prevent overwhelming
                if len(participants) >= 1000:
                    break
            
            return participants
            
        except FloodWaitError as e:
            logger.warning(f"Rate limited, waiting {e.seconds} seconds")
            await asyncio.sleep(e.seconds)
            return []
        except Exception as e:
            logger.error(f"Error getting group participants: {e}")
            return []
    
    async def qualify_participant(self, participant: User, source_group: str) -> bool:
        """Qualify a participant as a potential prospect"""
        try:
            # Skip if already in database
            if await self.db_service.prospect_exists(participant.id):
                return False
            
            # Skip if no bio or username
            if not participant.bio and not participant.username:
                return False
            
            # Skip if bot
            if participant.bot:
                return False
            
            # Skip if deleted account
            if participant.deleted:
                return False
            
            # Check for AI/ML indicators
            if not await self.has_ai_ml_indicators(participant):
                return False
            
            # Check for exclusion keywords
            if await self.has_exclusion_keywords(participant):
                return False
            
            # Check activity level
            if not await self.is_active_user(participant):
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error qualifying participant {participant.id}: {e}")
            return False
    
    async def has_ai_ml_indicators(self, participant: User) -> bool:
        """Check if participant shows AI/ML interest"""
        text_to_check = []
        
        if participant.bio:
            text_to_check.append(participant.bio.lower())
        
        if participant.username:
            text_to_check.append(participant.username.lower())
        
        if participant.first_name:
            text_to_check.append(participant.first_name.lower())
        
        if participant.last_name:
            text_to_check.append(participant.last_name.lower())
        
        combined_text = ' '.join(text_to_check)
        
        # Check for AI/ML keywords
        return any(keyword.lower() in combined_text for keyword in self.ai_keywords)
    
    async def has_exclusion_keywords(self, participant: User) -> bool:
        """Check if participant has exclusion keywords"""
        text_to_check = []
        
        if participant.bio:
            text_to_check.append(participant.bio.lower())
        
        if participant.username:
            text_to_check.append(participant.username.lower())
        
        combined_text = ' '.join(text_to_check)
        
        # Check for exclusion keywords
        return any(keyword.lower() in combined_text for keyword in self.exclude_keywords)
    
    async def is_active_user(self, participant: User) -> bool:
        """Check if user is active"""
        try:
            # Check if user was online recently
            if hasattr(participant, 'status') and participant.status:
                # Consider user active if online in last 30 days
                if hasattr(participant.status, 'was_online'):
                    last_online = participant.status.was_online
                    if last_online:
                        cutoff = datetime.now() - timedelta(days=30)
                        return last_online > cutoff
            
            # Default to true if we can't determine
            return True
            
        except Exception:
            return True
    
    async def create_prospect_dto(self, participant: User, source_group: str) -> ProspectDTO:
        """Create a ProspectDTO from a Telegram user"""
        prospect = ProspectDTO(
            telegram_id=participant.id,
            username=participant.username,
            first_name=participant.first_name,
            last_name=participant.last_name,
            bio=participant.bio,
            source_group=source_group,
            discovery_method='telegram_crawler',
            status='new'
        )
        
        # Calculate qualification score
        prospect.qualification_score = await self.lead_qualifier.calculate_lead_score(prospect)
        
        # Determine segment
        if prospect.qualification_score >= 80:
            prospect.segment = 'hot'
        elif prospect.qualification_score >= 60:
            prospect.segment = 'warm'
        elif prospect.qualification_score >= 40:
            prospect.segment = 'cold'
        else:
            prospect.segment = 'low_priority'
        
        return prospect
    
    async def check_rate_limits(self) -> bool:
        """Check if we're within rate limits"""
        now = datetime.now()
        
        # Reset daily counter if new day
        if now.date() != self.last_contact_time.date():
            self.contacts_today = 0
        
        # Check daily limit
        if self.contacts_today >= self.daily_contact_limit:
            return False
        
        # Check hourly limit
        hour_ago = now - timedelta(hours=1)
        if self.last_contact_time > hour_ago:
            # Calculate how many contacts we can make this hour
            contacts_this_hour = min(self.messages_per_hour, 
                                   self.daily_contact_limit - self.contacts_today)
            if contacts_this_hour <= 0:
                return False
        
        return True
    
    async def save_prospects(self, prospects: List[ProspectDTO]):
        """Save prospects to database"""
        try:
            saved_count = 0
            for prospect in prospects:
                if await self.db_service.save_prospect(prospect):
                    saved_count += 1
            
            logger.info(f"Saved {saved_count} new prospects to database")
            return saved_count
            
        except Exception as e:
            logger.error(f"Error saving prospects: {e}")
            return 0
    
    async def get_recent_messages(self, group_name: str, limit: int = 100) -> List[Dict]:
        """Get recent messages from a group for context analysis"""
        try:
            group = await self.client.get_entity(group_name)
            
            messages = []
            async for message in self.client.iter_messages(group, limit=limit):
                if message.text:
                    messages.append({
                        'id': message.id,
                        'text': message.text,
                        'date': message.date,
                        'sender_id': message.sender_id,
                        'views': message.views,
                        'replies': message.replies.replies if message.replies else 0
                    })
            
            return messages
            
        except Exception as e:
            logger.error(f"Error getting recent messages from {group_name}: {e}")
            return []
    
    async def analyze_group_activity(self, group_name: str) -> Dict[str, Any]:
        """Analyze group activity and engagement"""
        try:
            messages = await self.get_recent_messages(group_name, 500)
            
            if not messages:
                return {}
            
            # Calculate activity metrics
            total_messages = len(messages)
            unique_senders = len(set(m['sender_id'] for m in messages if m['sender_id']))
            avg_views = sum(m['views'] or 0 for m in messages) / total_messages
            avg_replies = sum(m['replies'] or 0 for m in messages) / total_messages
            
            # Analyze content
            ai_related_messages = 0
            for message in messages:
                if any(keyword.lower() in message['text'].lower() 
                      for keyword in self.ai_keywords):
                    ai_related_messages += 1
            
            return {
                'total_messages': total_messages,
                'unique_senders': unique_senders,
                'avg_views': avg_views,
                'avg_replies': avg_replies,
                'ai_related_percentage': (ai_related_messages / total_messages) * 100,
                'activity_score': min(100, (unique_senders / total_messages) * 100)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing group activity for {group_name}: {e}")
            return {}
    
    async def update_contact_stats(self):
        """Update contact statistics"""
        self.contacts_today += 1
        self.last_contact_time = datetime.now()
    
    async def get_daily_stats(self) -> Dict[str, Any]:
        """Get daily crawling statistics"""
        return {
            'contacts_today': self.contacts_today,
            'daily_limit': self.daily_contact_limit,
            'remaining_contacts': self.daily_contact_limit - self.contacts_today,
            'last_contact_time': self.last_contact_time.isoformat(),
            'target_groups': self.target_groups
        }
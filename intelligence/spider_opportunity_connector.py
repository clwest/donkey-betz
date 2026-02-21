"""
Spider Opportunity Connector - Real-time income opportunities from spider network
===============================================================================

This module connects the Decision Command interface to the spider network to provide
real-time income opportunities. It acts as a bridge between the spider intelligence
system and the AIIncomeBuilder to deliver personalized, actionable opportunities.

Features:
- Real-time opportunity fetching from spider network
- Opportunity filtering and scoring based on user profile
- Integration with AIIncomeBuilder analysis
- Caching and performance optimization
- Error handling and fallback mechanisms
"""

import json
import logging
import os
import redis.asyncio as aioredis
from typing import Dict, List, Optional
from datetime import datetime, timezone, timedelta
from dataclasses import dataclass
import hashlib

logger = logging.getLogger(__name__)


def _heuristic_quality_score(data: Dict) -> float:
    """
    Session 1062: Calculate quality score from available opportunity attributes.

    Instead of defaulting to 0.5 (which made all 11,500+ opportunities score 50),
    this uses real signals from the spider data to differentiate opportunities.

    Returns a score between 0.3 and 0.95.
    """
    score = 0.35  # Base score

    # Has budget info (+0.15)
    budget = data.get('budget', {})
    if isinstance(budget, dict):
        if budget.get('min') or budget.get('max'):
            score += 0.15
    elif isinstance(budget, str) and budget.strip():
        score += 0.10

    # Has meaningful description (+0.10)
    desc = data.get('description', data.get('summary', ''))
    if len(desc) > 200:
        score += 0.10
    elif len(desc) > 50:
        score += 0.05

    # Has skills listed (+0.10)
    skills = data.get('skills_required', data.get('skills', []))
    if isinstance(skills, str):
        skills = [s.strip() for s in skills.split(',') if s.strip()]
    if isinstance(skills, list) and len(skills) >= 3:
        score += 0.10
    elif isinstance(skills, list) and len(skills) >= 1:
        score += 0.05

    # High urgency (+0.05)
    if data.get('urgency') == 'high':
        score += 0.05

    # Client rating (+0.10)
    try:
        rating = data.get('client_rating')
        if rating is not None and float(rating) >= 4.5:
            score += 0.10
        elif rating is not None and float(rating) >= 4.0:
            score += 0.05
    except (ValueError, TypeError):
        pass

    # Has specific experience level set (+0.05)
    if data.get('experience_level') and data['experience_level'] != 'beginner':
        score += 0.05

    # Has deadline (+0.05) — implies active/real posting
    if data.get('deadline'):
        score += 0.05

    return min(0.95, score)


@dataclass
class SpiderOpportunity:
    """Structured opportunity from spider network"""
    id: str
    title: str
    description: str
    platform: str
    opportunity_type: str

    # Financial details
    budget_min: Optional[float] = None
    budget_max: Optional[float] = None
    estimated_earnings: Optional[float] = None
    hourly_rate: Optional[float] = None

    # Requirements
    skills_required: List[str] = None
    experience_level: str = 'beginner'
    deadline: Optional[str] = None

    # Metadata
    urgency: str = 'medium'
    quality_score: float = 0.5
    competition_level: str = 'medium'
    client_rating: Optional[float] = None

    # Spider data
    spider_source: str = ''
    discovered_at: datetime = None
    expires_at: Optional[datetime] = None
    raw_data: Dict = None

    def __post_init__(self):
        if self.skills_required is None:
            self.skills_required = []
        if self.discovered_at is None:
            self.discovered_at = datetime.now(timezone.utc)
        if self.raw_data is None:
            self.raw_data = {}


class SpiderOpportunityConnector:
    """Connects to spider network to fetch real-time income opportunities"""

    def __init__(self, redis_url: str = None):
        self.redis_url = redis_url or os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
        self.redis = None
        self.cache_timeout = 300  # 5 minutes
        self.opportunity_cache = {}
        self.last_fetch_time = None

        # Configuration
        self.max_opportunities = 50
        self.quality_threshold = 0.3
        self.platforms_enabled = [
            'upwork', 'fiverr', 'freelancer', 'toptal',
            'contently', 'copywriter', 'scripted'
        ]

    async def initialize(self):
        """Initialize Redis connection"""
        try:
            self.redis = await aioredis.from_url(self.redis_url)
            await self.redis.ping()
            logger.info("Spider opportunity connector initialized")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize spider connector: {e}")
            return False

    async def get_opportunities_for_user(self, user_profile: Dict) -> List[SpiderOpportunity]:
        """Get personalized opportunities for a user from spider network"""
        try:
            # Check cache first
            cache_key = self._generate_cache_key(user_profile)
            cached_opportunities = await self._get_cached_opportunities(cache_key)

            if cached_opportunities and self._is_cache_valid():
                logger.info(f"Returning {len(cached_opportunities)} cached opportunities")
                return cached_opportunities

            # Fetch fresh opportunities
            opportunities = await self._fetch_fresh_opportunities(user_profile)

            # Cache the results
            await self._cache_opportunities(cache_key, opportunities)

            logger.info(f"Fetched {len(opportunities)} fresh opportunities from spider network")
            return opportunities

        except Exception as e:
            logger.error(f"Error getting opportunities for user: {e}")
            return await self._get_fallback_opportunities(user_profile)

    async def _fetch_fresh_opportunities(self, user_profile: Dict) -> List[SpiderOpportunity]:
        """Fetch fresh opportunities from spider network"""
        opportunities = []

        try:
            if not self.redis:
                await self.initialize()

            # Get opportunities from different spider channels
            spider_channels = [
                'spider:opportunities:freelance',
                'spider:opportunities:content',
                'spider:opportunities:automation',
                'spider:opportunities:tutoring'
            ]

            for channel in spider_channels:
                try:
                    # Get latest opportunities from this channel
                    channel_opps = await self._fetch_from_channel(channel, user_profile)
                    opportunities.extend(channel_opps)
                except Exception as e:
                    logger.warning(f"Failed to fetch from channel {channel}: {e}")

            # Filter and score opportunities
            filtered_opportunities = await self._filter_and_score_opportunities(
                opportunities, user_profile
            )

            # Sort by relevance and take top opportunities
            sorted_opportunities = sorted(
                filtered_opportunities,
                key=lambda x: x.quality_score,
                reverse=True
            )

            # CRITICAL FIX: Save opportunities to database
            top_opportunities = sorted_opportunities[:self.max_opportunities]
            try:
                # Get user from profile (could be 'user' object or 'user_id')
                user = user_profile.get('user')
                if not user and user_profile.get('user_id'):
                    # Fetch user from database
                    from django.contrib.auth import get_user_model
                    from channels.db import database_sync_to_async

                    @database_sync_to_async
                    def get_user_by_id(user_id):
                        User = get_user_model()
                        return User.objects.filter(id=user_id).first()

                    user = await get_user_by_id(user_profile['user_id'])

                if user:
                    saved_count = await save_opportunities_batch(top_opportunities, user)
                    logger.info(f"✅ Saved {saved_count} opportunities to database")
                else:
                    logger.warning("No user provided in profile - opportunities not saved to database")
            except Exception as e:
                logger.error(f"Failed to save opportunities to database: {e}")

            self.last_fetch_time = datetime.now(timezone.utc)
            return top_opportunities

        except Exception as e:
            logger.error(f"Error fetching fresh opportunities: {e}")
            return []

    async def _fetch_from_channel(self, channel: str, user_profile: Dict) -> List[SpiderOpportunity]:
        """Fetch opportunities from a specific spider channel"""
        opportunities = []

        try:
            # Get recent data from Redis list/stream
            raw_data = await self.redis.lrange(channel, 0, 20)

            for item in raw_data:
                try:
                    opp_data = json.loads(item)
                    opportunity = await self._parse_spider_opportunity(opp_data, channel)
                    if opportunity:
                        opportunities.append(opportunity)
                except Exception as e:
                    logger.warning(f"Failed to parse opportunity from {channel}: {e}")

            # Also check for stream data if available
            try:
                stream_data = await self.redis.xrevrange(f"{channel}:stream", count=10)
                for stream_id, fields in stream_data:
                    try:
                        opp_data = {k.decode(): v.decode() for k, v in fields.items()}
                        # Parse JSON fields
                        for key in ['skills_required', 'metadata']:
                            if key in opp_data:
                                opp_data[key] = json.loads(opp_data[key])

                        opportunity = await self._parse_spider_opportunity(opp_data, channel)
                        if opportunity:
                            opportunities.append(opportunity)
                    except Exception as e:
                        logger.warning(f"Failed to parse stream data from {channel}: {e}")
            except Exception:
                # Stream might not exist, which is fine
                pass

        except Exception as e:
            logger.error(f"Error fetching from channel {channel}: {e}")

        return opportunities

    async def _parse_spider_opportunity(self, data: Dict, channel: str) -> Optional[SpiderOpportunity]:
        """Parse raw spider data into SpiderOpportunity object"""
        try:
            # Extract basic info
            opp_id = data.get('id', f"spider_{int(datetime.now().timestamp())}")
            title = data.get('title', data.get('name', 'Opportunity'))
            description = data.get('description', data.get('summary', ''))

            # Determine platform from channel or data
            platform = data.get('platform', self._extract_platform_from_channel(channel))

            # Determine opportunity type
            opp_type = data.get('type', self._infer_opportunity_type(title, description, channel))

            # Extract financial info
            budget_range = data.get('budget', {})
            if isinstance(budget_range, str):
                budget_min, budget_max = self._parse_budget_string(budget_range)
            else:
                budget_min = budget_range.get('min')
                budget_max = budget_range.get('max')

            # Extract skills
            skills = data.get('skills_required', data.get('skills', []))
            if isinstance(skills, str):
                skills = [s.strip() for s in skills.split(',')]

            # Create opportunity
            opportunity = SpiderOpportunity(
                id=opp_id,
                title=title,
                description=description,
                platform=platform,
                opportunity_type=opp_type,
                budget_min=budget_min,
                budget_max=budget_max,
                skills_required=skills,
                experience_level=data.get('experience_level', 'beginner'),
                deadline=data.get('deadline'),
                urgency=data.get('urgency', 'medium'),
                quality_score=data.get('quality_score') or _heuristic_quality_score(data),
                competition_level=data.get('competition_level', 'medium'),
                client_rating=data.get('client_rating'),
                spider_source=channel,
                raw_data=data
            )

            return opportunity

        except Exception as e:
            logger.error(f"Error parsing spider opportunity: {e}")
            return None

    def _extract_platform_from_channel(self, channel: str) -> str:
        """Extract platform name from channel"""
        if 'freelance' in channel:
            return 'upwork'
        elif 'content' in channel:
            return 'contently'
        elif 'automation' in channel:
            return 'zapier'
        elif 'tutoring' in channel:
            return 'preply'
        else:
            return 'general'

    def _infer_opportunity_type(self, title: str, description: str, channel: str) -> str:
        """Infer opportunity type from content"""
        content = f"{title} {description}".lower()

        if any(keyword in content for keyword in ['write', 'content', 'blog', 'article']):
            return 'content_creation'
        elif any(keyword in content for keyword in ['automat', 'zapier', 'workflow']):
            return 'ai_automation'
        elif any(keyword in content for keyword in ['teach', 'tutor', 'lesson', 'education']):
            return 'ai_tutoring'
        elif any(keyword in content for keyword in ['design', 'graphic', 'visual']):
            return 'digital_products'
        elif any(keyword in content for keyword in ['consult', 'advice', 'strategy']):
            return 'consulting'
        else:
            return 'freelance_services'

    def _parse_budget_string(self, budget_str: str) -> tuple:
        """Parse budget string like '$500-$2000' or '$50/hour'"""
        try:
            # Remove currency symbols and clean up
            cleaned = budget_str.replace('$', '').replace(',', '').strip()

            if '-' in cleaned:
                # Range like "500-2000"
                parts = cleaned.split('-')
                return float(parts[0]), float(parts[1])
            elif '/' in cleaned:
                # Hourly rate like "50/hour"
                rate = float(cleaned.split('/')[0])
                return rate, rate * 40  # Assume 40 hours max
            else:
                # Single value
                value = float(cleaned)
                return value, value
        except Exception:
            return None, None

    async def _filter_and_score_opportunities(self, opportunities: List[SpiderOpportunity], user_profile: Dict) -> List[SpiderOpportunity]:
        """Filter and score opportunities based on user profile"""
        filtered = []

        user_skills = set(skill.lower() for skill in user_profile.get('skills', []))
        user_balance = user_profile.get('currentBalance', 0)
        user_skill_level = user_profile.get('skillLevel', 'beginner')
        user_hours = user_profile.get('availableHours', 10)

        for opp in opportunities:
            # Basic quality filter
            if opp.quality_score < self.quality_threshold:
                continue

            # Calculate match score
            score = await self._calculate_match_score(opp, user_profile)
            opp.quality_score = score

            # Only include opportunities with decent scores
            if score > 0.3:
                filtered.append(opp)

        return filtered

    async def _calculate_match_score(self, opportunity: SpiderOpportunity, user_profile: Dict) -> float:
        """Calculate how well an opportunity matches a user profile"""
        score = 0.5  # Base score

        try:
            user_skills = set(skill.lower() for skill in user_profile.get('skills', []))
            user_skill_level = user_profile.get('skillLevel', 'beginner')
            user_hours = user_profile.get('availableHours', 10)

            # Skill matching (30% weight)
            required_skills = set(skill.lower() for skill in opportunity.skills_required)
            if required_skills:
                skill_match = len(user_skills & required_skills) / len(required_skills)
                score += skill_match * 0.3
            else:
                score += 0.15  # Bonus for no specific skills required

            # Experience level matching (20% weight)
            level_mapping = {'beginner': 1, 'intermediate': 2, 'advanced': 3, 'expert': 4}
            user_level = level_mapping.get(user_skill_level, 1)
            opp_level = level_mapping.get(opportunity.experience_level, 1)

            if user_level >= opp_level:
                score += 0.2
            elif user_level == opp_level - 1:
                score += 0.1  # Slight stretch is ok

            # Budget compatibility (15% weight)
            if opportunity.budget_min and opportunity.budget_min > 0:
                if opportunity.budget_min >= 100:  # Good paying opportunity
                    score += 0.15
                elif opportunity.budget_min >= 50:
                    score += 0.1

            # Time commitment (10% weight)
            if user_hours >= 20:
                score += 0.1
            elif user_hours >= 10:
                score += 0.05

            # Urgency factor (10% weight)
            if opportunity.urgency == 'high':
                score += 0.1
            elif opportunity.urgency == 'medium':
                score += 0.05

            # Platform preference (15% weight)
            platform_scores = {
                'upwork': 0.15, 'fiverr': 0.12, 'freelancer': 0.1,
                'contently': 0.14, 'toptal': 0.15, 'preply': 0.13
            }
            score += platform_scores.get(opportunity.platform.lower(), 0.05)

            # Ensure score is within bounds
            return max(0.1, min(0.95, score))

        except Exception as e:
            logger.error(f"Error calculating match score: {e}")
            return 0.3

    async def _get_fallback_opportunities(self, user_profile: Dict) -> List[SpiderOpportunity]:
        """Generate fallback opportunities when spider network is unavailable"""
        fallback_opportunities = []

        # Create some realistic demo opportunities
        demo_opportunities = [
            {
                'id': 'demo_content_1',
                'title': 'Content Writer Needed for Tech Blog',
                'description': 'Looking for experienced content writer to create technical articles',
                'platform': 'upwork',
                'type': 'content_creation',
                'budget_min': 150,
                'budget_max': 500,
                'skills_required': ['writing', 'research', 'technology'],
                'urgency': 'medium'
            },
            {
                'id': 'demo_automation_1',
                'title': 'Zapier Automation Expert Needed',
                'description': 'Need help setting up automated workflows for small business',
                'platform': 'fiverr',
                'type': 'ai_automation',
                'budget_min': 100,
                'budget_max': 300,
                'skills_required': ['automation', 'zapier', 'workflows'],
                'urgency': 'high'
            },
            {
                'id': 'demo_tutor_1',
                'title': 'Online Math Tutor - Immediate Start',
                'description': 'Teach math to high school students using online tools',
                'platform': 'preply',
                'type': 'ai_tutoring',
                'budget_min': 25,
                'budget_max': 50,
                'skills_required': ['mathematics', 'teaching', 'communication'],
                'urgency': 'high'
            }
        ]

        for demo_data in demo_opportunities:
            try:
                opportunity = SpiderOpportunity(
                    id=demo_data['id'],
                    title=demo_data['title'],
                    description=demo_data['description'],
                    platform=demo_data['platform'],
                    opportunity_type=demo_data['type'],
                    budget_min=demo_data['budget_min'],
                    budget_max=demo_data['budget_max'],
                    skills_required=demo_data['skills_required'],
                    urgency=demo_data['urgency'],
                    quality_score=0.7,
                    spider_source='fallback_demo'
                )

                fallback_opportunities.append(opportunity)
            except Exception as e:
                logger.error(f"Error creating fallback opportunity: {e}")

        # Score fallback opportunities
        scored_opportunities = await self._filter_and_score_opportunities(
            fallback_opportunities, user_profile
        )

        return scored_opportunities

    def _generate_cache_key(self, user_profile: Dict) -> str:
        """Generate cache key for user profile"""
        # Create a serializable copy of the profile
        cache_profile = {k: v for k, v in user_profile.items() if k != 'user'}
        # Convert UUID to string if present
        if 'user_id' in cache_profile:
            cache_profile['user_id'] = str(cache_profile['user_id'])
        profile_str = json.dumps(cache_profile, sort_keys=True)
        return f"spider_opportunities:{hashlib.md5(profile_str.encode()).hexdigest()}"

    async def _get_cached_opportunities(self, cache_key: str) -> Optional[List[SpiderOpportunity]]:
        """Get cached opportunities"""
        try:
            if not self.redis:
                return None

            cached_data = await self.redis.get(cache_key)
            if cached_data:
                opportunities_data = json.loads(cached_data)
                return [SpiderOpportunity(**opp_data) for opp_data in opportunities_data]
        except Exception as e:
            logger.error(f"Error getting cached opportunities: {e}")

        return None

    async def _cache_opportunities(self, cache_key: str, opportunities: List[SpiderOpportunity]):
        """Cache opportunities"""
        try:
            if not self.redis:
                return

            # Convert opportunities to JSON-serializable format
            opportunities_data = []
            for opp in opportunities:
                opp_dict = opp.__dict__.copy()
                # Convert datetime objects to ISO strings
                if opp_dict.get('discovered_at'):
                    opp_dict['discovered_at'] = opp_dict['discovered_at'].isoformat()
                if opp_dict.get('expires_at'):
                    opp_dict['expires_at'] = opp_dict['expires_at'].isoformat()
                opportunities_data.append(opp_dict)

            await self.redis.setex(
                cache_key,
                self.cache_timeout,
                json.dumps(opportunities_data)
            )
        except Exception as e:
            logger.error(f"Error caching opportunities: {e}")

    def _is_cache_valid(self) -> bool:
        """Check if cache is still valid"""
        if not self.last_fetch_time:
            return False

        return (datetime.now(timezone.utc) - self.last_fetch_time) < timedelta(seconds=self.cache_timeout)

    async def get_opportunity_by_id(self, opportunity_id: str) -> Optional[SpiderOpportunity]:
        """Get a specific opportunity by ID"""
        try:
            # Check all cached opportunities first
            for cached_opps in self.opportunity_cache.values():
                for opp in cached_opps:
                    if opp.id == opportunity_id:
                        return opp

            # If not found in cache, try to fetch from Redis
            if self.redis:
                # Check various channels
                channels = [
                    'spider:opportunities:freelance',
                    'spider:opportunities:content',
                    'spider:opportunities:automation',
                    'spider:opportunities:tutoring'
                ]

                for channel in channels:
                    raw_data = await self.redis.lrange(channel, 0, -1)
                    for item in raw_data:
                        try:
                            opp_data = json.loads(item)
                            if opp_data.get('id') == opportunity_id:
                                return await self._parse_spider_opportunity(opp_data, channel)
                        except Exception:
                            continue

            return None

        except Exception as e:
            logger.error(f"Error getting opportunity by ID {opportunity_id}: {e}")
            return None

    async def close(self):
        """Close Redis connection"""
        if self.redis:
            await self.redis.close()


# Global instance
spider_connector = SpiderOpportunityConnector()


async def save_opportunity_to_database(spider_opp: SpiderOpportunity, user) -> Optional['Opportunity']:
    """
    Save a SpiderOpportunity to the Django Opportunity model
    Returns the created Opportunity instance or None if failed
    """
    from django.db import transaction
    from core.models_unified_system import Opportunity
    from channels.db import database_sync_to_async

    @database_sync_to_async
    def _save_to_db():
        try:
            # Calculate potential revenue
            potential_revenue = spider_opp.budget_max or spider_opp.budget_min or spider_opp.estimated_earnings or 0

            # Calculate match score (convert 0-1 score to 0-100)
            match_score = int(spider_opp.quality_score * 100)

            with transaction.atomic():
                # Check if opportunity already exists
                existing = Opportunity.objects.filter(
                    user=user,
                    source=spider_opp.platform,
                    metadata__spider_id=spider_opp.id
                ).first()

                if existing:
                    logger.info(f"Opportunity {spider_opp.id} already exists in database")
                    return existing

                # Create new opportunity
                opportunity = Opportunity.objects.create(
                    user=user,
                    title=spider_opp.title,
                    opportunity_type=spider_opp.opportunity_type,
                    source=spider_opp.platform,
                    potential_revenue=potential_revenue,
                    hourly_rate=spider_opp.hourly_rate,
                    status='active',
                    match_score=match_score,
                    description=spider_opp.description,
                    requirements=spider_opp.skills_required,
                    expires_at=spider_opp.expires_at,
                    metadata={
                        'spider_id': spider_opp.id,
                        'spider_source': spider_opp.spider_source,
                        'budget_min': spider_opp.budget_min,
                        'budget_max': spider_opp.budget_max,
                        'experience_level': spider_opp.experience_level,
                        'deadline': spider_opp.deadline,
                        'urgency': spider_opp.urgency,
                        'competition_level': spider_opp.competition_level,
                        'client_rating': spider_opp.client_rating,
                        'discovered_at': spider_opp.discovered_at.isoformat() if spider_opp.discovered_at else None,
                        'raw_data': spider_opp.raw_data
                    }
                )

                logger.info(f"Created opportunity {opportunity.id} from spider {spider_opp.id}")
                return opportunity

        except Exception as e:
            logger.error(f"Error saving opportunity to database: {e}", exc_info=True)
            return None

    return await _save_to_db()


async def save_opportunities_batch(spider_opps: List[SpiderOpportunity], user) -> int:
    """
    Save multiple SpiderOpportunities to database in batch
    Returns count of successfully saved opportunities
    """
    saved_count = 0

    for spider_opp in spider_opps:
        opportunity = await save_opportunity_to_database(spider_opp, user)
        if opportunity:
            saved_count += 1

    logger.info(f"Saved {saved_count}/{len(spider_opps)} opportunities to database")
    return saved_count


async def get_spider_opportunities(user_profile: Dict) -> List[SpiderOpportunity]:
    """Convenience function to get opportunities"""
    try:
        if not spider_connector.redis:
            await spider_connector.initialize()

        return await spider_connector.get_opportunities_for_user(user_profile)
    except Exception as e:
        logger.error(f"Error in get_spider_opportunities: {e}")
        return await spider_connector._get_fallback_opportunities(user_profile)
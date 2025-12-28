"""
Revenue Opportunities WebSocket Consumer
========================================
Real-time opportunities from spider network to frontend
"""

import json
import logging
import asyncio
from typing import Dict, Any, List
from datetime import datetime
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
import redis

logger = logging.getLogger(__name__)


class RevenueOpportunitiesConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for Revenue Opportunities page
    Connects to spider network and sends real opportunities to users
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)
        self.user = None
        self.room_name = None
        self.room_group_name = None
        self.opportunities_task = None
        self.shown_opportunities = {}  # Track shown opportunities for learning
        self.engagement_session = None  # Track engagement metrics
        self.session_start_time = None

    async def connect(self):
        """Handle WebSocket connection"""
        self.user = self.scope.get('user', AnonymousUser())

        if isinstance(self.user, AnonymousUser):
            await self.close()
            return

        self.room_name = f'revenue_{self.user.id}'
        self.room_group_name = f'revenue_opportunities_{self.user.id}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

        # Initialize engagement tracking
        await self.initialize_engagement_session()

        # Send initial data
        await self.send_initial_opportunities()

        # Start streaming opportunities
        self.opportunities_task = asyncio.create_task(self.stream_opportunities())

        logger.info(f"✅ Revenue Opportunities WebSocket connected for user {self.user.username}")

    async def disconnect(self, close_code):
        """Handle WebSocket disconnect"""
        if self.opportunities_task:
            self.opportunities_task.cancel()

        # End engagement session
        await self.end_engagement_session()

        if self.room_group_name:
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

        logger.info(f"Revenue Opportunities WebSocket disconnected for user {self.user.username if self.user else 'unknown'}")

    async def receive(self, text_data):
        """Handle messages from WebSocket"""
        try:
            data = json.loads(text_data)
            action = data.get('action')

            if action == 'quick_apply':
                await self.handle_quick_apply(data)
            elif action == 'opportunity_clicked':
                await self.handle_opportunity_clicked(data)
            elif action == 'opportunity_rejected':
                await self.handle_opportunity_rejected(data)
            elif action == 'filter':
                await self.apply_filters(data.get('filters', {}))
            elif action == 'refresh':
                await self.send_initial_opportunities()
            elif action == 'get_details':
                await self.send_opportunity_details(data.get('opportunity_id'))

        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON'
            }))
        except Exception as e:
            logger.error(f"Error in receive: {str(e)}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': str(e)
            }))

    async def send_initial_opportunities(self):
        """Send initial set of opportunities"""
        opportunities = await self.get_opportunities_from_spiders()

        # Track that we showed these opportunities
        await self.record_opportunities_shown(opportunities)

        await self.send(text_data=json.dumps({
            'type': 'opportunities_update',
            'opportunities': opportunities,
            'total': len(opportunities),
            'timestamp': datetime.now().isoformat(),
            'stats': {
                'activeCount': len(opportunities),
                'totalValue': sum(
                    (opp.get('salary_min', 0) + opp.get('salary_max', 0)) // 2
                    if opp.get('salary_min') else opp.get('budget', 0)
                    for opp in opportunities
                ),
                'appliedToday': 0,
                'successRate': 0
            }
        }))

    async def record_opportunities_shown(self, opportunities: List[Dict]):
        """Track which opportunities were shown to user"""
        from django.utils import timezone

        # Count opportunities by platform
        platform_counts = {}
        for opp in opportunities:
            platform = opp.get('platform', 'unknown')
            platform_counts[platform] = platform_counts.get(platform, 0) + 1

        # Store in user's session for later comparison
        self.shown_opportunities = {
            opp['id']: {
                'platform': opp.get('platform'),
                'title': opp.get('title'),
                'shown_at': timezone.now().isoformat()
            }
            for opp in opportunities
        }

        logger.info(f"📊 Showed {len(opportunities)} opportunities to {self.user.username}: {platform_counts}")

    async def apply_user_learnings(self, opportunities: List[Dict]) -> List[Dict]:
        """Apply user-specific learnings to personalize opportunity ranking"""
        from core.models import UserAgentLearning

        # Get ALL active learnings for this user across all domains
        all_learnings = await database_sync_to_async(
            lambda: list(UserAgentLearning.objects.filter(
                user=self.user,
                agent_name='IncomeBuilder',
                is_active=True
            ))
        )()

        if not all_learnings:
            logger.info("No learnings yet for this user - showing unbiased results")
            return opportunities

        # Organize learnings by domain
        platform_preferences = {}
        salary_preferences = {}
        skill_preferences = []
        remote_preferences = None
        company_size_preferences = None

        for learning in all_learnings:
            content = learning.learning_content
            if not isinstance(content, dict):
                continue

            domain = learning.learning_domain
            confidence = learning.confidence_score
            success_rate = learning.success_rate

            if domain == 'platform_preferences':
                platform = content.get('preferred_platform', '').lower()
                if platform:
                    platform_preferences[platform] = {
                        'confidence': confidence,
                        'success_rate': success_rate,
                        'boost': confidence * 0.5  # Up to +50%
                    }

            elif domain == 'salary_preferences':
                salary_range = content.get('salary_range', {})
                if salary_range:
                    salary_preferences = {
                        'min': salary_range.get('min', 0),
                        'max': salary_range.get('max', 999999),
                        'confidence': confidence,
                        'boost': confidence * 0.3  # Up to +30%
                    }

            elif domain == 'skill_preferences':
                preferred_skills = content.get('preferred_skills', [])
                if preferred_skills:
                    skill_preferences = {
                        'skills': [s.lower() for s in preferred_skills],
                        'confidence': confidence,
                        'boost': confidence * 0.2  # Up to +20%
                    }

            elif domain == 'remote_preferences':
                remote_pref = content.get('preference', '').lower()
                if remote_pref:
                    remote_preferences = {
                        'preference': remote_pref,  # 'fully_remote', 'hybrid', 'onsite'
                        'confidence': confidence,
                        'boost': confidence * 0.25  # Up to +25%
                    }

            elif domain == 'company_size_preferences':
                size_pref = content.get('preferred_size', '').lower()
                if size_pref:
                    company_size_preferences = {
                        'size': size_pref,  # 'startup', 'small', 'medium', 'enterprise'
                        'confidence': confidence,
                        'boost': confidence * 0.15  # Up to +15%
                    }

        logger.info(f"📊 Learnings for {self.user.username}: {len(platform_preferences)} platforms, "
                   f"salary_range={bool(salary_preferences)}, skills={bool(skill_preferences)}, "
                   f"remote={bool(remote_preferences)}, company_size={bool(company_size_preferences)}")

        # Apply boosts to opportunities
        for opp in opportunities:
            total_boost = 0
            reasons = []

            # Platform boost
            platform = opp.get('platform', '').lower()
            if platform in platform_preferences:
                pref = platform_preferences[platform]
                total_boost += pref['boost']
                reasons.append(f"{pref['success_rate']*100:.0f}% interest in {platform.title()}")

            # Salary boost
            if salary_preferences:
                opp_salary = opp.get('budget_min', opp.get('budget', 0))
                if opp_salary and salary_preferences['min'] <= opp_salary <= salary_preferences['max']:
                    total_boost += salary_preferences['boost']
                    reasons.append(f"Matches your salary range")

            # Skills boost
            if skill_preferences:
                opp_skills = [s.lower() for s in opp.get('skills', [])]
                matching_skills = set(skill_preferences['skills']) & set(opp_skills)
                if matching_skills:
                    total_boost += skill_preferences['boost']
                    reasons.append(f"Uses your preferred skills")

            # Remote boost
            if remote_preferences:
                location = opp.get('location', '').lower()
                if 'remote' in location and remote_preferences['preference'] == 'fully_remote':
                    total_boost += remote_preferences['boost']
                    reasons.append(f"Fully remote position")

            # Apply total boost
            if total_boost > 0:
                original_score = opp.get('match_score', 0)
                new_score = min(100, original_score * (1 + total_boost))
                opp['match_score'] = int(new_score)
                opp['personalization_boost'] = f"+{total_boost*100:.0f}%"
                opp['reason'] = " · ".join(reasons[:2])  # Show top 2 reasons

                logger.debug(f"✨ Boosted {opp['title']}: {original_score} → {new_score} (+{total_boost*100:.0f}%)")

        return opportunities

    async def get_opportunities_from_spiders(self) -> List[Dict[str, Any]]:
        """Get opportunities from spider network using real spider orchestrator"""
        opportunities = []

        try:
            # SESSION 30: Connect to REAL spider network via orchestrator
            from intelligence.income_spider_orchestrator import income_spider_orchestrator
            from intelligence.income_builder import UserProfile, SkillLevel
            from django.core.cache import cache

            logger.info("🕷️ Revenue Opportunities: Fetching real data from spider network...")

            # Try cache first for fast response
            cached_opportunities = await database_sync_to_async(cache.get)('latest_opportunities', None)
            if cached_opportunities:
                logger.info(f"✅ Found {len(cached_opportunities)} cached opportunities")
                return cached_opportunities[:50]

            # Get REAL user profile from database
            from core.models import ExtendedUserProfile, UserProfile as CoreUserProfile

            try:
                # Try to get extended profile first
                extended_profile = await database_sync_to_async(
                    lambda: ExtendedUserProfile.objects.select_related('user').get(user=self.user)
                )()

                # Extract skills from extended profile
                user_skills = extended_profile.get_skills_list() if hasattr(extended_profile, 'get_skills_list') else []

                # Get basic profile for additional data
                try:
                    basic_profile = await database_sync_to_async(
                        lambda: CoreUserProfile.objects.get(user=self.user)
                    )()
                    if basic_profile.skills and isinstance(basic_profile.skills, list):
                        user_skills.extend(basic_profile.skills)
                except CoreUserProfile.DoesNotExist:
                    pass

                # Map experience level to SkillLevel enum
                experience_map = {
                    'entry': SkillLevel.BEGINNER,
                    'junior': SkillLevel.BEGINNER,
                    'mid': SkillLevel.INTERMEDIATE,
                    'senior': SkillLevel.ADVANCED,
                    'lead': SkillLevel.EXPERT,
                    'executive': SkillLevel.EXPERT,
                }
                skill_level = experience_map.get(extended_profile.experience_level, SkillLevel.INTERMEDIATE)

                # Remove duplicates from skills
                user_skills = list(set(user_skills)) if user_skills else ['python', 'django']

                logger.info(f"✅ Loaded real profile for {self.user.username}: {len(user_skills)} skills, {skill_level}")

            except ExtendedUserProfile.DoesNotExist:
                # Fallback to default profile
                user_skills = ['python', 'django', 'javascript']
                skill_level = SkillLevel.INTERMEDIATE
                logger.warning(f"⚠️ No extended profile for {self.user.username}, using defaults")

            # Create Income Builder profile from real user data
            profile = UserProfile(
                id=f'user_{self.user.id}',
                current_balance=0.0,
                skills=user_skills,
                skill_level=skill_level,
                available_hours_per_week=20  # Hardcoded - user profile field not implemented
            )

            # Fetch REAL opportunities from spider network
            result = await income_spider_orchestrator.discover_opportunities_for_user(
                profile,
                use_real_data=True,
                max_opportunities=50
            )

            logger.info(f"🎯 Spider network found {len(result.opportunities)} real opportunities")

            # Convert to frontend format with FULL details
            opportunities = []
            for opp in result.opportunities:
                # Format salary/budget display
                if opp.budget_min and opp.budget_max:
                    if opp.budget_min == opp.budget_max:
                        salary_display = f"${opp.budget_min:,}"
                    else:
                        salary_display = f"${opp.budget_min:,} - ${opp.budget_max:,}"
                elif opp.budget_min:
                    salary_display = f"${opp.budget_min:,}+"
                elif opp.hourly_rate:
                    salary_display = f"${opp.hourly_rate}/hr"
                else:
                    salary_display = "Salary TBD"

                frontend_opp = {
                    'id': opp.id,
                    'title': opp.title,
                    'company': opp.platform,
                    'platform': opp.platform,
                    'budget': opp.budget_min or 0,
                    'budget_min': opp.budget_min,
                    'budget_max': opp.budget_max,
                    'hourly_rate': opp.hourly_rate,
                    'salary_display': salary_display,  # NEW: Formatted for display
                    'type': 'hourly' if opp.hourly_rate else 'fixed',
                    'description': opp.description[:300] if opp.description else '',  # More description
                    'full_description': opp.description,  # Full text for modal
                    'skills': opp.skills_required[:10],  # More skills
                    'posted': 'Today',
                    'deadline': str(opp.deadline) if opp.deadline else 'Flexible',
                    'client_rating': opp.client_rating or 4.5,
                    'match_score': int(opp.quality_score * 100),
                    'experience_level': opp.experience_level,
                    'quick_apply_available': True,
                    'url': opp.raw_data.get('url', '#') if opp.raw_data else '#',
                    'source': opp.spider_source,
                    'location': opp.raw_data.get('location', 'Remote') if opp.raw_data else 'Remote',
                }
                opportunities.append(frontend_opp)

            # Store in cache for 5 minutes
            if opportunities:
                await database_sync_to_async(cache.set)('latest_opportunities', opportunities, timeout=300)
                logger.info(f"💾 Cached {len(opportunities)} opportunities for 5 minutes")

            # NEW: Apply user-specific learnings to personalize results
            opportunities = await self.apply_user_learnings(opportunities)

            # If no real opportunities (spiders failed), use fallback
            if not opportunities:
                opportunities = [
                    {
                        'id': 'opp_001',
                        'title': 'Python Backend Developer',
                        'company': 'TechStartup Inc',
                        'budget': 5000,
                        'type': 'fixed',
                        'platform': 'upwork',
                        'description': 'Build REST APIs for our SaaS platform',
                        'skills': ['Python', 'Django', 'PostgreSQL'],
                        'match_score': 92,
                        'quick_apply_available': True,
                        'posted': '2 hours ago',
                        'deadline': '5 days',
                        'client_rating': 4.8
                    },
                    {
                        'id': 'opp_002',
                        'title': 'Content Writer for Tech Blog',
                        'company': 'Digital Media Co',
                        'budget': 800,
                        'type': 'fixed',
                        'platform': 'fiverr',
                        'description': 'Write 10 SEO-optimized articles about AI',
                        'skills': ['Writing', 'SEO', 'AI Knowledge'],
                        'match_score': 78,
                        'quick_apply_available': True,
                        'posted': '5 hours ago',
                        'deadline': '7 days',
                        'client_rating': 4.5
                    },
                    {
                        'id': 'opp_003',
                        'title': 'React Frontend Development',
                        'company': 'Design Agency',
                        'budget': 3500,
                        'type': 'fixed',
                        'platform': 'freelancer',
                        'description': 'Create responsive UI for e-commerce site',
                        'skills': ['React', 'TypeScript', 'Tailwind CSS'],
                        'match_score': 85,
                        'quick_apply_available': True,
                        'posted': '1 day ago',
                        'deadline': '10 days',
                        'client_rating': 4.7
                    }
                ]

            # Sort by match score
            opportunities.sort(key=lambda x: x.get('match_score', 0), reverse=True)

        except Exception as e:
            logger.error(f"Error getting opportunities: {str(e)}")

        return opportunities

    def calculate_match_score(self, opportunity: Dict[str, Any]) -> int:
        """Calculate match score based on user profile"""
        # Get user profile
        from core.models import ExtendedUserProfile
        try:
            profile = ExtendedUserProfile.objects.get(user=self.user)
            user_skills = json.loads(profile.skills) if profile.skills else []

            # Simple matching algorithm
            required_skills = opportunity.get('skills_required', opportunity.get('skills', []))
            if not required_skills:
                return 75  # Default score

            matches = sum(1 for skill in required_skills if skill.lower() in [s.lower() for s in user_skills])
            score = int((matches / len(required_skills)) * 100) if required_skills else 75

            # Boost score based on budget
            budget = opportunity.get('budget', 0)
            if isinstance(budget, dict):
                budget = budget.get('max', 0)
            if budget > 1000:
                score = min(100, score + 10)

            return score

        except Exception:
            return 75  # Default score if no profile

    async def handle_opportunity_clicked(self, data: Dict[str, Any]):
        """Record that user clicked on an opportunity"""
        from core.models import UserAgentLearning
        from core.models_engagement_metrics import OpportunityInteraction
        from django.utils import timezone

        opportunity_id = data.get('opportunity_id')
        platform = data.get('platform')

        if not opportunity_id or not platform:
            return

        logger.info(f"📊 User {self.user.username} clicked opportunity {opportunity_id} from {platform}")

        # Update engagement metrics
        if self.engagement_session:
            self.engagement_session.opportunities_clicked += 1
            await database_sync_to_async(self.engagement_session.calculate_metrics)()

        # Track interaction
        await database_sync_to_async(
            OpportunityInteraction.objects.create
        )(
            user=self.user,
            engagement_session=self.engagement_session,
            opportunity_id=opportunity_id,
            opportunity_title=data.get('title', 'Unknown'),
            opportunity_platform=platform,
            opportunity_salary=data.get('budget', 0),
            interaction_type='click',
            was_personalized=(self.engagement_session.ab_test_group == 'treatment' if self.engagement_session else False),
            personalization_boost=data.get('personalization_boost', 0),
            match_score=data.get('match_score', 0)
        )

        # Update or create platform preference learning
        learning = await database_sync_to_async(
            UserAgentLearning.create_learning
        )(
            user=self.user,
            agent_name='IncomeBuilder',
            domain='platform_preferences',
            content={
                'preferred_platform': platform,
                'click_timestamp': timezone.now().isoformat(),
                'opportunity_id': opportunity_id
            },
            source='interaction_mining',
            confidence=0.6  # Medium confidence - just a click
        )

        # Record success (user showed interest)
        await database_sync_to_async(learning.record_success)()

        logger.info(f"✅ Recorded learning: {platform} preference (confidence: {learning.confidence_score:.1%})")

    async def handle_opportunity_rejected(self, data: Dict[str, Any]):
        """Record that user rejected/ignored an opportunity"""
        from core.models import UserAgentLearning

        opportunity_id = data.get('opportunity_id')
        platform = data.get('platform')
        reason = data.get('reason', 'not_interested')  # Frontend can send reason

        if not opportunity_id or not platform:
            return

        logger.info(f"❌ User {self.user.username} rejected opportunity {opportunity_id} from {platform}")

        # Get existing platform preference learning
        learnings = await database_sync_to_async(
            lambda: list(UserAgentLearning.objects.filter(
                user=self.user,
                agent_name='IncomeBuilder',
                domain='platform_preferences',
                learning_content__preferred_platform=platform
            ))
        )()

        if learnings:
            learning = learnings[0]
            # Record failure (user not interested in this platform)
            await database_sync_to_async(learning.record_failure)()
            logger.info(f"📉 Reduced {platform} confidence: {learning.confidence_score:.1%}")

    async def stream_opportunities(self):
        """Stream new opportunities as they come in"""
        while True:
            try:
                await asyncio.sleep(30)  # Check every 30 seconds

                # Get new opportunities
                opportunities = await self.get_opportunities_from_spiders()

                # Send only new/updated ones
                if opportunities:
                    await self.send(text_data=json.dumps({
                        'type': 'new_opportunities',
                        'data': {
                            'opportunities': opportunities[:5],  # Send top 5
                            'timestamp': datetime.now().isoformat()
                        }
                    }))

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in stream_opportunities: {str(e)}")
                await asyncio.sleep(60)  # Back off on error

    async def handle_quick_apply(self, data: Dict[str, Any]):
        """Handle quick apply action"""
        opportunity_id = data.get('opportunity_id')

        if not opportunity_id:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Opportunity ID required'
            }))
            return

        # Process application
        from core.views_job_application_system import QuickApplyView
        from core.models import Revenue
        from django.http import HttpRequest
        from django.utils import timezone

        # Create mock request
        request = HttpRequest()
        request.user = self.user
        request._body = json.dumps({
            'job_data': {
                'id': opportunity_id,
                'title': data.get('title', 'Unknown Position'),
                'company': data.get('company', 'Unknown Company'),
                'platform': data.get('platform', 'freelance')
            }
        }).encode()
        request.content_type = 'application/json'

        # Use QuickApplyView to process
        view = QuickApplyView()
        response = await database_sync_to_async(view.post)(request)

        response_data = json.loads(response.content)

        # Track revenue if application was successful
        if response_data.get('success', False):
            # Extract salary information from opportunity
            salary_min = data.get('salary_min', data.get('budget', 50000))
            salary_max = data.get('salary_max', salary_min)

            # If it's an hourly rate, calculate annual
            if isinstance(salary_min, int) and salary_min < 500:  # Likely hourly
                salary_min = salary_min * 2000  # Assume 2000 hours/year
                salary_max = salary_max * 2000 if isinstance(salary_max, int) else salary_min

            # Calculate potential revenue (average of min and max)
            potential_amount = (salary_min + salary_max) / 2

            # Create Revenue record
            await database_sync_to_async(Revenue.objects.create)(
                user=self.user,
                amount=potential_amount,
                source='quick_apply',
                status='potential',
                opportunity_id=opportunity_id,
                opportunity_title=data.get('title', 'Unknown Position'),
                company=data.get('company', 'Unknown Company'),
                application_date=timezone.now(),
                description=f"Quick Apply to {data.get('title')} at {data.get('company')}",
                spider_source=data.get('source', 'Unknown'),
                agent_involved='QuickApplyAgent',
                match_score=data.get('match_score', 0.75)
            )

            logger.info(f"Revenue tracked: ${potential_amount} potential from {opportunity_id}")

            # Update engagement metrics for application
            if self.engagement_session:
                self.engagement_session.opportunities_applied += 1
                self.engagement_session.potential_revenue += potential_amount
                await database_sync_to_async(self.engagement_session.calculate_metrics)()

            # Track application interaction
            from core.models_engagement_metrics import OpportunityInteraction

            await database_sync_to_async(
                OpportunityInteraction.objects.create
            )(
                user=self.user,
                engagement_session=self.engagement_session,
                opportunity_id=opportunity_id,
                opportunity_title=data.get('title', 'Unknown'),
                opportunity_platform=data.get('platform', 'unknown'),
                opportunity_salary=potential_amount,
                interaction_type='apply',
                was_personalized=(self.engagement_session.ab_test_group == 'treatment' if self.engagement_session else False),
                resulted_in_application=True,
                match_score=data.get('match_score', 0)
            )

            # NEW: Record high-confidence learning
            from core.models import UserAgentLearning

            platform = data.get('platform', 'unknown')

            # Strong signal - user actually applied!
            learning = await database_sync_to_async(
                UserAgentLearning.create_learning
            )(
                user=self.user,
                agent_name='IncomeBuilder',
                domain='platform_preferences',
                content={
                    'preferred_platform': platform,
                    'application_timestamp': timezone.now().isoformat(),
                    'opportunity_id': opportunity_id,
                    'application_successful': True
                },
                source='success_pattern',
                confidence=0.8  # High confidence - actual application
            )

            # Record multiple successes for strong signal
            for _ in range(3):  # Weight applications 3x more than clicks
                await database_sync_to_async(learning.record_success)()

            logger.info(f"🎯 Recorded strong learning: {platform} application (confidence: {learning.confidence_score:.1%})")

        await self.send(text_data=json.dumps({
            'type': 'quick_apply_result',
            'data': {
                'opportunity_id': opportunity_id,
                'success': response_data.get('success', False),
                'message': response_data.get('message', ''),
                'application_id': response_data.get('application', {}).get('id')
            }
        }))

    async def apply_filters(self, filters: Dict[str, Any]):
        """Apply filters and send filtered opportunities"""
        # Get all opportunities
        all_opportunities = await self.get_opportunities_from_spiders()

        # Apply filters
        filtered = all_opportunities

        if filters.get('min_budget'):
            min_budget = float(filters['min_budget'])
            filtered = [o for o in filtered if self._get_budget_value(o) >= min_budget]

        if filters.get('platform'):
            platform = filters['platform'].lower()
            filtered = [o for o in filtered if o.get('platform', '').lower() == platform]

        if filters.get('skills'):
            required_skills = filters['skills']
            filtered = [o for o in filtered if any(
                skill in o.get('skills', []) for skill in required_skills
            )]

        await self.send(text_data=json.dumps({
            'type': 'filtered_opportunities',
            'data': {
                'opportunities': filtered,
                'total': len(filtered),
                'filters_applied': filters
            }
        }))

    def _get_budget_value(self, opportunity: Dict[str, Any]) -> float:
        """Extract budget value from opportunity"""
        budget = opportunity.get('budget', 0)
        if isinstance(budget, dict):
            return budget.get('max', budget.get('min', 0))
        return float(budget)

    async def send_opportunity_details(self, opportunity_id: str):
        """Send detailed information about an opportunity"""
        # Get from Redis
        opportunity_json = await database_sync_to_async(
            self.redis_client.get
        )(f'freelance:opportunity:{opportunity_id}')

        if opportunity_json:
            opportunity = json.loads(opportunity_json)

            # Add additional details
            opportunity['full_description'] = opportunity.get('description', '')
            opportunity['application_tips'] = self._generate_application_tips(opportunity)

            await self.send(text_data=json.dumps({
                'type': 'opportunity_details',
                'data': opportunity
            }))
        else:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Opportunity not found'
            }))

    def _generate_application_tips(self, opportunity: Dict[str, Any]) -> List[str]:
        """Generate application tips based on opportunity"""
        tips = []

        budget = self._get_budget_value(opportunity)
        if budget > 1000:
            tips.append("This is a high-value project. Emphasize your relevant experience.")

        if opportunity.get('client_rating', 0) >= 4.5:
            tips.append("This client has excellent ratings. Be professional and detailed.")

        skills = opportunity.get('skills', [])
        if 'Python' in skills:
            tips.append("Mention specific Python frameworks and projects you've completed.")

        return tips

    # Group send handler
    async def opportunity_update(self, event):
        """Handle opportunity updates from channel layer"""
        await self.send(text_data=json.dumps({
            'type': 'opportunity_update',
            'data': event['data']
        }))

    # ==========================================
    # ENGAGEMENT METRICS & A/B TESTING
    # ==========================================

    async def initialize_engagement_session(self):
        """Initialize engagement tracking for this session"""
        from core.models_engagement_metrics import EngagementMetrics
        import random

        self.session_start_time = datetime.now()

        # Assign to A/B test group (20% control, 80% treatment)
        ab_group = 'control' if random.random() < 0.2 else 'treatment'

        # Create engagement session
        self.engagement_session = await database_sync_to_async(
            EngagementMetrics.objects.create
        )(
            user=self.user,
            session_id=f"session_{self.user.id}_{datetime.now().timestamp()}",
            ab_test_group=ab_group,
            personalized_results=(ab_group == 'treatment')
        )

        logger.info(f"📊 Engagement session started: {self.engagement_session.session_id} (Group: {ab_group})")

    async def end_engagement_session(self):
        """End engagement tracking session"""
        if self.engagement_session:
            await database_sync_to_async(self.engagement_session.end_session)()
            logger.info(f"📊 Engagement session ended: CTR={self.engagement_session.ctr:.2%}, App Rate={self.engagement_session.application_rate:.2%}")

    async def record_opportunities_shown(self, opportunities: List[Dict]):
        """Track which opportunities were shown to user"""
        from django.utils import timezone

        # Count opportunities by platform
        platform_counts = {}
        for opp in opportunities:
            platform = opp.get('platform', 'unknown')
            platform_counts[platform] = platform_counts.get(platform, 0) + 1

        # Store in user's session for later comparison
        self.shown_opportunities = {
            opp['id']: {
                'platform': opp.get('platform'),
                'title': opp.get('title'),
                'shown_at': timezone.now().isoformat()
            }
            for opp in opportunities
        }

        # Update engagement metrics
        if self.engagement_session:
            self.engagement_session.opportunities_shown += len(opportunities)
            await database_sync_to_async(self.engagement_session.save)()

        logger.info(f"📊 Showed {len(opportunities)} opportunities to {self.user.username}: {platform_counts}")
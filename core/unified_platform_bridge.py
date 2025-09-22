"""
Unified Platform Bridge - The Missing Connection Layer
=====================================================

This bridge connects all isolated components and enables real data flow
to transform the platform into an actual money-making system.

Key Responsibilities:
1. Profile persistence across all components
2. Real-time data synchronization
3. Spider data → Income Builder pipeline
4. Quick Apply → Real application submission
5. Revenue tracking for completed work
6. WebSocket message routing
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.core.cache import cache
from channels.layers import get_channel_layer

# Import models
from core.models import (
    UserProfile, ExtendedUserProfile, JobApplication,
    ResumeVersion, UserEmbedding, ChatConversation
)

User = get_user_model()
logger = logging.getLogger(__name__)


class UnifiedPlatformBridge:
    """
    The central nervous system that connects all platform components.
    Makes data flow seamlessly between Personal Assistant, Income Builder,
    Decision Command, Revenue Dashboard, Quick Apply, and Spider Network.
    """

    def __init__(self):
        self.channel_layer = get_channel_layer()
        self.active_users = {}
        self.component_states = {}

    # ==================== PROFILE SYNCHRONIZATION ====================

    async def sync_user_profile(self, user_id: int, profile_data: Dict) -> bool:
        """
        Sync user profile across ALL components.
        This is the master function that updates everywhere at once.
        """
        try:
            user = await User.objects.aget(id=user_id)

            # Update basic profile
            profile, created = await UserProfile.objects.aget_or_create(user=user)
            for field, value in profile_data.items():
                if hasattr(profile, field):
                    setattr(profile, field, value)
            await profile.asave()

            # Update extended profile
            ext_profile, created = await ExtendedUserProfile.objects.aget_or_create(user=user)
            ext_profile.calculate_profile_completeness()
            await ext_profile.asave()

            # Cache for instant access
            cache.set(f'user_profile_{user_id}', profile_data, 3600)

            # Notify all connected components via WebSocket
            await self.broadcast_profile_update(user_id, profile_data)

            # Update component-specific data
            await self.update_income_builder_context(user_id, profile_data)
            await self.update_decision_engine_context(user_id, profile_data)
            await self.update_personal_assistant_context(user_id, profile_data)

            return True

        except Exception as e:
            logger.error(f"Failed to sync user profile: {e}")
            return False

    async def broadcast_profile_update(self, user_id: int, profile_data: Dict):
        """Broadcast profile updates to all connected components."""
        if self.channel_layer:
            await self.channel_layer.group_send(
                f"user_{user_id}",
                {
                    "type": "profile.updated",
                    "profile": profile_data,
                    "timestamp": timezone.now().isoformat()
                }
            )

    # ==================== SPIDER → INCOME BUILDER PIPELINE ====================

    async def process_spider_discovery(self, spider_data: Dict) -> bool:
        """
        Process job discovered by spiders and feed to Income Builder.
        This is where spider discoveries become real opportunities.
        """
        try:
            # Validate job data
            if not self.is_valid_job(spider_data):
                return False

            # Store in database
            job_data = {
                'title': spider_data.get('title', ''),
                'company': spider_data.get('company', ''),
                'description': spider_data.get('description', ''),
                'url': spider_data.get('url', ''),
                'salary_min': self.extract_salary(spider_data.get('salary', '')),
                'location': spider_data.get('location', ''),
                'discovered_at': timezone.now(),
                'source': spider_data.get('spider_id', 'unknown')
            }

            # Score against all active user profiles
            scored_opportunities = await self.score_opportunity_for_all_users(job_data)

            # Send high-scoring opportunities to Income Builder
            for user_score in scored_opportunities:
                if user_score['score'] > 0.7:  # 70%+ match
                    await self.send_to_income_builder(user_score['user_id'], job_data, user_score['score'])
                    await self.notify_user_of_opportunity(user_score['user_id'], job_data, user_score['score'])

            return True

        except Exception as e:
            logger.error(f"Failed to process spider discovery: {e}")
            return False

    async def score_opportunity_for_all_users(self, job_data: Dict) -> List[Dict]:
        """Score job opportunity against all user profiles."""
        scored_opportunities = []

        # Get active users (logged in within last 7 days)
        cutoff_date = timezone.now() - timedelta(days=7)
        active_users = User.objects.filter(last_login__gte=cutoff_date)

        async for user in active_users:
            try:
                # Get user profile
                profile = await UserProfile.objects.aget(user=user)
                ext_profile = await ExtendedUserProfile.objects.aget(user=user)

                # Calculate match score
                score = await self.calculate_match_score(profile, ext_profile, job_data)

                scored_opportunities.append({
                    'user_id': user.id,
                    'score': score,
                    'reasons': await self.get_match_reasons(profile, ext_profile, job_data)
                })

            except Exception as e:
                logger.error(f"Failed to score opportunity for user {user.id}: {e}")
                continue

        return scored_opportunities

    async def calculate_match_score(self, profile: UserProfile, ext_profile: ExtendedUserProfile, job_data: Dict) -> float:
        """Calculate how well a job matches a user's profile."""
        score = 0.0

        # Skills matching (40% weight)
        skills_score = self.calculate_skills_match(ext_profile.get_skills_list(), job_data['description'])
        score += skills_score * 0.4

        # Experience level matching (20% weight)
        exp_score = self.calculate_experience_match(ext_profile.years_experience, job_data['description'])
        score += exp_score * 0.2

        # Salary fit (20% weight)
        salary_score = self.calculate_salary_fit(ext_profile.desired_salary_min, job_data.get('salary_min', 0))
        score += salary_score * 0.2

        # Location preference (10% weight)
        location_score = self.calculate_location_match(ext_profile.location, job_data.get('location', ''))
        score += location_score * 0.1

        # Remote work preference (10% weight)
        remote_score = self.calculate_remote_match(ext_profile.remote_preference, job_data['description'])
        score += remote_score * 0.1

        return min(score, 1.0)

    # ==================== INCOME BUILDER REAL DATA FEED ====================

    async def send_to_income_builder(self, user_id: int, job_data: Dict, score: float):
        """Send real job opportunity to Income Builder component."""
        opportunity = {
            'id': f"real_{job_data['url'].split('/')[-1]}",
            'title': job_data['title'],
            'company': job_data['company'],
            'description': job_data['description'][:200] + '...',
            'url': job_data['url'],
            'match_score': score,
            'salary_range': f"${job_data.get('salary_min', 0):,}+",
            'location': job_data.get('location', 'Remote'),
            'discovered_at': job_data['discovered_at'].isoformat(),
            'source': 'live_spider',
            'is_real': True
        }

        # Send via WebSocket to Income Builder
        if self.channel_layer:
            await self.channel_layer.group_send(
                f"user_{user_id}",
                {
                    "type": "income_builder.new_opportunity",
                    "opportunity": opportunity
                }
            )

        # Cache for immediate retrieval
        cache_key = f'opportunities_{user_id}'
        cached_opps = cache.get(cache_key, [])
        cached_opps.insert(0, opportunity)  # Add to front
        cache.set(cache_key, cached_opps[:20], 1800)  # Keep latest 20

    # ==================== QUICK APPLY REAL SUBMISSION ====================

    async def submit_real_application(self, user_id: int, job_data: Dict, application_data: Dict) -> Dict:
        """
        Actually submit job application to external job board.
        This transforms Quick Apply from fake to real.
        """
        try:
            user = await User.objects.aget(id=user_id)
            ext_profile = await ExtendedUserProfile.objects.aget(user=user)

            # Get best resume version for this job
            resume = await self.select_best_resume(user, job_data)

            # Generate customized cover letter
            cover_letter = await self.generate_cover_letter(ext_profile, job_data)

            # Submit application based on platform
            submission_result = await self.submit_to_platform(job_data, {
                'resume': resume,
                'cover_letter': cover_letter,
                'profile': ext_profile,
                **application_data
            })

            # Record application in database
            application = await JobApplication.objects.acreate(
                user=user,
                job_id=job_data.get('job_id', job_data['url'].split('/')[-1]),
                platform=self.detect_platform(job_data['url']),
                company=job_data['company'],
                position=job_data['title'],
                job_url=job_data['url'],
                application_method='quick_apply',
                resume_version=resume.version_name if resume else 'default',
                cover_letter_used=cover_letter,
                match_score=job_data.get('match_score', 0.0)
            )

            # Update resume usage stats
            if resume:
                resume.increment_usage()
                await resume.asave()

            # Notify user of successful application
            await self.notify_application_submitted(user_id, application)

            return {
                'success': True,
                'application_id': str(application.id),
                'submitted_at': application.applied_date.isoformat(),
                'platform': application.platform,
                'next_steps': await self.get_next_steps(application)
            }

        except Exception as e:
            logger.error(f"Failed to submit real application: {e}")
            return {
                'success': False,
                'error': str(e),
                'suggestion': 'Try applying manually or check your profile completeness'
            }

    # ==================== REVENUE TRACKING PIPELINE ====================

    async def record_revenue(self, user_id: int, revenue_data: Dict) -> bool:
        """Record actual revenue from completed work."""
        try:
            # Store revenue record
            from core.models import PlatformMetrics

            await PlatformMetrics.objects.acreate(
                metric_name='user_revenue',
                metric_value=float(revenue_data['amount']),
                subsystem='income_tracking',
                labels={
                    'user_id': user_id,
                    'source': revenue_data.get('source', 'unknown'),
                    'project_type': revenue_data.get('project_type', 'general'),
                    'currency': revenue_data.get('currency', 'USD')
                }
            )

            # Update user profile with earnings
            profile = await UserProfile.objects.aget(user_id=user_id)
            total_earnings = getattr(profile, 'total_earnings', 0) + float(revenue_data['amount'])
            profile.total_earnings = total_earnings
            await profile.asave()

            # Send celebration notification
            await self.celebrate_revenue(user_id, revenue_data)

            # Update revenue dashboard
            await self.update_revenue_dashboard(user_id, revenue_data)

            return True

        except Exception as e:
            logger.error(f"Failed to record revenue: {e}")
            return False

    # ==================== DECISION ENGINE CONNECTION ====================

    async def get_decision_recommendation(self, user_id: int, opportunity_data: Dict) -> Dict:
        """
        Get AI-powered recommendation on whether to pursue opportunity.
        Connects Decision Command to real data and ML insights.
        """
        try:
            user = await User.objects.aget(id=user_id)
            profile = await UserProfile.objects.aget(user=user)
            ext_profile = await ExtendedUserProfile.objects.aget(user=user)

            # Get historical performance data
            past_applications = JobApplication.objects.filter(user=user)
            success_rate = await self.calculate_user_success_rate(past_applications)

            # Calculate opportunity metrics
            metrics = {
                'skill_match': await self.calculate_match_score(profile, ext_profile, opportunity_data),
                'competition_level': await self.estimate_competition(opportunity_data),
                'earning_potential': await self.estimate_earning_potential(opportunity_data),
                'time_investment': await self.estimate_time_investment(opportunity_data),
                'success_probability': await self.predict_success_probability(user, opportunity_data)
            }

            # Generate recommendation
            should_apply = metrics['success_probability'] > 0.6 and metrics['skill_match'] > 0.7

            recommendation = {
                'should_apply': should_apply,
                'confidence': metrics['success_probability'],
                'reasoning': await self.generate_reasoning(metrics),
                'action_plan': await self.generate_action_plan(user, opportunity_data) if should_apply else None,
                'metrics': metrics,
                'alternatives': await self.suggest_alternatives(user, opportunity_data) if not should_apply else None
            }

            # Store decision for learning
            await self.store_decision_for_learning(user_id, opportunity_data, recommendation)

            return recommendation

        except Exception as e:
            logger.error(f"Failed to generate decision recommendation: {e}")
            return {
                'should_apply': False,
                'confidence': 0.0,
                'reasoning': f"Unable to analyze opportunity: {str(e)}",
                'error': True
            }

    # ==================== WEBSOCKET MESSAGE ROUTER ====================

    async def route_message(self, user_id: int, message: Dict):
        """Route messages between all components via WebSocket."""
        message_type = message.get('type')

        routing_map = {
            'profile_update': ['personal_assistant', 'income_builder', 'decision_engine'],
            'opportunity_found': ['income_builder', 'personal_assistant', 'decision_command'],
            'application_submitted': ['revenue_dashboard', 'personal_assistant'],
            'revenue_recorded': ['revenue_dashboard', 'personal_assistant', 'income_builder'],
            'decision_requested': ['decision_engine', 'personal_assistant']
        }

        components = routing_map.get(message_type, [])

        if self.channel_layer:
            for component in components:
                await self.channel_layer.group_send(
                    f"user_{user_id}_{component}",
                    {
                        "type": f"{component}.message",
                        "data": message,
                        "timestamp": timezone.now().isoformat()
                    }
                )

    # ==================== UTILITY METHODS ====================

    def is_valid_job(self, spider_data: Dict) -> bool:
        """Validate job data from spider."""
        required_fields = ['title', 'company', 'description', 'url']
        return all(field in spider_data and spider_data[field] for field in required_fields)

    def extract_salary(self, salary_text: str) -> int:
        """Extract minimum salary from text."""
        import re
        numbers = re.findall(r'\d{1,3}(?:,\d{3})*', salary_text.replace('$', ''))
        return int(numbers[0].replace(',', '')) if numbers else 0

    def calculate_skills_match(self, user_skills: List[str], job_description: str) -> float:
        """Calculate how well user skills match job requirements."""
        if not user_skills:
            return 0.0

        job_desc_lower = job_description.lower()
        matched_skills = sum(1 for skill in user_skills if skill.lower() in job_desc_lower)
        return matched_skills / len(user_skills)

    def detect_platform(self, url: str) -> str:
        """Detect job platform from URL."""
        if 'linkedin.com' in url:
            return 'LinkedIn'
        elif 'indeed.com' in url:
            return 'Indeed'
        elif 'glassdoor.com' in url:
            return 'Glassdoor'
        elif 'angel.co' in url:
            return 'AngelList'
        else:
            return 'Unknown'

    async def notify_user_of_opportunity(self, user_id: int, job_data: Dict, score: float):
        """Send notification about new opportunity match."""
        if self.channel_layer:
            await self.channel_layer.group_send(
                f"user_{user_id}",
                {
                    "type": "notification.new_opportunity",
                    "title": f"New {score*100:.0f}% Match Found!",
                    "message": f"{job_data['title']} at {job_data['company']}",
                    "score": score,
                    "job_data": job_data
                }
            )


# Global bridge instance
platform_bridge = UnifiedPlatformBridge()
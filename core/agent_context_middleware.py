"""
Agent Context Middleware - Inject user context into all agent executions

This middleware ensures that every agent in the platform receives comprehensive
user context for personalized AI responses and decision making.
"""

import logging
from typing import Dict, Any, Optional
from functools import wraps
from django.contrib.auth import get_user_model

from django.db import models  # Session 1083

logger = logging.getLogger(__name__)

User = get_user_model()


class AgentContextMiddleware:
    """
    Middleware that injects user context into every agent execution.

    This is the critical component that transforms the platform from generic
    to personalized by ensuring all 149+ agents know about the user.
    """

    def __init__(self):
        self.context_cache = {}  # Cache contexts to avoid repeated DB queries
        self.cache_timeout = 300  # 5 minutes cache

    def get_user_context(self, user: User) -> Dict[str, Any]:
        """
        Build comprehensive user context from all profile data.

        This is the heart of personalization - it gathers everything
        the agents need to know about the user.
        """
        cache_key = f"user_context_{user.id}"

        # Check cache first
        if cache_key in self.context_cache:
            cached_data, timestamp = self.context_cache[cache_key]
            import time
            if time.time() - timestamp < self.cache_timeout:
                return cached_data

        try:
            # Get all user profile data
            basic_profile = getattr(user, 'userprofile', None)
            extended_profile = getattr(user, 'extended_profile', None)
            stats = getattr(user, 'userstatistics', None)

            # Session 878: Get EnhancedUserProfile for goals
            try:
                from core.models import EnhancedUserProfile
                enhanced_profile = EnhancedUserProfile.objects.filter(user=user).first()
            except Exception:
                enhanced_profile = None

            # Build comprehensive context
            context = {
                'user_id': str(user.id),
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,

                # Basic profile information
                'basic_profile': self._extract_basic_profile(basic_profile),

                # Extended professional profile
                'professional_profile': self._extract_professional_profile(extended_profile),

                # Skills and experience
                'skills': self._extract_skills(extended_profile),

                # Job preferences and career goals
                'job_preferences': self._extract_job_preferences(extended_profile),

                # Work history and education
                'background': self._extract_background(extended_profile),

                # Application history and patterns
                'application_patterns': self._extract_application_patterns(user),

                # Platform usage statistics
                'usage_stats': self._extract_usage_stats(stats),

                # Success patterns from embeddings
                'success_patterns': self._extract_success_patterns(user),

                # Personalization metadata
                'personalization': {
                    'profile_completeness': getattr(extended_profile, 'profile_completeness', 0) if extended_profile else 0,
                    'last_active': user.last_login.isoformat() if user.last_login else None,
                    'account_created': user.date_joined.isoformat(),
                    'platform_role': getattr(user, 'platform_role', 'unified_user'),
                    'subscription_tier': getattr(user, 'subscription_tier', 'free'),
                    # Session 878: Add goals from EnhancedUserProfile
                    'goals': enhanced_profile.long_term_goals if enhanced_profile and enhanced_profile.long_term_goals else []
                }
            }

            # Cache the context
            import time
            self.context_cache[cache_key] = (context, time.time())

            logger.info(f"✅ Built user context for {user.username} (profile {context['personalization']['profile_completeness']:.1f}% complete)")
            return context

        except Exception as e:
            logger.error(f"❌ Failed to build user context for {user.username}: {str(e)}")
            # Return minimal context on error
            return {
                'user_id': str(user.id),
                'username': user.username,
                'error': 'Failed to load full context',
                'personalization': {
                    'profile_completeness': 0,
                    'platform_role': 'unified_user'
                }
            }

    def _extract_basic_profile(self, profile) -> Dict[str, Any]:
        """Extract basic profile information."""
        if not profile:
            return {}

        return {
            'display_name': profile.get_display_name(),
            'bio': getattr(profile, 'bio', ''),
            'occupation': getattr(profile, 'occupation', ''),
            'location': getattr(profile, 'location', ''),
            'avatar_url': profile.get_avatar_url(),
            'preferences': {
                'ai_model': getattr(profile, 'preferred_ai_model', 'gpt-5-mini'),
                'content_tone': getattr(profile, 'default_content_tone', 'professional'),
                'dark_mode': getattr(profile, 'dark_mode', True)
            }
        }

    def _extract_professional_profile(self, extended_profile) -> Dict[str, Any]:
        """Extract professional profile information."""
        if not extended_profile:
            return {}

        return {
            'full_name': getattr(extended_profile, 'full_name', ''),
            'phone': getattr(extended_profile, 'phone', ''),
            'location': getattr(extended_profile, 'location', ''),
            'current_title': getattr(extended_profile, 'current_title', ''),
            'years_experience': getattr(extended_profile, 'years_experience', 0),
            'experience_level': getattr(extended_profile, 'experience_level', 'entry'),
            'salary_range': {
                'min': float(extended_profile.desired_salary_min) if extended_profile.desired_salary_min else None,
                'max': float(extended_profile.desired_salary_max) if extended_profile.desired_salary_max else None
            },
            'remote_preference': getattr(extended_profile, 'remote_preference', 'no_preference'),
            'willing_to_relocate': getattr(extended_profile, 'willing_to_relocate', False),
            'linkedin_url': getattr(extended_profile, 'linkedin_url', ''),
            'portfolio_url': getattr(extended_profile, 'portfolio_url', ''),
            'github_username': getattr(extended_profile, 'github_username', '')
        }

    def _extract_skills(self, extended_profile) -> Dict[str, Any]:
        """Extract skills and certifications."""
        if not extended_profile:
            return {'skills': [], 'certifications': [], 'top_skills': []}

        skills = getattr(extended_profile, 'skills', [])
        certifications = getattr(extended_profile, 'certifications', [])

        return {
            'skills': skills,
            'skills_list': [skill.get('name', '') for skill in skills if skill.get('name')],
            'top_skills': extended_profile.get_top_skills() if hasattr(extended_profile, 'get_top_skills') else skills[:5],
            'certifications': certifications
        }

    def _extract_job_preferences(self, extended_profile) -> Dict[str, Any]:
        """Extract job search preferences."""
        if not extended_profile:
            return {}

        return getattr(extended_profile, 'job_preferences', {})

    def _extract_background(self, extended_profile) -> Dict[str, Any]:
        """Extract work history and education."""
        if not extended_profile:
            return {'work_history': [], 'education': []}

        return {
            'work_history': getattr(extended_profile, 'work_history', []),
            'education': getattr(extended_profile, 'education', [])
        }

    def _extract_application_patterns(self, user) -> Dict[str, Any]:
        """Extract job application patterns and success metrics."""
        try:
            from .models import JobApplication

            applications = JobApplication.objects.filter(user=user)
            total_apps = applications.count()

            if total_apps == 0:
                return {
                    'total_applications': 0,
                    'success_rate': 0,
                    'average_response_time': None,
                    'preferred_platforms': [],
                    'successful_industries': []
                }

            # Calculate success metrics
            successful_apps = applications.filter(status__in=['offer_received', 'offer_accepted'])
            success_rate = (successful_apps.count() / total_apps) * 100 if total_apps > 0 else 0

            # Response time analysis
            responded_apps = applications.exclude(response_time_days__isnull=True)
            avg_response_time = responded_apps.aggregate(
                avg_time=models.Avg('response_time_days')
            )['avg_time'] if responded_apps.exists() else None

            # Platform preferences (most used)
            platform_counts = applications.values('platform').annotate(
                count=models.Count('id')
            ).order_by('-count')[:3]

            # Successful company/industry patterns
            successful_companies = list(successful_apps.values_list('company', flat=True))

            return {
                'total_applications': total_apps,
                'success_rate': round(success_rate, 2),
                'average_response_time': round(avg_response_time, 1) if avg_response_time else None,
                'preferred_platforms': [p['platform'] for p in platform_counts],
                'successful_companies': successful_companies[:5],
                'recent_activity': applications.order_by('-applied_date')[:3].values(
                    'company', 'position', 'status', 'applied_date'
                )
            }

        except Exception as e:
            logger.warning(f"Could not extract application patterns for {user.username}: {str(e)}")
            return {
                'total_applications': 0,
                'success_rate': 0,
                'error': 'Could not load application data'
            }

    def _extract_usage_stats(self, stats) -> Dict[str, Any]:
        """Extract platform usage statistics."""
        if not stats:
            return {}

        return {
            'total_contents': getattr(stats, 'total_contents', 0),
            'total_ai_requests': getattr(stats, 'total_ai_requests', 0),
            'last_7_days_activity': getattr(stats, 'last_7_days_activity', 0),
            'last_30_days_activity': getattr(stats, 'last_30_days_activity', 0),
            'favorite_style': getattr(stats, 'favorite_style', ''),
            'storage_used_mb': stats.get_total_storage_mb() if hasattr(stats, 'get_total_storage_mb') else 0
        }

    def _extract_success_patterns(self, user) -> Dict[str, Any]:
        """Extract success patterns from user embeddings."""
        try:
            from .models import UserEmbedding

            # Get high-confidence success patterns
            success_embeddings = UserEmbedding.objects.filter(
                user=user,
                content_type='success_pattern',
                confidence_score__gte=0.7
            ).order_by('-confidence_score')[:5]

            # Get recent successful application patterns
            app_success_embeddings = UserEmbedding.objects.filter(
                user=user,
                content_type='successful_application',
                confidence_score__gte=0.6
            ).order_by('-last_used')[:3]

            return {
                'success_patterns': [
                    {
                        'content': emb.content[:200],
                        'confidence': emb.confidence_score,
                        'usage_count': emb.usage_count
                    } for emb in success_embeddings
                ],
                'application_success_patterns': [
                    {
                        'content': emb.content[:100],
                        'confidence': emb.confidence_score,
                        'last_used': emb.last_used.isoformat() if emb.last_used else None
                    } for emb in app_success_embeddings
                ]
            }

        except Exception as e:
            logger.warning(f"Could not extract success patterns for {user.username}: {str(e)}")
            return {'success_patterns': [], 'application_success_patterns': []}

    def inject_context_into_agent(self, agent_instance, user: User):
        """
        Inject user context into an agent instance.

        This method modifies the agent to include user context
        in all its operations.
        """
        context = self.get_user_context(user)

        # Add context to agent
        if hasattr(agent_instance, 'set_user_context'):
            agent_instance.set_user_context(context)
        else:
            # Fallback: add as attribute
            agent_instance.user_context = context

        # Add convenience methods
        agent_instance.get_user_skill = lambda skill_name: self._get_user_skill(context, skill_name)
        agent_instance.get_user_preference = lambda key, default=None: self._get_user_preference(context, key, default)
        agent_instance.calculate_opportunity_fit = lambda opportunity: self._calculate_opportunity_fit(context, opportunity)

        logger.info(f"🔗 Injected user context into {agent_instance.__class__.__name__} for {user.username}")

    def _get_user_skill(self, context: Dict, skill_name: str) -> Optional[Dict]:
        """Helper to get specific skill from context."""
        skills = context.get('skills', {}).get('skills', [])
        for skill in skills:
            if skill.get('name', '').lower() == skill_name.lower():
                return skill
        return None

    def _get_user_preference(self, context: Dict, key: str, default=None):
        """Helper to get user preference from context."""
        return context.get('job_preferences', {}).get(key, default)

    def _calculate_opportunity_fit(self, context: Dict, opportunity: Dict) -> float:
        """
        Calculate how well an opportunity fits the user.

        This is a core personalization algorithm that scores opportunities
        based on the user's profile, skills, and preferences.
        """
        score = 0.0

        # Skills match (40% weight)
        user_skills = set(context.get('skills', {}).get('skills_list', []))
        required_skills = set(opportunity.get('required_skills', []))
        preferred_skills = set(opportunity.get('preferred_skills', []))

        if required_skills:
            skill_match = len(required_skills & user_skills) / len(required_skills)
            score += skill_match * 40

        if preferred_skills:
            preferred_match = len(preferred_skills & user_skills) / len(preferred_skills)
            score += preferred_match * 10

        # Salary match (30% weight)
        salary_range = context.get('professional_profile', {}).get('salary_range', {})
        opp_salary_min = opportunity.get('salary_min', 0)
        opp_salary_max = opportunity.get('salary_max', 0)

        if salary_range.get('min') and opp_salary_min >= salary_range['min']:
            score += 30
        elif salary_range.get('max') and opp_salary_max >= salary_range['min']:
            score += 20

        # Location/Remote match (15% weight)
        remote_pref = context.get('professional_profile', {}).get('remote_preference', 'no_preference')
        is_remote = opportunity.get('remote', False)
        opp_location = opportunity.get('location', '')
        user_location = context.get('professional_profile', {}).get('location', '')

        if remote_pref == 'remote' and is_remote:
            score += 15
        elif remote_pref == 'onsite' and not is_remote and opp_location == user_location:
            score += 15
        elif remote_pref == 'hybrid':
            score += 10
        elif remote_pref == 'no_preference':
            score += 8

        # Experience level match (15% weight)
        user_exp = context.get('professional_profile', {}).get('years_experience', 0)
        min_exp = opportunity.get('min_experience', 0)
        max_exp = opportunity.get('max_experience', 999)

        if min_exp <= user_exp <= max_exp:
            score += 15
        elif user_exp >= min_exp:
            score += 10

        return min(score, 100.0)  # Cap at 100

    def get_system_learnings_for_agent(self, agent_name: str, max_learnings: int = 3) -> str:
        """
        Session 945: Get system learnings relevant to a specific agent.

        Fetches patterns from the learning loop orchestrator that are
        applicable to this agent.

        Args:
            agent_name: Name of the agent
            max_learnings: Maximum number of learnings to include

        Returns:
            Formatted string for prompt injection
        """
        try:
            from core.services.learning_loop_orchestrator import get_learning_loop_orchestrator

            orchestrator = get_learning_loop_orchestrator()
            return orchestrator.format_learnings_for_prompt(agent_name, max_learnings)
        except Exception as e:
            logger.warning(f"Could not get system learnings for {agent_name}: {e}")
            return ""


# Global middleware instance
_agent_context_middleware = AgentContextMiddleware()


def with_user_context(user: User):
    """
    Decorator to automatically inject user context into agent methods.

    Usage:
    @with_user_context(request.user)
    def my_agent_method(self, *args, **kwargs):
        # self.user_context will be available
        # self.get_user_skill('Python') will work
        return result
    """
    def decorator(func):
        @wraps(func)
        def wrapper(agent_instance, *args, **kwargs):
            # Inject context before execution
            _agent_context_middleware.inject_context_into_agent(agent_instance, user)

            # Execute the original method
            return func(agent_instance, *args, **kwargs)
        return wrapper
    return decorator


def get_user_context_for_agent(user: User) -> Dict[str, Any]:
    """
    Public function to get user context for any agent.

    This is the main entry point for agents to get user context.
    """
    return _agent_context_middleware.get_user_context(user)


def calculate_opportunity_fit_score(user: User, opportunity: Dict[str, Any]) -> float:
    """
    Public function to calculate opportunity fit score.

    This allows any agent to score opportunities for a user.
    """
    context = _agent_context_middleware.get_user_context(user)
    return _agent_context_middleware._calculate_opportunity_fit(context, opportunity)


def get_system_learnings_for_agent(agent_name: str, max_learnings: int = 3) -> str:
    """
    Session 945: Public function to get system learnings for an agent.

    This is the main entry point for agents to get learnings from the
    learning loop orchestrator.

    Args:
        agent_name: Name of the agent requesting learnings
        max_learnings: Maximum number of learnings to include

    Returns:
        Formatted string ready for prompt injection
    """
    return _agent_context_middleware.get_system_learnings_for_agent(agent_name, max_learnings)


class UserContextualAgent:
    """
    Base class for agents that need user context.

    All agents should inherit from this to get automatic context injection.
    """

    def __init__(self, user: User = None):
        self.user = user
        self.user_context = None
        if user:
            self.load_user_context()

    def load_user_context(self):
        """Load user context into this agent."""
        if self.user:
            self.user_context = get_user_context_for_agent(self.user)

    def get_user_skill(self, skill_name: str) -> Optional[Dict]:
        """Get specific skill information."""
        if not self.user_context:
            return None
        return _agent_context_middleware._get_user_skill(self.user_context, skill_name)

    def get_user_preference(self, key: str, default=None):
        """Get user preference value."""
        if not self.user_context:
            return default
        return _agent_context_middleware._get_user_preference(self.user_context, key, default)

    def calculate_opportunity_fit(self, opportunity: Dict[str, Any]) -> float:
        """Calculate how well an opportunity fits this user."""
        if not self.user_context:
            return 0.0
        return _agent_context_middleware._calculate_opportunity_fit(self.user_context, opportunity)

    def get_personalized_prompt(self, base_prompt: str) -> str:
        """
        Enhance a prompt with user context for personalized AI responses.

        This automatically adds relevant user information to prompts.
        """
        if not self.user_context:
            return base_prompt

        prof = self.user_context.get('professional_profile', {})
        skills = self.user_context.get('skills', {})

        context_addition = f"""

User Context for Personalization:
- Name: {prof.get('full_name', 'Unknown')}
- Title: {prof.get('current_title', 'Unknown')}
- Experience: {prof.get('years_experience', 0)} years ({prof.get('experience_level', 'entry')} level)
- Location: {prof.get('location', 'Unknown')}
- Top Skills: {', '.join(skill.get('name', '') for skill in skills.get('top_skills', [])[:3])}
- Remote Preference: {prof.get('remote_preference', 'no_preference')}
- Salary Range: ${prof.get('salary_range', {}).get('min', 0):,} - ${prof.get('salary_range', {}).get('max', 0):,}

Please personalize your response based on this user's specific background and needs.
"""

        return base_prompt + context_addition


# Export the main functions
__all__ = [
    'AgentContextMiddleware',
    'with_user_context',
    'get_user_context_for_agent',
    'calculate_opportunity_fit_score',
    'UserContextualAgent'
]
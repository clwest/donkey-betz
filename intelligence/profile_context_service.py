"""
Profile Context Service
=======================

Service to provide user profile context to all AI agents and systems
for personalized recommendations and responses.
"""

import logging
from typing import Dict, Any, Optional
from django.contrib.auth import get_user_model
from django.core.cache import cache
from datetime import datetime

logger = logging.getLogger(__name__)
User = get_user_model()


class ProfileContextService:
    """
    Centralized service for accessing and managing user profile context
    across all AI agents and systems.
    """

    def __init__(self):
        self.cache_timeout = 300  # 5 minutes
        self.context_types = [
            'general',
            'work',
            'personal',
            'learning',
            'income_opportunities',
            'job_matching',
            'communication'
        ]

    async def get_user_context(self, user_id: str, context_type: str = 'general') -> Dict[str, Any]:
        """
        Get comprehensive user context for AI agents.

        Args:
            user_id: User identifier
            context_type: Type of context needed (general, work, income_opportunities, etc.)

        Returns:
            Dictionary with relevant user context
        """
        try:
            # Check cache first
            cache_key = f'user_context_{user_id}_{context_type}'
            cached_context = cache.get(cache_key)

            if cached_context:
                return cached_context

            # Build fresh context
            context = await self._build_user_context(user_id, context_type)

            # Cache the context
            cache.set(cache_key, context, self.cache_timeout)

            return context

        except Exception as e:
            logger.error(f"Error getting user context: {e}")
            return self._get_default_context(user_id)

    async def _build_user_context(self, user_id: str, context_type: str) -> Dict[str, Any]:
        """Build comprehensive user context from all available sources"""
        from django.contrib.auth import get_user_model

        User = get_user_model()

        try:
            # Get user
            user = await self._get_user(user_id)
            if not user:
                return self._get_default_context(user_id)

            # Get enhanced profile
            enhanced_profile = await self._get_enhanced_profile(user)

            # Build base context
            context = {
                'user_id': user_id,
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email,
                'context_type': context_type,
                'generated_at': datetime.now().isoformat(),
                'has_interview_data': enhanced_profile.interview_completed if enhanced_profile else False
            }

            if enhanced_profile:
                # Get context from enhanced profile
                profile_context = enhanced_profile.get_context_for_ai(context_type)
                context.update(profile_context)

                # Add interview-specific context if available
                if enhanced_profile.interview_completed:
                    interview_context = self._get_interview_context(enhanced_profile, context_type)
                    context.update(interview_context)

                # Add personalization context
                personalization = self._get_personalization_context(enhanced_profile)
                context['personalization'] = personalization

            # Add session-based profile data (for backward compatibility)
            session_profile = await self._get_session_profile(user_id)
            if session_profile:
                context['session_profile'] = session_profile

            # Add behavioral context
            behavioral_context = await self._get_behavioral_context(user_id, context_type)
            context.update(behavioral_context)

            return context

        except Exception as e:
            logger.error(f"Error building user context: {e}")
            return self._get_default_context(user_id)

    def _get_interview_context(self, profile: 'EnhancedUserProfile', context_type: str) -> Dict[str, Any]:
        """Extract interview-specific context"""
        interview_context = {
            'interview_completed': profile.interview_completed,
            'interview_type': profile.interview_type,
            'current_situation': profile.current_situation,
            'available_hours_per_week': profile.available_hours_per_week,
            'monthly_income_goal': float(profile.monthly_income_goal) if profile.monthly_income_goal else None,
            'commitment_level': profile.commitment_level,
            'profile_strength_score': profile.profile_strength_score
        }

        if context_type == 'income_opportunities':
            interview_context.update({
                'strongest_skill': profile.strongest_skill,
                'skill_example': profile.skill_example,
                'professional_background': profile.professional_background,
                'career_motivation': profile.career_motivation,
                'work_type_preferences': profile.work_type_preferences,
                'things_to_avoid': profile.things_to_avoid,
                'hidden_talents': profile.hidden_talents,
                'available_assets': profile.available_assets,
                'personalized_recommendations': profile.personalized_recommendations,
                'auto_apply_preference': profile.auto_apply_preference
            })

        return interview_context

    def _get_personalization_context(self, profile: 'EnhancedUserProfile') -> Dict[str, Any]:
        """Get personalization data for AI responses"""
        return {
            'communication_style': profile.communication_style,
            'decision_framework': profile.decision_framework,
            'learning_style': profile.learning_style,
            'primary_role': profile.primary_role,
            'long_term_goals': profile.long_term_goals[:3] if profile.long_term_goals else [],
            'core_competencies': list(profile.core_competencies.keys())[:5] if profile.core_competencies else [],
            'profile_completeness': profile.profile_completeness,
            'interaction_count': profile.interaction_count
        }

    async def _get_behavioral_context(self, user_id: str, context_type: str) -> Dict[str, Any]:
        """Get user behavioral context from interaction history"""
        # This would analyze user behavior patterns, preferences, and interactions
        # For now, return basic behavioral indicators

        behavioral_context = {
            'preferred_response_length': 'medium',  # short, medium, long
            'engagement_level': 'high',  # low, medium, high
            'technical_level': 'intermediate',  # beginner, intermediate, advanced
            'interaction_frequency': 'regular'  # rare, occasional, regular, frequent
        }

        return behavioral_context

    async def _get_user(self, user_id: str):
        """Get user from database"""
        try:
            from django.contrib.auth import get_user_model
            from channels.db import database_sync_to_async

            User = get_user_model()

            @database_sync_to_async
            def get_user_sync():
                try:
                    return User.objects.get(id=user_id)
                except User.DoesNotExist:
                    return None

            return await get_user_sync()
        except Exception as e:
            logger.error(f"Error getting user: {e}")
            return None

    async def _get_enhanced_profile(self, user):
        """Get enhanced profile from database"""
        try:
            from core.models import EnhancedUserProfile
            from channels.db import database_sync_to_async

            @database_sync_to_async
            def get_profile_sync():
                try:
                    return EnhancedUserProfile.objects.get(user=user)
                except EnhancedUserProfile.DoesNotExist:
                    return None

            return await get_profile_sync()
        except Exception as e:
            logger.error(f"Error getting enhanced profile: {e}")
            return None

    async def _get_session_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get session-based profile data for backward compatibility"""
        try:
            from channels.db import database_sync_to_async

            @database_sync_to_async
            def get_session_data():
                # This would get session data if available
                # For now, return None - session data handled elsewhere
                return None

            return await get_session_data()
        except Exception as e:
            logger.error(f"Error getting session profile: {e}")
            return None

    def _get_default_context(self, user_id: str) -> Dict[str, Any]:
        """Get minimal default context when profile is unavailable"""
        return {
            'user_id': user_id,
            'context_type': 'general',
            'generated_at': datetime.now().isoformat(),
            'has_interview_data': False,
            'profile_completeness': 0,
            'personalization': {
                'communication_style': 'balanced',
                'decision_framework': 'analytical',
                'learning_style': 'mixed',
                'interaction_count': 0
            },
            'message': 'Limited context available - consider completing profile interview for better personalization'
        }

    async def update_user_context(self, user_id: str, updates: Dict[str, Any]) -> bool:
        """Update user context and invalidate cache"""
        try:
            # Clear cached contexts for this user
            await self.invalidate_user_cache(user_id)

            # Update profile data if needed
            if updates:
                await self._update_profile_data(user_id, updates)

            return True

        except Exception as e:
            logger.error(f"Error updating user context: {e}")
            return False

    async def invalidate_user_cache(self, user_id: str):
        """Invalidate all cached contexts for a user"""
        try:
            for context_type in self.context_types:
                cache_key = f'user_context_{user_id}_{context_type}'
                cache.delete(cache_key)

        except Exception as e:
            logger.error(f"Error invalidating cache: {e}")

    async def _update_profile_data(self, user_id: str, updates: Dict[str, Any]):
        """Update profile data in database"""
        try:
            from core.models import EnhancedUserProfile
            from channels.db import database_sync_to_async

            @database_sync_to_async
            def update_profile():
                try:
                    user = User.objects.get(id=user_id)
                    profile, created = EnhancedUserProfile.objects.get_or_create(user=user)

                    # Update allowed fields
                    for field, value in updates.items():
                        if hasattr(profile, field):
                            setattr(profile, field, value)

                    profile.save()
                    return True
                except Exception as e:
                    logger.error(f"Error updating profile in database: {e}")
                    return False

            return await update_profile()

        except Exception as e:
            logger.error(f"Error updating profile data: {e}")
            return False

    async def get_personalized_greeting(self, user_id: str) -> str:
        """Get personalized greeting based on user context"""
        try:
            context = await self.get_user_context(user_id, 'general')

            name = context.get('first_name', 'there')
            interview_completed = context.get('has_interview_data', False)
            completeness = context.get('profile_completeness', 0)

            if interview_completed and completeness > 70:
                return f"Hi {name}! I know your goals and can provide personalized recommendations."
            elif interview_completed:
                return f"Welcome back {name}! Your profile is {completeness:.0f}% complete."
            else:
                return f"Hi {name}! I'd love to learn about your goals to provide better assistance."

        except Exception as e:
            logger.error(f"Error getting personalized greeting: {e}")
            return "Hi! I'm your AI assistant, ready to help."

    async def get_context_summary(self, user_id: str) -> Dict[str, Any]:
        """Get summary of user context for debugging/admin purposes"""
        try:
            context = await self.get_user_context(user_id, 'general')

            return {
                'user_id': user_id,
                'has_profile': context.get('has_interview_data', False),
                'completeness': context.get('profile_completeness', 0),
                'primary_role': context.get('primary_role', 'Unknown'),
                'commitment_level': context.get('commitment_level', 'Unknown'),
                'income_goal': context.get('monthly_income_goal', 0),
                'available_hours': context.get('available_hours_per_week', 0),
                'communication_style': context.get('personalization', {}).get('communication_style', 'balanced'),
                'last_updated': context.get('generated_at')
            }

        except Exception as e:
            logger.error(f"Error getting context summary: {e}")
            return {'error': str(e)}


# Global service instance
profile_context_service = ProfileContextService()


class AgentContextMixin:
    """
    Mixin for AI agents to easily access user profile context.
    """

    async def get_user_context(self, user_id: str, context_type: str = 'general') -> Dict[str, Any]:
        """Get user context for this agent"""
        return await profile_context_service.get_user_context(user_id, context_type)

    async def get_personalized_response_context(self, user_id: str) -> Dict[str, Any]:
        """Get context specifically for personalizing responses"""
        context = await self.get_user_context(user_id, 'communication')

        return {
            'communication_style': context.get('personalization', {}).get('communication_style', 'balanced'),
            'technical_level': context.get('technical_level', 'intermediate'),
            'preferred_response_length': context.get('preferred_response_length', 'medium'),
            'decision_framework': context.get('decision_framework', 'analytical'),
            'user_name': context.get('first_name', ''),
            'primary_role': context.get('primary_role', ''),
            'experience_level': context.get('experience_level', 'intermediate')
        }

    def format_personalized_response(self, response: str, context: Dict[str, Any]) -> str:
        """Format response based on user preferences"""
        communication_style = context.get('communication_style', 'balanced')
        name = context.get('user_name', '')

        # Add personal touch if name available
        if name and not response.startswith(('Hi', 'Hello', name)):
            response = f"{name}, {response.lower()}"

        # Adjust response style
        if communication_style == 'concise':
            # Keep response brief
            lines = response.split('\n')
            if len(lines) > 3:
                response = '\n'.join(lines[:3]) + '\n\nWould you like more details?'

        elif communication_style == 'detailed':
            # Add more context if response is too brief
            if len(response) < 100:
                response += '\n\nLet me know if you need more specific information or have follow-up questions.'

        return response
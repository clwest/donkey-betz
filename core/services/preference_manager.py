"""
Agent Preference Manager - Unified User Preference System
==========================================================

Session 203: Created as Phase 4 of Agent Architecture Refactor
Session 727: Migrated from agents/preference_manager.py to core/services/preference_manager.py

This manager provides a unified interface for agents to:
1. Retrieve user preferences (styles, models, voices, etc.)
2. Learn from user interactions and successful generations
3. Apply preferences automatically to agent operations
4. Track preference evolution over time

The goal is to make agents "remember" user preferences so they don't have
to specify the same options repeatedly.

Example:
    # Agent automatically applies user's preferred style
    manager = AgentPreferenceManager(user)
    prefs = manager.get_image_preferences()
    # prefs = {'style': 'pixar', 'model': 'sd3-large-turbo', 'aspect_ratio': '16:9'}

    # Learn from user interaction
    manager.record_preference(
        domain='image',
        preference_type='style',
        value='pixar',
        context={'prompt': 'dancing donkey', 'user_rating': 5}
    )
"""

from __future__ import annotations

import logging
import json
from typing import Dict, Any, Optional
from collections import defaultdict

logger = logging.getLogger(__name__)


class AgentPreferenceManager:
    """
    Unified preference manager for all specialist agents.

    Consolidates preferences from:
    - UserCreativePreference (content/models.py)
    - StyleMemory (style_memory/models.py)
    - AgentExecutionMemory (core/models_agent_memory.py)
    - Redis cache for fast access
    """

    # Default preferences by domain
    DEFAULT_PREFERENCES = {
        'image': {
            'style': None,  # No default - let user choose
            'model': 'sd3-large-turbo',
            'aspect_ratio': '1:1',
            'quality': 'standard',
        },
        'video': {
            'duration': 5,
            'quality': 'gen4_turbo',
            'aspect_ratio': '16:9',
        },
        'audio': {
            'voice': 'Rachel',
            'model': 'eleven_multilingual_v2',
            'stability': 0.5,
            'similarity_boost': 0.75,
        },
        'research': {
            'sources': ['web', 'spiders'],
            'depth': 'standard',
            'max_results': 10,
        }
    }

    # Preference weight decay (older preferences count less)
    DECAY_DAYS = 30  # Preferences older than this get lower weight

    def __init__(self, user, project_id: Optional[str] = None):
        """
        Initialize the preference manager.

        Args:
            user: Django user object
            project_id: Optional project ID for project-specific preferences
        """
        self.user = user
        self.user_id = user.id if user else None
        self.project_id = project_id
        self._cache = {}
        self._redis = None

    @property
    def redis(self):
        """Lazy load Redis connection."""
        if self._redis is None:
            try:
                import redis
                self._redis = redis.Redis(
                    host='localhost',
                    port=6379,
                    db=4,  # Use db=4 for preferences
                    decode_responses=True
                )
            except Exception as e:
                logger.warning(f"Redis not available for preferences: {e}")
                self._redis = None
        return self._redis

    def get_preferences(self, domain: str) -> Dict[str, Any]:
        """
        Get all preferences for a domain.

        Args:
            domain: 'image', 'video', 'audio', or 'research'

        Returns:
            Dictionary of preferences merged from all sources
        """
        # Start with defaults
        prefs = self.DEFAULT_PREFERENCES.get(domain, {}).copy()

        # Try cache first
        cache_key = f"prefs:{self.user_id}:{domain}"
        if cache_key in self._cache:
            prefs.update(self._cache[cache_key])
            return prefs

        # Try Redis cache
        if self.redis:
            try:
                cached = self.redis.get(cache_key)
                if cached:
                    cached_prefs = json.loads(cached)
                    prefs.update(cached_prefs)
                    self._cache[cache_key] = cached_prefs
                    return prefs
            except Exception as e:
                logger.debug(f"Redis cache miss: {e}")

        # Load from database
        db_prefs = self._load_preferences_from_db(domain)
        if db_prefs:
            prefs.update(db_prefs)
            # Cache for future
            self._cache[cache_key] = db_prefs
            if self.redis:
                try:
                    self.redis.setex(cache_key, 3600, json.dumps(db_prefs))  # 1 hour TTL
                except Exception as _e:
                    logger.warning(
                        "preferences.get_preferences: swallowed (%s: %s) — degraded",
                        type(_e).__name__, _e,
                    )

        return prefs

    def get_image_preferences(self) -> Dict[str, Any]:
        """Get image generation preferences."""
        return self.get_preferences('image')

    def get_video_preferences(self) -> Dict[str, Any]:
        """Get video generation preferences."""
        return self.get_preferences('video')

    def get_audio_preferences(self) -> Dict[str, Any]:
        """Get audio generation preferences."""
        return self.get_preferences('audio')

    def get_research_preferences(self) -> Dict[str, Any]:
        """Get research preferences."""
        return self.get_preferences('research')

    def get_preferred_style(self, domain: str = 'image') -> Optional[str]:
        """
        Get user's most preferred style for a domain.

        Args:
            domain: 'image', 'video', or 'audio'

        Returns:
            Style name or None if no preference
        """
        prefs = self.get_preferences(domain)
        return prefs.get('style')

    def get_preferred_voice(self) -> str:
        """Get user's preferred voice for audio/speech."""
        prefs = self.get_audio_preferences()
        return prefs.get('voice', 'Rachel')

    def record_preference(
        self,
        domain: str,
        preference_type: str,
        value: Any,
        context: Optional[Dict[str, Any]] = None,
        weight: float = 1.0
    ) -> bool:
        """
        Record a user preference (learning from interaction).

        Args:
            domain: 'image', 'video', 'audio', 'research'
            preference_type: Type of preference ('style', 'voice', 'model', etc.)
            value: Preference value
            context: Optional context (prompt, rating, etc.)
            weight: Preference weight (higher = stronger signal)

        Returns:
            Success status
        """
        if not self.user_id:
            return False

        logger.info(f"Recording preference: {domain}.{preference_type} = {value} (weight={weight})")

        try:
            # Record to StyleMemory for style preferences
            if preference_type == 'style' and domain == 'image':
                self._record_style_memory(value, context)

            # Record to UserCreativePreference
            self._update_creative_preference(domain, preference_type, value, weight)

            # Invalidate cache
            cache_key = f"prefs:{self.user_id}:{domain}"
            self._cache.pop(cache_key, None)
            if self.redis:
                try:
                    self.redis.delete(cache_key)
                except Exception as _e:
                    logger.warning(
                        "preferences.record_preference: swallowed (%s: %s) — degraded",
                        type(_e).__name__, _e,
                    )

            return True

        except Exception as e:
            logger.error(f"Error recording preference: {e}", exc_info=True)
            return False

    def record_successful_generation(
        self,
        domain: str,
        parameters: Dict[str, Any],
        user_rating: Optional[int] = None
    ) -> bool:
        """
        Record a successful generation to learn preferences.

        Args:
            domain: 'image', 'video', 'audio'
            parameters: Generation parameters used
            user_rating: Optional 1-5 star rating

        Returns:
            Success status
        """
        # Calculate weight based on rating
        weight = 1.0
        if user_rating:
            weight = user_rating / 5.0  # Normalize to 0-1

        # Extract and record relevant preferences
        preference_mapping = {
            'image': ['style', 'model', 'aspect_ratio'],
            'video': ['duration', 'quality', 'aspect_ratio'],
            'audio': ['voice', 'model'],
        }

        for pref_type in preference_mapping.get(domain, []):
            if pref_type in parameters:
                self.record_preference(
                    domain=domain,
                    preference_type=pref_type,
                    value=parameters[pref_type],
                    context=parameters,
                    weight=weight
                )

        return True

    def apply_preferences(
        self,
        domain: str,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Apply user preferences to parameters (non-destructive).

        Only fills in missing parameters from preferences.
        User-specified values always take precedence.

        Args:
            domain: 'image', 'video', 'audio', 'research'
            parameters: Current parameters

        Returns:
            Parameters with preferences applied for missing values
        """
        prefs = self.get_preferences(domain)
        result = parameters.copy()

        for key, value in prefs.items():
            if key not in result and value is not None:
                result[key] = value
                logger.debug(f"Applied preference: {key} = {value}")

        return result

    def get_preference_summary(self) -> Dict[str, Any]:
        """
        Get a summary of all user preferences.

        Returns:
            Dictionary with preferences for all domains
        """
        return {
            'image': self.get_image_preferences(),
            'video': self.get_video_preferences(),
            'audio': self.get_audio_preferences(),
            'research': self.get_research_preferences(),
            'learning_stage': self._get_learning_stage(),
        }

    def clear_preferences(self, domain: Optional[str] = None) -> bool:
        """
        Clear user preferences.

        Args:
            domain: Specific domain to clear, or None for all

        Returns:
            Success status
        """
        try:
            if domain:
                cache_key = f"prefs:{self.user_id}:{domain}"
                self._cache.pop(cache_key, None)
                if self.redis:
                    self.redis.delete(cache_key)
            else:
                # Clear all
                for d in ['image', 'video', 'audio', 'research']:
                    cache_key = f"prefs:{self.user_id}:{d}"
                    self._cache.pop(cache_key, None)
                    if self.redis:
                        self.redis.delete(cache_key)

            logger.info(f"Cleared preferences for user {self.user_id}, domain={domain}")
            return True

        except Exception as e:
            logger.error(f"Error clearing preferences: {e}")
            return False

    # Private methods

    def _load_preferences_from_db(self, domain: str) -> Dict[str, Any]:
        """Load preferences from database models."""
        prefs = {}

        try:
            # Load from UserCreativePreference
            from content.models import UserCreativePreference

            try:
                creative_prefs = UserCreativePreference.objects.get(user=self.user)

                if domain == 'image':
                    # Get most preferred style
                    if creative_prefs.preferred_styles:
                        prefs['style'] = creative_prefs.preferred_styles[0] if creative_prefs.preferred_styles else None

                    # Get most preferred model
                    if creative_prefs.preferred_models:
                        prefs['model'] = creative_prefs.preferred_models[0] if creative_prefs.preferred_models else None

            except UserCreativePreference.DoesNotExist:
                pass

            # Load from StyleMemory for more recent preferences
            from style_memory.models import StyleMemory, StylePattern

            # Get recent positive interactions
            recent_positive = StyleMemory.objects.filter(
                user=self.user,
                interaction_type__in=['love', 'like', 'save', 'rate_4', 'rate_5']
            ).order_by('-created_at')[:20]

            # Analyze for style patterns
            style_counts = defaultdict(int)
            for memory in recent_positive:
                for style in memory.style_elements:
                    style_counts[style] += 1

            if style_counts and domain == 'image':
                # Get most common style
                most_common = max(style_counts.items(), key=lambda x: x[1])
                if most_common[1] >= 2:  # At least 2 occurrences
                    prefs['learned_style'] = most_common[0]

            # Load from StylePattern for high-confidence patterns
            patterns = StylePattern.objects.filter(
                user=self.user,
                confidence__gte=0.7
            ).order_by('-confidence')[:5]

            for pattern in patterns:
                if pattern.pattern_type == 'style' and domain == 'image':
                    prefs.setdefault('style', pattern.pattern_value)

        except Exception as e:
            logger.warning(f"Error loading preferences from DB: {e}")

        return prefs

    def _record_style_memory(self, style: str, context: Optional[Dict[str, Any]]):
        """Record style preference to StyleMemory."""
        try:
            from style_memory.models import StyleMemory

            # Determine interaction type based on context
            interaction_type = 'like'
            if context:
                rating = context.get('user_rating')
                if rating:
                    if rating >= 4:
                        interaction_type = 'love'
                    elif rating <= 2:
                        interaction_type = 'dislike'

            StyleMemory.objects.create(
                user=self.user,
                content_id=context.get('content_id', f"style_pref_{style}"),
                interaction_type=interaction_type,
                style_elements=[style],
                prompt=context.get('prompt', '') if context else '',
                project_id=self.project_id,
            )

        except Exception as e:
            logger.warning(f"Error recording style memory: {e}")

    def _update_creative_preference(
        self,
        domain: str,
        preference_type: str,
        value: Any,
        weight: float
    ):
        """Update UserCreativePreference model."""
        try:
            from content.models import UserCreativePreference

            prefs, created = UserCreativePreference.objects.get_or_create(
                user=self.user,
                defaults={
                    'preferred_styles': [],
                    'preferred_models': [],
                }
            )

            # Update based on preference type
            if preference_type == 'style' and domain == 'image':
                styles = list(prefs.preferred_styles or [])
                # Remove if exists, add to front (most recent = most preferred)
                if value in styles:
                    styles.remove(value)
                styles.insert(0, value)
                prefs.preferred_styles = styles[:10]  # Keep top 10

            elif preference_type == 'model' and domain == 'image':
                models = list(prefs.preferred_models or [])
                if value in models:
                    models.remove(value)
                models.insert(0, value)
                prefs.preferred_models = models[:5]  # Keep top 5

            prefs.total_choices += 1
            prefs.save()

        except Exception as e:
            logger.warning(f"Error updating creative preference: {e}")

    def _get_learning_stage(self) -> str:
        """Get user's preference learning stage."""
        try:
            from content.models import UserCreativePreference

            prefs = UserCreativePreference.objects.filter(user=self.user).first()
            if prefs:
                return prefs.get_learning_stage()

        except Exception as _e:
            logger.warning(
                "preferences._get_learning_stage: swallowed (%s: %s) — degraded",
                type(_e).__name__, _e,
            )

        return "new"


# Convenience functions
def get_user_preferences(user, domain: str = 'image') -> Dict[str, Any]:
    """Get preferences for a user and domain."""
    manager = AgentPreferenceManager(user)
    return manager.get_preferences(domain)


def apply_user_preferences(user, domain: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
    """Apply user preferences to parameters."""
    manager = AgentPreferenceManager(user)
    return manager.apply_preferences(domain, parameters)


__all__ = [
    'AgentPreferenceManager',
    'get_user_preferences',
    'apply_user_preferences',
]

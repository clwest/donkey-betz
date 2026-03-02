"""
Memory Context Service
======================

Session 628: Cross-Session Memory for PA Prompts

Builds contextual memory blocks for injection into PA system prompts,
enabling cross-session personalization based on stored preferences,
goals, and decisions.

Uses decay weighting from Session 601 (e^(-age_days / 21)) to prioritize
recent memories while not forgetting older important ones.
"""

import logging
import math
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.utils import timezone

from core.models import UserMemoryContext, EnhancedUserProfile

logger = logging.getLogger(__name__)
User = get_user_model()


class MemoryContextService:
    """
    Builds memory context for PA prompt injection.

    Retrieves preferences, goals, and decisions from UserMemoryContext
    and EnhancedUserProfile, applies decay weighting, and formats
    for system prompt injection.
    """

    # Cache settings
    CACHE_PREFIX = "memory_context"
    CACHE_TTL = 300  # 5 minutes

    # Context limits (approximate tokens)
    MAX_CONTEXT_CHARS = 2000  # ~500 tokens
    MAX_MEMORIES_PER_TYPE = 5

    # Decay half-life in days (from Session 601)
    DECAY_HALF_LIFE = 21

    def __init__(self, user: Optional[User] = None):
        """
        Initialize the Memory Context Service.

        Args:
            user: User for personalized operations
        """
        self.user = user
        # Env-var overrides for context limits
        env_max_tokens = os.environ.get('MEMORY_MAX_TOKENS', '')
        self.max_context_chars = int(env_max_tokens) * 4 if env_max_tokens else self.MAX_CONTEXT_CHARS
        self.max_items = int(os.environ.get('MEMORY_MAX_ITEMS', '200'))

    def calculate_decay_weight(self, created_at: datetime) -> float:
        """
        Calculate decay weight based on age.

        Formula from Session 601: e^(-age_days / 21)

        Args:
            created_at: When the memory was created

        Returns:
            Weight between 0.0 and 1.0
        """
        if created_at is None:
            return 0.5

        now = timezone.now()
        if timezone.is_naive(created_at):
            created_at = timezone.make_aware(created_at)

        age_days = (now - created_at).days
        return math.exp(-age_days / self.DECAY_HALF_LIFE)

    def get_prompt_context(self, user: User) -> str:
        """
        Build memory context string for system prompt injection.

        Retrieves preferences, goals, and decisions, applies decay
        weighting, and formats as a structured context block.

        Args:
            user: User to get context for

        Returns:
            Formatted context string for prompt injection
        """
        # Check cache
        cache_key = f"{self.CACHE_PREFIX}:prompt:{user.id}"
        cached = cache.get(cache_key)
        if cached:
            return cached

        context_parts = []

        # 1. Get profile-based context (static preferences)
        profile_context = self._get_profile_context(user)
        if profile_context:
            context_parts.append(profile_context)

        # 2. Get dynamic preferences from UserMemoryContext
        preferences = self._get_weighted_memories(
            user,
            memory_types=['preference'],
            limit=self.MAX_MEMORIES_PER_TYPE
        )
        if preferences:
            context_parts.append(self._format_preferences(preferences))

        # 3. Get goals
        goals = self._get_weighted_memories(
            user,
            memory_types=['goal'],
            limit=3
        )
        if goals:
            context_parts.append(self._format_goals(goals))

        # 4. Get recent decisions (for context on what user chose before)
        decisions = self._get_weighted_memories(
            user,
            memory_types=['decision'],
            limit=3,
            days_back=30  # Only recent decisions
        )
        if decisions:
            context_parts.append(self._format_decisions(decisions))

        # Combine and truncate
        context = "\n\n".join(context_parts)
        if len(context) > self.max_context_chars:
            context = context[:self.max_context_chars] + "..."

        # Cache result
        cache.set(cache_key, context, self.CACHE_TTL)

        logger.info(f"Built memory context for {user.username}: {len(context)} chars")
        return context

    def get_content_preferences(self, user: User, channel=None) -> Dict[str, Any]:
        """
        Get preferences specifically for content generation.

        Merges user preferences with optional channel-specific settings.

        Args:
            user: User to get preferences for
            channel: Optional ContentChannel for channel-specific prefs

        Returns:
            Dictionary of content preferences
        """
        cache_key = f"{self.CACHE_PREFIX}:content:{user.id}:{channel.id if channel else 'none'}"
        cached = cache.get(cache_key)
        if cached:
            return cached

        prefs = {
            'visual_style': None,
            'voice_id': None,
            'voice_name': None,
            'content_tone': None,
            'preferred_topics': [],
            'avoided_topics': [],
        }

        # Get from profile
        try:
            profile = EnhancedUserProfile.objects.get(user=user)
            if profile.communication_style:
                prefs['content_tone'] = profile.communication_style
        except EnhancedUserProfile.DoesNotExist:
            pass

        # Get from UserMemoryContext preferences
        memories = UserMemoryContext.objects.filter(
            user=user,
            memory_type='preference'
        ).order_by('-importance', '-created_at')[:10]

        for memory in memories:
            content_lower = memory.content.lower()
            metadata = memory.context_metadata or {}

            # Extract visual style preference
            if 'style' in content_lower or 'visual' in content_lower:
                if not prefs['visual_style']:
                    prefs['visual_style'] = metadata.get('value') or memory.content[:50]

            # Extract voice preference
            if 'voice' in content_lower:
                if not prefs['voice_id']:
                    prefs['voice_id'] = metadata.get('voice_id')
                    prefs['voice_name'] = metadata.get('voice_name')

            # Extract topic preferences
            if 'topic' in content_lower or 'interest' in content_lower:
                topic = metadata.get('topic') or memory.content[:50]
                if 'avoid' in content_lower or 'dislike' in content_lower:
                    prefs['avoided_topics'].append(topic)
                else:
                    prefs['preferred_topics'].append(topic)

        # Override with channel-specific if provided
        if channel:
            if channel.visual_style:
                prefs['visual_style'] = prefs['visual_style'] or channel.visual_style
            if channel.voice_id:
                prefs['voice_id'] = prefs['voice_id'] or channel.voice_id
                prefs['voice_name'] = prefs['voice_name'] or channel.voice_name

        cache.set(cache_key, prefs, self.CACHE_TTL)
        return prefs

    def _get_profile_context(self, user: User) -> Optional[str]:
        """Get context from EnhancedUserProfile."""
        try:
            profile = EnhancedUserProfile.objects.get(user=user)
        except EnhancedUserProfile.DoesNotExist:
            return None

        parts = []

        # Role
        if profile.primary_role:
            parts.append(f"Role: {profile.primary_role}")

        # Communication style
        if profile.communication_style:
            style_map = {
                'concise': 'prefers brief, to-the-point responses',
                'detailed': 'prefers comprehensive, detailed information',
                'balanced': 'prefers balanced responses based on context',
                'visual': 'prefers charts and visual explanations',
                'narrative': 'prefers story-based explanations'
            }
            style_desc = style_map.get(profile.communication_style, profile.communication_style)
            parts.append(f"Communication: {style_desc}")

        # Decision framework
        if profile.decision_framework:
            framework_map = {
                'data_driven': 'makes decisions based on data and metrics',
                'intuitive': 'trusts gut feeling and experience',
                'collaborative': 'prefers team consensus',
                'analytical': 'uses pros/cons analysis',
                'rapid': 'prefers quick decisions, iterate later'
            }
            framework_desc = framework_map.get(profile.decision_framework, profile.decision_framework)
            parts.append(f"Decision style: {framework_desc}")

        # Current projects (limit to top 3)
        if profile.current_projects:
            projects = profile.current_projects[:3] if isinstance(profile.current_projects, list) else []
            if projects:
                parts.append(f"Active projects: {', '.join(str(p) for p in projects)}")

        if not parts:
            return None

        return "Profile:\n- " + "\n- ".join(parts)

    def _get_weighted_memories(
        self,
        user: User,
        memory_types: List[str],
        limit: int = 5,
        days_back: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get memories with decay weighting applied.

        Args:
            user: User to get memories for
            memory_types: Types of memories to retrieve
            limit: Maximum number to return
            days_back: Optional limit to recent days

        Returns:
            List of memory dicts with decay_weight added
        """
        query = UserMemoryContext.objects.filter(
            user=user,
            memory_type__in=memory_types
        )

        if days_back:
            cutoff = timezone.now() - timedelta(days=days_back)
            query = query.filter(created_at__gte=cutoff)

        # Get more than we need, then sort by weighted score
        memories = list(query.order_by('-importance', '-created_at')[:limit * 2])

        # Calculate weighted scores
        weighted = []
        for memory in memories:
            decay_weight = self.calculate_decay_weight(memory.created_at)
            weighted_score = memory.importance * decay_weight
            weighted.append({
                'content': memory.content,
                'importance': memory.importance,
                'decay_weight': decay_weight,
                'weighted_score': weighted_score,
                'created_at': memory.created_at,
                'metadata': memory.context_metadata or {}
            })

        # Sort by weighted score and limit
        weighted.sort(key=lambda x: x['weighted_score'], reverse=True)
        return weighted[:limit]

    def _format_preferences(self, preferences: List[Dict]) -> str:
        """Format preferences for prompt."""
        if not preferences:
            return ""

        lines = ["Preferences:"]
        for pref in preferences:
            content = pref['content'][:100]  # Truncate
            lines.append(f"- {content}")

        return "\n".join(lines)

    def _format_goals(self, goals: List[Dict]) -> str:
        """Format goals for prompt."""
        if not goals:
            return ""

        lines = ["Goals:"]
        for goal in goals:
            content = goal['content'][:100]
            lines.append(f"- {content}")

        return "\n".join(lines)

    def _format_decisions(self, decisions: List[Dict]) -> str:
        """Format past decisions for prompt."""
        if not decisions:
            return ""

        lines = ["Recent decisions:"]
        for decision in decisions:
            content = decision['content'][:100]
            lines.append(f"- {content}")

        return "\n".join(lines)

    def store_preference(
        self,
        user: User,
        content: str,
        importance: int = 7,
        **metadata
    ) -> UserMemoryContext:
        """
        Store a new preference for the user.

        Args:
            user: User to store preference for
            content: Preference content
            importance: Importance level (1-10)
            **metadata: Additional metadata

        Returns:
            Created UserMemoryContext
        """
        # Ensure profile exists
        profile, _ = EnhancedUserProfile.objects.get_or_create(user=user)

        memory = UserMemoryContext.objects.create(
            user=user,
            profile=profile,
            memory_type='preference',
            content=content[:500],
            importance=min(max(importance, 1), 10),
            source='assistant',
            context_metadata={
                'stored_at': timezone.now().isoformat(),
                **metadata
            }
        )

        # Clear cache
        cache.delete(f"{self.CACHE_PREFIX}:prompt:{user.id}")
        cache.delete(f"{self.CACHE_PREFIX}:content:{user.id}:none")

        logger.info(f"Stored preference for {user.username}: {content[:50]}...")
        return memory

    def clear_cache(self, user: User):
        """Clear all cached context for a user."""
        cache.delete(f"{self.CACHE_PREFIX}:prompt:{user.id}")
        cache.delete(f"{self.CACHE_PREFIX}:content:{user.id}:none")
        logger.info(f"Cleared memory context cache for {user.username}")


# Convenience function
def get_memory_context_service(user: Optional[User] = None) -> MemoryContextService:
    """Get a MemoryContextService instance."""
    return MemoryContextService(user)

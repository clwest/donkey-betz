"""
Agent Learning Service
======================

Session 219 Phase C: Agent Personalization & Learning

This service enables the 14 AI Content agents to learn from user interactions
and adapt their behavior over time. Key features:

1. Interaction Tracking - Log all user interactions with agent outputs
2. Preference Learning - Learn user preferences from interaction patterns
3. Agent Memory - Short-term and long-term memory for each agent
4. Adaptive Context - Generate personalized context for agent operations
5. Knowledge Sharing - Share learned insights via the collaboration hub

The goal: Agents remember what users like and proactively suggest
content aligned with their preferences.
"""

import logging
import json
import redis
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime, timezone
from collections import defaultdict
from enum import Enum
import uuid

logger = logging.getLogger(__name__)


class InteractionType(Enum):
    """Types of user interactions with agent outputs"""
    CREATED = "created"        # User generated content
    EDITED = "edited"          # User modified output
    SAVED = "saved"            # User saved to gallery
    SHARED = "shared"          # User shared content
    DOWNLOADED = "downloaded"  # User downloaded
    RATED = "rated"            # User rated output
    USED = "used"              # User used suggestion
    REJECTED = "rejected"      # User rejected suggestion
    FAVORITED = "favorited"    # User marked as favorite


class PreferenceCategory(Enum):
    """Categories of learned preferences"""
    STYLE = "style"            # Visual/artistic styles
    THEME = "theme"            # Content themes
    MODEL = "model"            # AI model preferences
    QUALITY = "quality"        # Quality settings
    FORMAT = "format"          # Output formats
    COLOR = "color"            # Color preferences
    MOOD = "mood"              # Mood/tone preferences
    COMPLEXITY = "complexity"  # Detail level preferences


@dataclass
class AgentInteraction:
    """Records a single user interaction with an agent"""
    id: str
    user_id: int
    agent_name: str
    interaction_type: InteractionType
    input_data: Dict[str, Any]
    output_data: Dict[str, Any]
    rating: Optional[int] = None  # 1-5 stars
    was_modified: bool = False
    session_id: Optional[str] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'user_id': self.user_id,
            'agent_name': self.agent_name,
            'interaction_type': self.interaction_type.value,
            'input_data': self.input_data,
            'output_data': self.output_data,
            'rating': self.rating,
            'was_modified': self.was_modified,
            'session_id': self.session_id,
            'created_at': self.created_at.isoformat()
        }


@dataclass
class LearnedPreference:
    """A preference learned from user interactions"""
    category: PreferenceCategory
    value: str
    confidence: float  # 0-1, how confident we are
    occurrences: int
    last_seen: datetime
    positive_signals: int  # saved, rated high, etc.
    negative_signals: int  # rejected, edited heavily, etc.

    def to_dict(self) -> Dict[str, Any]:
        return {
            'category': self.category.value,
            'value': self.value,
            'confidence': self.confidence,
            'occurrences': self.occurrences,
            'last_seen': self.last_seen.isoformat(),
            'positive_signals': self.positive_signals,
            'negative_signals': self.negative_signals
        }


@dataclass
class AgentMemory:
    """Memory store for an agent about a user"""
    user_id: int
    agent_name: str
    short_term: List[Dict[str, Any]] = field(default_factory=list)  # Recent (session)
    long_term: Dict[str, LearnedPreference] = field(default_factory=dict)  # Permanent
    interaction_count: int = 0
    first_interaction: Optional[datetime] = None
    last_interaction: Optional[datetime] = None


class AgentLearningService:
    """
    Central service for agent learning and personalization.

    Integrates with:
    - 14 AI Content agents (from ai_content_agents.py)
    - Agent Collaboration Hub (for knowledge sharing)
    - Redis for fast caching
    - Existing preference systems (StyleMemory, UserCreativePreference)
    """

    # Memory retention settings
    SHORT_TERM_LIMIT = 20       # Max items in short-term memory
    CONFIDENCE_THRESHOLD = 0.6  # Min confidence for preference
    DECAY_DAYS = 30             # Days before preference weight decays

    # Redis keys
    REDIS_PREFIX = "agent_learning"

    def __init__(self, redis_config: Dict[str, Any] = None):
        self.redis_config = redis_config or {
            'host': 'localhost',
            'port': 6379,
            'db': 5  # Use db=5 for agent learning
        }

        self.redis_client = None
        self._connect_redis()

        # In-memory caches
        self._user_memories: Dict[str, AgentMemory] = {}
        self._interaction_buffer: List[AgentInteraction] = []

        logger.info("Agent Learning Service initialized")

    def _connect_redis(self):
        """Connect to Redis"""
        try:
            self.redis_client = redis.Redis(**self.redis_config, decode_responses=True)
            self.redis_client.ping()
            logger.info("Agent Learning Service connected to Redis")
        except Exception as e:
            logger.warning(f"Redis not available: {e}")
            self.redis_client = None

    # ===== Interaction Tracking (C1) =====

    def record_interaction(
        self,
        user_id: int,
        agent_name: str,
        interaction_type: InteractionType,
        input_data: Dict[str, Any],
        output_data: Dict[str, Any],
        rating: Optional[int] = None,
        was_modified: bool = False,
        session_id: Optional[str] = None
    ) -> AgentInteraction:
        """
        Record a user interaction with an agent.

        This is the primary entry point for learning. Every time a user
        interacts with agent output (create, edit, save, rate, etc.),
        call this method.
        """
        interaction = AgentInteraction(
            id=f"int_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:6]}",
            user_id=user_id,
            agent_name=agent_name,
            interaction_type=interaction_type,
            input_data=input_data,
            output_data=output_data,
            rating=rating,
            was_modified=was_modified,
            session_id=session_id
        )

        # Add to buffer
        self._interaction_buffer.append(interaction)

        # Update user memory
        self._update_memory(interaction)

        # Learn from interaction
        self._learn_from_interaction(interaction)

        # Persist to Redis
        self._persist_interaction(interaction)

        logger.debug(f"Recorded interaction: {user_id}/{agent_name}/{interaction_type.value}")

        return interaction

    def _update_memory(self, interaction: AgentInteraction):
        """Update user's agent memory with new interaction"""
        key = f"{interaction.user_id}:{interaction.agent_name}"

        if key not in self._user_memories:
            self._user_memories[key] = AgentMemory(
                user_id=interaction.user_id,
                agent_name=interaction.agent_name,
                first_interaction=interaction.created_at
            )

        memory = self._user_memories[key]

        # Update short-term memory
        memory.short_term.append(interaction.to_dict())
        if len(memory.short_term) > self.SHORT_TERM_LIMIT:
            memory.short_term.pop(0)

        # Update stats
        memory.interaction_count += 1
        memory.last_interaction = interaction.created_at

    def _persist_interaction(self, interaction: AgentInteraction):
        """Persist interaction to Redis"""
        if not self.redis_client:
            return

        try:
            key = f"{self.REDIS_PREFIX}:interactions:{interaction.user_id}:{interaction.agent_name}"
            # Store in sorted set with timestamp as score
            self.redis_client.zadd(
                key,
                {json.dumps(interaction.to_dict()): interaction.created_at.timestamp()}
            )
            # Trim to last 100 interactions
            self.redis_client.zremrangebyrank(key, 0, -101)
        except Exception as e:
            logger.error(f"Error persisting interaction: {e}")

    # ===== Preference Learning (C2) =====

    def _learn_from_interaction(self, interaction: AgentInteraction):
        """Learn user preferences from an interaction"""
        key = f"{interaction.user_id}:{interaction.agent_name}"
        memory = self._user_memories.get(key)

        if not memory:
            return

        # Extract signals from interaction
        signals = self._extract_preference_signals(interaction)

        for category, value, is_positive in signals:
            self._update_preference(memory, category, value, is_positive)

    def _extract_preference_signals(
        self,
        interaction: AgentInteraction
    ) -> List[tuple]:
        """Extract preference signals from interaction"""
        signals = []
        input_data = interaction.input_data
        output_data = interaction.output_data

        # Determine if interaction was positive
        is_positive = interaction.interaction_type in [
            InteractionType.SAVED,
            InteractionType.FAVORITED,
            InteractionType.SHARED,
            InteractionType.USED
        ] or (interaction.rating and interaction.rating >= 4)

        is_negative = interaction.interaction_type == InteractionType.REJECTED or \
                      (interaction.rating and interaction.rating <= 2) or \
                      interaction.was_modified

        # Extract style preferences
        if 'style' in input_data:
            signals.append((
                PreferenceCategory.STYLE,
                input_data['style'],
                is_positive and not is_negative
            ))

        # Extract model preferences
        if 'model' in input_data:
            signals.append((
                PreferenceCategory.MODEL,
                input_data['model'],
                is_positive and not is_negative
            ))

        # Extract quality preferences
        if 'quality' in input_data or 'output_format' in input_data:
            quality = input_data.get('quality', input_data.get('output_format', 'standard'))
            signals.append((
                PreferenceCategory.QUALITY,
                quality,
                is_positive
            ))

        # Extract theme from prompt
        prompt = input_data.get('prompt', '')
        themes = self._extract_themes(prompt)
        for theme in themes:
            signals.append((
                PreferenceCategory.THEME,
                theme,
                is_positive and not is_negative
            ))

        # Extract color preferences if present
        if 'colors' in output_data or 'dominant_colors' in output_data:
            colors = output_data.get('colors', output_data.get('dominant_colors', []))
            for color in colors[:3]:  # Top 3 colors
                signals.append((
                    PreferenceCategory.COLOR,
                    color,
                    is_positive
                ))

        return signals

    def _extract_themes(self, prompt: str) -> List[str]:
        """Extract themes from a prompt"""
        themes = []

        # Simple keyword-based theme extraction
        theme_keywords = {
            'cyberpunk': ['cyberpunk', 'neon', 'futuristic', 'cyber', 'synthwave'],
            'fantasy': ['fantasy', 'magic', 'dragon', 'elf', 'medieval', 'mythical'],
            'nature': ['nature', 'forest', 'mountain', 'ocean', 'landscape', 'wildlife'],
            'portrait': ['portrait', 'face', 'person', 'character', 'headshot'],
            'abstract': ['abstract', 'geometric', 'pattern', 'minimalist'],
            'vintage': ['vintage', 'retro', 'old', 'classic', 'nostalgic'],
            'dark': ['dark', 'gothic', 'noir', 'shadow', 'moody'],
            'bright': ['bright', 'colorful', 'vibrant', 'cheerful', 'happy'],
            'professional': ['professional', 'corporate', 'business', 'clean'],
            'artistic': ['artistic', 'creative', 'experimental', 'avant-garde']
        }

        prompt_lower = prompt.lower()
        for theme, keywords in theme_keywords.items():
            if any(kw in prompt_lower for kw in keywords):
                themes.append(theme)

        return themes[:3]  # Max 3 themes

    def _update_preference(
        self,
        memory: AgentMemory,
        category: PreferenceCategory,
        value: str,
        is_positive: bool
    ):
        """Update a learned preference"""
        key = f"{category.value}:{value}"

        if key not in memory.long_term:
            memory.long_term[key] = LearnedPreference(
                category=category,
                value=value,
                confidence=0.5,  # Start neutral
                occurrences=0,
                last_seen=datetime.now(timezone.utc),
                positive_signals=0,
                negative_signals=0
            )

        pref = memory.long_term[key]
        pref.occurrences += 1
        pref.last_seen = datetime.now(timezone.utc)

        if is_positive:
            pref.positive_signals += 1
        else:
            pref.negative_signals += 1

        # Recalculate confidence
        total = pref.positive_signals + pref.negative_signals
        if total > 0:
            pref.confidence = pref.positive_signals / total

    # ===== Agent Memory (C3) =====

    def get_user_memory(self, user_id: int, agent_name: str) -> Optional[AgentMemory]:
        """Get memory for a user-agent pair"""
        key = f"{user_id}:{agent_name}"

        # Try in-memory cache
        if key in self._user_memories:
            return self._user_memories[key]

        # Try Redis
        if self.redis_client:
            memory = self._load_memory_from_redis(user_id, agent_name)
            if memory:
                self._user_memories[key] = memory
                return memory

        return None

    def _load_memory_from_redis(self, user_id: int, agent_name: str) -> Optional[AgentMemory]:
        """Load user memory from Redis"""
        try:
            prefs_key = f"{self.REDIS_PREFIX}:preferences:{user_id}:{agent_name}"
            prefs_data = self.redis_client.hgetall(prefs_key)

            if not prefs_data:
                return None

            memory = AgentMemory(user_id=user_id, agent_name=agent_name)

            for key, value in prefs_data.items():
                try:
                    pref_data = json.loads(value)
                    memory.long_term[key] = LearnedPreference(
                        category=PreferenceCategory(pref_data['category']),
                        value=pref_data['value'],
                        confidence=pref_data['confidence'],
                        occurrences=pref_data['occurrences'],
                        last_seen=datetime.fromisoformat(pref_data['last_seen']),
                        positive_signals=pref_data['positive_signals'],
                        negative_signals=pref_data['negative_signals']
                    )
                except Exception as _e:
                    logger.warning(
                        "agent_learning_service._load_memory_from_redis: swallowed (%s: %s) — degraded",
                        type(_e).__name__, _e,
                    )

            return memory

        except Exception as e:
            logger.error(f"Error loading memory from Redis: {e}")
            return None

    def save_memory(self, user_id: int, agent_name: str):
        """Save user memory to Redis"""
        key = f"{user_id}:{agent_name}"
        memory = self._user_memories.get(key)

        if not memory or not self.redis_client:
            return

        try:
            prefs_key = f"{self.REDIS_PREFIX}:preferences:{user_id}:{agent_name}"

            for pref_key, pref in memory.long_term.items():
                self.redis_client.hset(prefs_key, pref_key, json.dumps(pref.to_dict()))

        except Exception as e:
            logger.error(f"Error saving memory: {e}")

    def get_top_preferences(
        self,
        user_id: int,
        agent_name: str,
        category: Optional[PreferenceCategory] = None,
        limit: int = 5
    ) -> List[LearnedPreference]:
        """Get top learned preferences for a user-agent pair"""
        memory = self.get_user_memory(user_id, agent_name)
        if not memory:
            return []

        prefs = list(memory.long_term.values())

        # Filter by category
        if category:
            prefs = [p for p in prefs if p.category == category]

        # Filter by confidence threshold
        prefs = [p for p in prefs if p.confidence >= self.CONFIDENCE_THRESHOLD]

        # Sort by confidence * occurrences
        prefs.sort(key=lambda p: p.confidence * p.occurrences, reverse=True)

        return prefs[:limit]

    # ===== Adaptive Context (C4) =====

    def get_adaptive_context(self, user_id: int, agent_name: str) -> str:
        """
        Generate adaptive context string for an agent based on learned preferences.

        This context is injected into agent prompts to personalize behavior.
        """
        preferences = self.get_top_preferences(user_id, agent_name, limit=10)

        if not preferences:
            return ""

        # Group by category
        by_category = defaultdict(list)
        for pref in preferences:
            by_category[pref.category.value].append(pref.value)

        # Build context string
        lines = ["User Preferences (learned from interactions):"]

        if 'style' in by_category:
            lines.append(f"- Preferred styles: {', '.join(by_category['style'][:3])}")

        if 'theme' in by_category:
            lines.append(f"- Common themes: {', '.join(by_category['theme'][:3])}")

        if 'model' in by_category:
            lines.append(f"- Preferred models: {', '.join(by_category['model'][:2])}")

        if 'quality' in by_category:
            lines.append(f"- Quality preference: {by_category['quality'][0]}")

        if 'color' in by_category:
            lines.append(f"- Color preferences: {', '.join(by_category['color'][:3])}")

        if 'mood' in by_category:
            lines.append(f"- Preferred mood: {by_category['mood'][0]}")

        return "\n".join(lines)

    def apply_preferences_to_params(
        self,
        user_id: int,
        agent_name: str,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Apply learned preferences to generation parameters.

        Only fills in missing parameters - user-specified values take precedence.
        """
        result = params.copy()

        # Get style preferences
        style_prefs = self.get_top_preferences(user_id, agent_name, PreferenceCategory.STYLE, limit=1)
        if style_prefs and 'style' not in result:
            result['style'] = style_prefs[0].value

        # Get model preferences
        model_prefs = self.get_top_preferences(user_id, agent_name, PreferenceCategory.MODEL, limit=1)
        if model_prefs and 'model' not in result:
            result['model'] = model_prefs[0].value

        # Get quality preferences
        quality_prefs = self.get_top_preferences(user_id, agent_name, PreferenceCategory.QUALITY, limit=1)
        if quality_prefs and 'quality' not in result:
            result['quality'] = quality_prefs[0].value

        return result

    # ===== Knowledge Sharing Integration (C4 - Wire to collaboration) =====

    def share_learning_as_knowledge(self, user_id: int, agent_name: str):
        """
        Share learned preferences with other agents via the collaboration hub.

        This allows agents to learn from each other's user interactions.
        """
        try:
            from core.services.agent_collaboration_hub import get_collaboration_hub

            hub = get_collaboration_hub()
            preferences = self.get_top_preferences(user_id, agent_name, limit=5)

            if not preferences:
                return

            # Format as knowledge
            content = {
                'user_id': user_id,
                'preferences': [p.to_dict() for p in preferences],
                'agent_name': agent_name,
                'learned_at': datetime.now(timezone.utc).isoformat()
            }

            # Share knowledge
            hub.share_knowledge(
                agent_name=agent_name,
                category='user_preferences',
                title=f"User {user_id} preferences from {agent_name}",
                content=content,
                confidence=sum(p.confidence for p in preferences) / len(preferences),
                tags=['user_preferences', agent_name, f'user_{user_id}']
            )

            logger.debug(f"Shared learning as knowledge: {agent_name} for user {user_id}")

        except Exception as e:
            logger.error(f"Error sharing learning: {e}")

    # ===== Statistics & Analytics =====

    def get_learning_stats(self, user_id: int) -> Dict[str, Any]:
        """Get learning statistics for a user across all agents"""
        stats = {
            'total_interactions': 0,
            'agents_interacted': [],
            'preferences_learned': 0,
            'top_styles': [],
            'top_themes': [],
            'learning_progress': {}
        }

        # Collect stats from all agent memories
        for key, memory in self._user_memories.items():
            if key.startswith(f"{user_id}:"):
                agent_name = key.split(':')[1]
                stats['agents_interacted'].append(agent_name)
                stats['total_interactions'] += memory.interaction_count
                stats['preferences_learned'] += len(memory.long_term)

                # Track learning progress per agent
                stats['learning_progress'][agent_name] = {
                    'interactions': memory.interaction_count,
                    'preferences': len(memory.long_term),
                    'confidence_avg': sum(
                        p.confidence for p in memory.long_term.values()
                    ) / max(len(memory.long_term), 1)
                }

        # Get top styles across all agents
        all_style_prefs = []
        for key, memory in self._user_memories.items():
            if key.startswith(f"{user_id}:"):
                all_style_prefs.extend([
                    p for p in memory.long_term.values()
                    if p.category == PreferenceCategory.STYLE and p.confidence >= 0.6
                ])

        # Sort and get top
        all_style_prefs.sort(key=lambda p: p.confidence * p.occurrences, reverse=True)
        stats['top_styles'] = [p.value for p in all_style_prefs[:5]]

        # Get top themes
        all_theme_prefs = []
        for key, memory in self._user_memories.items():
            if key.startswith(f"{user_id}:"):
                all_theme_prefs.extend([
                    p for p in memory.long_term.values()
                    if p.category == PreferenceCategory.THEME and p.confidence >= 0.6
                ])

        all_theme_prefs.sort(key=lambda p: p.confidence * p.occurrences, reverse=True)
        stats['top_themes'] = [p.value for p in all_theme_prefs[:5]]

        return stats

    def get_user_preferences_summary(self, user_id: int, agent_name: str) -> Dict[str, Any]:
        """Get a summary of learned preferences for a user-agent pair"""
        memory = self.get_user_memory(user_id, agent_name)

        if not memory:
            return {
                'status': 'no_data',
                'message': 'No interactions recorded yet',
                'preferences': {}
            }

        # Group preferences by category
        by_category = {}
        for pref in memory.long_term.values():
            cat = pref.category.value
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append({
                'value': pref.value,
                'confidence': round(pref.confidence, 2),
                'occurrences': pref.occurrences
            })

        # Sort each category by confidence
        for cat in by_category:
            by_category[cat].sort(key=lambda x: x['confidence'], reverse=True)
            by_category[cat] = by_category[cat][:5]  # Top 5 per category

        return {
            'status': 'ok',
            'interaction_count': memory.interaction_count,
            'first_interaction': memory.first_interaction.isoformat() if memory.first_interaction else None,
            'last_interaction': memory.last_interaction.isoformat() if memory.last_interaction else None,
            'preferences': by_category
        }

    def clear_user_preferences(self, user_id: int, agent_name: Optional[str] = None):
        """Clear learned preferences for a user"""
        keys_to_remove = []

        for key in list(self._user_memories.keys()):
            if key.startswith(f"{user_id}:"):
                if agent_name is None or key == f"{user_id}:{agent_name}":
                    keys_to_remove.append(key)

        for key in keys_to_remove:
            del self._user_memories[key]

        # Clear from Redis
        if self.redis_client:
            try:
                if agent_name:
                    self.redis_client.delete(
                        f"{self.REDIS_PREFIX}:preferences:{user_id}:{agent_name}"
                    )
                    self.redis_client.delete(
                        f"{self.REDIS_PREFIX}:interactions:{user_id}:{agent_name}"
                    )
                else:
                    # Clear all for user - get all keys matching pattern
                    for key in self.redis_client.scan_iter(
                        f"{self.REDIS_PREFIX}:*:{user_id}:*"
                    ):
                        self.redis_client.delete(key)
            except Exception as e:
                logger.error(f"Error clearing Redis preferences: {e}")

        logger.info(f"Cleared preferences for user {user_id}, agent={agent_name}")


# Global service instance
_learning_service: Optional[AgentLearningService] = None


def get_learning_service() -> AgentLearningService:
    """Get the global learning service instance"""
    global _learning_service
    if _learning_service is None:
        _learning_service = AgentLearningService()
    return _learning_service


# Convenience functions
def record_interaction(
    user_id: int,
    agent_name: str,
    interaction_type: str,
    input_data: Dict[str, Any],
    output_data: Dict[str, Any],
    rating: Optional[int] = None,
    was_modified: bool = False
) -> AgentInteraction:
    """Record a user interaction (convenience function)"""
    service = get_learning_service()
    return service.record_interaction(
        user_id=user_id,
        agent_name=agent_name,
        interaction_type=InteractionType(interaction_type),
        input_data=input_data,
        output_data=output_data,
        rating=rating,
        was_modified=was_modified
    )


def get_adaptive_context(user_id: int, agent_name: str) -> str:
    """Get adaptive context for an agent (convenience function)"""
    service = get_learning_service()
    return service.get_adaptive_context(user_id, agent_name)


def apply_preferences(user_id: int, agent_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """Apply preferences to parameters (convenience function)"""
    service = get_learning_service()
    return service.apply_preferences_to_params(user_id, agent_name, params)


logger.info("Agent Learning Service module loaded")

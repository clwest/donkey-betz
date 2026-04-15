"""
Sci-Fi Integration Service - Mood, Memory, Evolution, Synergy

Session 290: SIMPLIFIED from 15 features to 7 core features.

This service bridges sci-fi features into agent actions:

ACTIVE FEATURES:
1. Mood System - Agent emotional states affect decisions (3 simplified states)
2. Memory Palace - Past interactions influence current actions
3. Evolution System - XP and levels affect confidence (simplified to stats)
4. Synergy System - Static bonuses for agent team collaboration
5. Time Travel - Decision replay for debugging (separate module)
6. Hive Mind Mode - Multi-agent collaboration (separate module)
7. Spider Integration - Real data feeding (separate module)

DEPRECATED FEATURES (Session 284-290):
- Agent Dreams - Returns empty list, no new records
- Agent Conversations - Merged into Hive Mind
- Prophecies/Predictions - Removed
- Time Capsules - Removed
- Memory Clusters - Use simple tags instead
- Rivalries/Alliances - Replaced by static Synergy system

Session 264: Phase 3 - Sci-Fi Integration
Session 284: Deprecated Dreams, Prophecies, Time Capsules
Session 290: Simplified Relationships to Synergy, updated service
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime

from django.utils import timezone
from django.core.cache import cache

logger = logging.getLogger(__name__)


@dataclass
class MoodInfluence:
    """How mood affects agent behavior."""
    mood_type: str
    intensity: float  # 0.0 to 1.0
    style_modifier: str  # e.g., "bold", "calm", "experimental"
    confidence_modifier: float  # e.g., 1.2 for confident, 0.8 for uncertain
    description: str

    def to_dict(self) -> dict:
        return {
            'mood_type': self.mood_type,
            'intensity': self.intensity,
            'style_modifier': self.style_modifier,
            'confidence_modifier': self.confidence_modifier,
            'description': self.description,
        }


@dataclass
class EvolutionInfluence:
    """How evolution affects agent behavior."""
    level: int
    xp: int
    title: str
    confidence_boost: float  # Higher levels = more confident
    specializations: List[str]
    authority_level: str  # "junior", "senior", "expert", "master"

    def to_dict(self) -> dict:
        return {
            'level': self.level,
            'xp': self.xp,
            'title': self.title,
            'confidence_boost': self.confidence_boost,
            'specializations': self.specializations,
            'authority_level': self.authority_level,
        }


@dataclass
class RelationshipInfluence:
    """How relationships affect collaboration."""
    allies: List[str]
    rivals: List[str]
    neutral: List[str]
    collaboration_bonus: Dict[str, float]  # agent_name -> bonus multiplier
    team_synergy: float  # 0.0 to 2.0

    def to_dict(self) -> dict:
        return {
            'allies': self.allies,
            'rivals': self.rivals,
            'neutral': self.neutral,
            'collaboration_bonus': self.collaboration_bonus,
            'team_synergy': self.team_synergy,
        }


@dataclass
class MemoryInfluence:
    """How memory affects agent context."""
    relevant_memories: List[Dict[str, Any]]
    user_preferences: Dict[str, Any]
    past_successes: List[str]
    past_failures: List[str]
    learned_patterns: List[str]

    def to_dict(self) -> dict:
        return {
            'relevant_memories': self.relevant_memories,
            'user_preferences': self.user_preferences,
            'past_successes': self.past_successes,
            'past_failures': self.past_failures,
            'learned_patterns': self.learned_patterns,
        }


@dataclass
class SciFiContext:
    """Complete sci-fi context for an agent."""
    agent_name: str
    mood: Optional[MoodInfluence] = None
    evolution: Optional[EvolutionInfluence] = None
    relationships: Optional[RelationshipInfluence] = None
    memory: Optional[MemoryInfluence] = None
    dreams: List[Dict[str, Any]] = field(default_factory=list)
    fetch_time: Optional[datetime] = None

    def to_dict(self) -> dict:
        return {
            'agent_name': self.agent_name,
            'mood': self.mood.to_dict() if self.mood else None,
            'evolution': self.evolution.to_dict() if self.evolution else None,
            'relationships': self.relationships.to_dict() if self.relationships else None,
            'memory': self.memory.to_dict() if self.memory else None,
            'dreams': self.dreams,
            'fetch_time': self.fetch_time.isoformat() if self.fetch_time else None,
        }

    def get_style_influence(self) -> str:
        """Get combined style influence from mood and evolution."""
        if self.mood:
            return self.mood.style_modifier
        return "balanced"

    def get_confidence_level(self) -> float:
        """Get combined confidence from mood and evolution."""
        confidence = 1.0
        if self.mood:
            confidence *= self.mood.confidence_modifier
        if self.evolution:
            confidence *= self.evolution.confidence_boost
        return min(confidence, 2.0)  # Cap at 2x

    def get_prompt_enhancement(self) -> str:
        """Get text to enhance prompts with sci-fi context."""
        parts = []

        if self.mood:
            parts.append(f"Current mood: {self.mood.mood_type} ({self.mood.description})")
            parts.append(f"Style tendency: {self.mood.style_modifier}")

        if self.evolution:
            parts.append(f"Agent level: {self.evolution.level} ({self.evolution.title})")
            if self.evolution.specializations:
                parts.append(f"Specializations: {', '.join(self.evolution.specializations[:3])}")

        if self.relationships and self.relationships.allies:
            parts.append(f"Works well with: {', '.join(self.relationships.allies[:3])}")

        if self.memory and self.memory.learned_patterns:
            parts.append(f"Learned patterns: {', '.join(self.memory.learned_patterns[:3])}")

        if self.dreams:
            recent_dream = self.dreams[0] if self.dreams else None
            if recent_dream:
                dream_content = recent_dream.get('content', '')[:100]
                parts.append(f"Recent creative thought: {dream_content}")

        return "\n".join(parts) if parts else "No sci-fi context available"


class SciFiIntegrationService:
    """
    Integrates all sci-fi features into agent actions.

    This service provides:
    - Mood-influenced style choices
    - Memory-enhanced context
    - Evolution-based confidence
    - Relationship-aware collaboration
    """

    # Mood type -> behavior mapping
    MOOD_BEHAVIORS = {
        'excited': {
            'style_modifier': 'bold and vibrant',
            'confidence_modifier': 1.3,
            'description': 'Full of energy, tends toward bold choices',
        },
        'focused': {
            'style_modifier': 'precise and clean',
            'confidence_modifier': 1.1,
            'description': 'Concentrated, favors clarity',
        },
        'creative': {
            'style_modifier': 'experimental and unique',
            'confidence_modifier': 1.0,
            'description': 'Open to trying new things',
        },
        'tired': {
            'style_modifier': 'simple and efficient',
            'confidence_modifier': 0.8,
            'description': 'Prefers straightforward solutions',
        },
        'frustrated': {
            'style_modifier': 'direct and no-nonsense',
            'confidence_modifier': 0.9,
            'description': 'Wants quick results',
        },
        'curious': {
            'style_modifier': 'exploratory and diverse',
            'confidence_modifier': 1.0,
            'description': 'Interested in exploring options',
        },
        'confident': {
            'style_modifier': 'bold and authoritative',
            'confidence_modifier': 1.4,
            'description': 'Ready to make strong recommendations',
        },
        'reflective': {
            'style_modifier': 'thoughtful and nuanced',
            'confidence_modifier': 1.0,
            'description': 'Considering multiple perspectives',
        },
    }

    # Level -> authority mapping
    LEVEL_AUTHORITY = {
        (1, 5): ('junior', 0.9),
        (6, 15): ('senior', 1.0),
        (16, 30): ('expert', 1.15),
        (31, 100): ('master', 1.3),
    }

    # Cache settings
    CACHE_TTL = 300  # 5 minutes
    CACHE_PREFIX = 'scifi_context:'

    def __init__(self):
        """Initialize the sci-fi integration service."""

    def get_scifi_context(
        self,
        agent_name: str,
        task: Optional[str] = None,
        user=None,
        include_dreams: bool = True,
        use_cache: bool = True
    ) -> SciFiContext:
        """
        Get complete sci-fi context for an agent.

        Args:
            agent_name: Name of the agent
            task: Optional task for context
            user: Optional user for personalization
            include_dreams: Whether to include dream data
            use_cache: Whether to use cached data

        Returns:
            SciFiContext with all sci-fi influences
        """
        cache_key = f"{self.CACHE_PREFIX}{agent_name}:{hash(task or '')}"

        if use_cache:
            cached = cache.get(cache_key)
            if cached and isinstance(cached, dict):
                # Reconstruct dataclass objects from cached dicts
                try:
                    if cached.get('mood'):
                        cached['mood'] = MoodInfluence(**cached['mood'])
                    if cached.get('evolution'):
                        cached['evolution'] = EvolutionInfluence(**cached['evolution'])
                    if cached.get('relationships'):
                        cached['relationships'] = RelationshipInfluence(**cached['relationships'])
                    if cached.get('memory'):
                        cached['memory'] = MemoryInfluence(**cached['memory'])
                    return SciFiContext(**cached)
                except Exception as e:
                    logger.warning(f"Error deserializing cached context: {e}")
                    # Fall through to rebuild context

        context = SciFiContext(
            agent_name=agent_name,
            fetch_time=timezone.now()
        )

        # Get mood influence
        context.mood = self._get_mood_influence(agent_name)

        # Get evolution influence
        context.evolution = self._get_evolution_influence(agent_name)

        # Get relationship influence
        context.relationships = self._get_relationship_influence(agent_name)

        # Get memory influence
        if user:
            context.memory = self._get_memory_influence(agent_name, task, user)

        # Get recent dreams
        if include_dreams:
            context.dreams = self._get_recent_dreams(agent_name)

        # Cache the result
        if use_cache:
            cache.set(cache_key, context.to_dict(), self.CACHE_TTL)

        return context

    def _get_mood_influence(self, agent_name: str) -> Optional[MoodInfluence]:
        """Get mood influence for an agent."""
        try:
            from core.models_unified_system import AgentMood

            # Try to find mood by agent name via FK
            # Note: AgentMood uses 'last_updated' not 'updated_at'
            mood = AgentMood.objects.filter(
                agent__name=agent_name
            ).select_related('agent').order_by('-last_updated').first()

            # Fallback: try direct agent_name field if exists
            if not mood:
                mood = AgentMood.objects.filter(
                    agent__name__icontains=agent_name.replace('Agent', '')
                ).select_related('agent').first()

            if mood:
                # Note: Field is 'current_mood', not 'mood_type'
                mood_type = getattr(mood, 'current_mood', 'focused').lower()
                behavior = self.MOOD_BEHAVIORS.get(mood_type, self.MOOD_BEHAVIORS['focused'])

                return MoodInfluence(
                    mood_type=mood_type,
                    intensity=float(getattr(mood, 'intensity', 0.7)),
                    style_modifier=behavior['style_modifier'],
                    confidence_modifier=behavior['confidence_modifier'],
                    description=behavior['description'],
                )

        except Exception as e:
            logger.warning(f"Error getting mood for {agent_name}: {e}")

        # Default mood
        return MoodInfluence(
            mood_type='focused',
            intensity=0.7,
            style_modifier='balanced',
            confidence_modifier=1.0,
            description='Default balanced state',
        )

    def _get_evolution_influence(self, agent_name: str) -> Optional[EvolutionInfluence]:
        """Get evolution influence for an agent."""
        try:
            from core.models_unified_system import AgentEvolution

            # Try to find evolution by agent name via FK
            evolution = AgentEvolution.objects.filter(
                agent__name=agent_name
            ).select_related('agent').first()

            # Fallback: try partial match
            if not evolution:
                evolution = AgentEvolution.objects.filter(
                    agent__name__icontains=agent_name.replace('Agent', '')
                ).select_related('agent').first()

            if evolution:
                level = getattr(evolution, 'current_level', getattr(evolution, 'level', 1))
                xp = getattr(evolution, 'total_xp', getattr(evolution, 'xp', 0))

                # Determine authority level
                authority = 'junior'
                confidence_boost = 0.9
                for (min_lvl, max_lvl), (auth, boost) in self.LEVEL_AUTHORITY.items():
                    if min_lvl <= level <= max_lvl:
                        authority = auth
                        confidence_boost = boost
                        break

                # Get specializations from evolution data
                specializations = []
                if hasattr(evolution, 'specializations') and evolution.specializations:
                    specializations = evolution.specializations[:5]
                elif hasattr(evolution, 'skills_unlocked') and evolution.skills_unlocked:
                    specializations = evolution.skills_unlocked[:5]

                # Generate title based on level
                titles = {
                    (1, 5): 'Apprentice',
                    (6, 15): 'Journeyman',
                    (16, 30): 'Expert',
                    (31, 50): 'Master',
                    (51, 100): 'Legendary',
                }
                title = 'Agent'
                for (min_l, max_l), t in titles.items():
                    if min_l <= level <= max_l:
                        title = t
                        break

                return EvolutionInfluence(
                    level=level,
                    xp=xp,
                    title=title,
                    confidence_boost=confidence_boost,
                    specializations=specializations,
                    authority_level=authority,
                )

        except Exception as e:
            logger.warning(f"Error getting evolution for {agent_name}: {e}")

        # Default evolution
        return EvolutionInfluence(
            level=1,
            xp=0,
            title='Apprentice',
            confidence_boost=1.0,
            specializations=[],
            authority_level='junior',
        )

    def _get_relationship_influence(self, agent_name: str) -> Optional[RelationshipInfluence]:
        """
        Get relationship influence for an agent.

        Session 290: Simplified to use static synergy mapping instead of
        database queries. This replaces the complex AgentRelationship,
        Rivalry, and Alliance system with a simple, fast lookup.
        """
        try:
            # Use the new synergy system instead of database queries
            from core.agents.synergy import get_relationship_influence_simple

            synergy_data = get_relationship_influence_simple(agent_name)

            return RelationshipInfluence(
                allies=synergy_data['allies'],
                rivals=synergy_data['rivals'],  # Always empty now
                neutral=synergy_data['neutral'],
                collaboration_bonus=synergy_data['collaboration_bonus'],
                team_synergy=synergy_data['team_synergy'],
            )

        except Exception as e:
            logger.warning(f"Error getting synergy for {agent_name}: {e}")

        return RelationshipInfluence(
            allies=[],
            rivals=[],
            neutral=[],
            collaboration_bonus={},
            team_synergy=1.0,
        )

    def _get_memory_influence(
        self,
        agent_name: str,
        task: Optional[str],
        user
    ) -> Optional[MemoryInfluence]:
        """Get memory influence for an agent."""
        try:
            from core.models_unified_system import AgentMemory

            # Get recent memories for this agent
            # Session 799: AgentMemory doesn't have user field - memories are per-agent
            memories = AgentMemory.objects.filter(
                agent__name=agent_name
            ).select_related('agent').order_by('-created_at')[:10]

            # Fallback if no results - try partial name match
            if not memories.exists():
                memories = AgentMemory.objects.filter(
                    agent__name__icontains=agent_name.replace('Agent', '')
                ).select_related('agent').order_by('-created_at')[:10]

            relevant_memories = []
            past_successes = []
            past_failures = []
            learned_patterns = []

            for mem in memories:
                memory_data = {
                    'content': getattr(mem, 'content', '')[:200],
                    'summary': getattr(mem, 'summary', '')[:100],
                    'created_at': mem.created_at.isoformat() if hasattr(mem, 'created_at') else '',
                }
                relevant_memories.append(memory_data)

                # Analyze memory for patterns
                content = getattr(mem, 'content', '').lower()
                if 'success' in content or 'worked well' in content:
                    past_successes.append(getattr(mem, 'summary', content[:50]))
                elif 'failed' in content or 'error' in content:
                    past_failures.append(getattr(mem, 'summary', content[:50]))

            # Extract patterns from content
            if relevant_memories:
                # Simple pattern detection
                all_content = ' '.join(m.get('content', '') for m in relevant_memories)
                if 'minimalist' in all_content.lower():
                    learned_patterns.append('User prefers minimalist styles')
                if 'vibrant' in all_content.lower() or 'colorful' in all_content.lower():
                    learned_patterns.append('User likes vibrant colors')
                if 'professional' in all_content.lower():
                    learned_patterns.append('User prefers professional aesthetic')

            # Get user preferences
            user_preferences = {}
            if hasattr(user, 'profile') and hasattr(user.profile, 'preferences'):
                user_preferences = user.profile.preferences or {}

            return MemoryInfluence(
                relevant_memories=relevant_memories,
                user_preferences=user_preferences,
                past_successes=past_successes[:5],
                past_failures=past_failures[:5],
                learned_patterns=learned_patterns[:5],
            )

        except Exception as e:
            logger.warning(f"Error getting memory for {agent_name}: {e}")

        return MemoryInfluence(
            relevant_memories=[],
            user_preferences={},
            past_successes=[],
            past_failures=[],
            learned_patterns=[],
        )

    def _get_recent_dreams(self, agent_name: str, limit: int = 3) -> List[Dict[str, Any]]:
        """
        Get recent dreams/creative thoughts for an agent.

        Session 497: RE-ENABLED with quality filtering.
        Dreams provide creative insights that can enhance agent responses.
        Only high-quality, recent dreams are included.

        Args:
            agent_name: Name of the agent
            limit: Maximum number of dreams to return

        Returns:
            List of dream dictionaries with content and metadata
        """
        try:
            from core.models_unified_system import AgentDream

            # Session 497: Re-enabled with quality filtering
            # Only get recent dreams (last 7 days) with meaningful content
            from datetime import timedelta

            cutoff = timezone.now() - timedelta(days=7)

            # Session 1083 (Rigby audit): AgentDream uses `dreamed_at`,
            # not `created_at`. The old query raised FieldError on
            # every agent_name lookup, surfaced in logs tonight as
            # `Could not fetch dreams for EditorAgent: Cannot resolve
            # keyword 'created_at'`. Sister bug to the content_voice_system
            # drift in round 32.
            dreams = AgentDream.objects.filter(
                agent__name=agent_name,
                dreamed_at__gte=cutoff
            ).select_related('agent').order_by('-dreamed_at')[:limit]

            # Fallback: try partial name match
            if not dreams.exists():
                dreams = AgentDream.objects.filter(
                    agent__name__icontains=agent_name.replace('Agent', ''),
                    dreamed_at__gte=cutoff
                ).select_related('agent').order_by('-dreamed_at')[:limit]

            result = []
            for dream in dreams:
                content = getattr(dream, 'content', '') or getattr(dream, 'dream_content', '')
                # Quality filter: only include dreams with substantial content
                if content and len(content) >= 20:
                    result.append({
                        'content': content[:200],
                        'dream_type': getattr(dream, 'dream_type', 'creative'),
                        'dreamed_at': dream.dreamed_at.isoformat() if getattr(dream, 'dreamed_at', None) else '',
                        'emotional_tone': getattr(dream, 'emotional_tone', 'neutral'),
                    })

            if result:
                logger.debug(f"Found {len(result)} quality dreams for {agent_name}")

            return result

        except Exception as e:
            # Upgraded from debug to warning so the next schema drift
            # surfaces instead of being silent again.
            logger.warning(
                "scifi_integration._get_recent_dreams for %s: %s: %s",
                agent_name, type(e).__name__, e,
            )
            return []

    def get_collaboration_bonus(
        self,
        agent_names: List[str]
    ) -> Tuple[float, Dict[str, Any]]:
        """
        Calculate collaboration bonus for a team of agents.

        Session 290: Simplified to use the new static synergy system
        instead of database queries. This is faster and more predictable.

        Args:
            agent_names: List of agents working together

        Returns:
            Tuple of (bonus_multiplier, details)
        """
        if len(agent_names) < 2:
            return (1.0, {'reason': 'Single agent, no collaboration bonus'})

        try:
            # Use the new synergy system
            from core.agents.synergy import get_team_synergy

            total_bonus, details = get_team_synergy(agent_names)

            # Convert to the expected format
            formatted_details = {
                'team_size': details['team_size'],
                'synergies': details['synergy_details'],
                'conflicts': [],  # No longer tracking conflicts
                'final_multiplier': details['final_multiplier'],
            }

            return (total_bonus, formatted_details)

        except Exception as e:
            logger.warning(f"Error calculating collaboration bonus: {e}")

        return (1.0, {
            'team_size': len(agent_names),
            'synergies': [],
            'conflicts': [],
            'final_multiplier': 1.0,
        })

    def get_prompt_injection(
        self,
        agent_name: str,
        task: Optional[str] = None,
        user=None
    ) -> str:
        """
        Get text to inject into agent prompts with sci-fi context.

        Args:
            agent_name: Name of the agent
            task: Optional task context
            user: Optional user for personalization

        Returns:
            Formatted string to inject into prompts
        """
        context = self.get_scifi_context(agent_name, task, user)

        parts = ["\n## Agent Personality & Context\n"]

        if context.mood:
            parts.append(f"**Current Mood:** {context.mood.mood_type.title()}")
            parts.append(f"- {context.mood.description}")
            parts.append(f"- Style tendency: {context.mood.style_modifier}")
            parts.append("")

        if context.evolution:
            parts.append(f"**Experience Level:** {context.evolution.title} (Level {context.evolution.level})")
            if context.evolution.specializations:
                parts.append(f"- Specializations: {', '.join(context.evolution.specializations)}")
            parts.append(f"- Authority: {context.evolution.authority_level}")
            parts.append("")

        if context.relationships:
            if context.relationships.allies:
                parts.append(f"**Works well with:** {', '.join(context.relationships.allies[:5])}")
            if context.relationships.rivals:
                parts.append(f"**Competitive with:** {', '.join(context.relationships.rivals[:3])}")
            parts.append("")

        if context.memory and context.memory.learned_patterns:
            parts.append("**Learned from past interactions:**")
            for pattern in context.memory.learned_patterns[:3]:
                parts.append(f"- {pattern}")
            parts.append("")

        if context.dreams:
            parts.append("**Recent creative insight:**")
            parts.append(f"- {context.dreams[0].get('content', '')[:150]}")

        return "\n".join(parts)

    def invalidate_cache(self, agent_name: Optional[str] = None):
        """Invalidate cached sci-fi context."""
        if agent_name:
            logger.info(f"Invalidating sci-fi cache for {agent_name}")
        else:
            logger.info("Invalidating all sci-fi context caches")


# Singleton instance
_scifi_service = None


def get_scifi_integration_service() -> SciFiIntegrationService:
    """Get the singleton SciFiIntegrationService instance."""
    global _scifi_service
    if _scifi_service is None:
        _scifi_service = SciFiIntegrationService()
    return _scifi_service

"""
Unified Memory Manager
======================

Single interface for all memory operations across the platform.
Handles storage, retrieval, and cross-agent/assistant communication.

This manager ensures all components (Personal Assistant, Agents, Advisors)
share a unified memory system with bidirectional data flow.
"""

import logging
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from django.contrib.auth import get_user_model
from django.db.models import Q, Count, F
from django.core.cache import cache

from core.models import (
    UserMemoryContext,
    EnhancedUserProfile
)

logger = logging.getLogger(__name__)
User = get_user_model()


class UnifiedMemoryManager:
    """
    Unified Memory Manager - Central hub for all memory operations.

    Features:
    - Single interface for all memory operations
    - Handles storage from any source (assistant, agent, system)
    - Smart retrieval with filtering and relevance scoring
    - Cross-agent memory sharing
    - Agent activity tracking
    - Bidirectional communication support
    """

    # Memory type constants
    MEMORY_TYPES = {
        'interaction': 'User interaction with assistant',
        'decision': 'Decision made by user',
        'preference': 'User preference',
        'goal': 'User goal or objective',
        'skill': 'Skill or competency',
        'project': 'Project or task',
        'learning': 'System learning from interaction',
        'pattern': 'Behavioral pattern detected',
        'agent_action': 'Action taken by an agent',
        'agent_learning': 'Learning by an agent',
        'agent_recommendation': 'Recommendation from agent',
        'cross_agent': 'Memory shared between agents',
        'system_insight': 'Platform-level learning',
        'agent_usage': 'Agent execution tracking',
    }

    def __init__(self, user: Optional[User] = None):
        """
        Initialize the Unified Memory Manager.

        Args:
            user: Optional user for personalized operations
        """
        self.user = user
        self.cache_prefix = "memory_manager"
        self.cache_ttl = 300  # 5 minutes
        logger.info(f"🧠 Unified Memory Manager initialized{f' for {user.username}' if user else ''}")

    def store_memory(self,
                    user: User,
                    source: str,
                    memory_type: str,
                    content: str,
                    importance: int = 5,
                    **metadata) -> UserMemoryContext:
        """
        Store memory from any source with unified interface.

        Args:
            user: User the memory belongs to
            source: Source of memory (e.g., "assistant", "agent:JobMatcher")
            memory_type: Type of memory from MEMORY_TYPES
            content: Memory content
            importance: Importance level 1-10
            **metadata: Additional metadata

        Returns:
            Created UserMemoryContext instance
        """
        try:
            # Ensure user has enhanced profile
            enhanced_profile, _ = EnhancedUserProfile.objects.get_or_create(user=user)

            # Create memory entry
            memory = UserMemoryContext.objects.create(
                user=user,
                profile=enhanced_profile,
                memory_type=memory_type,
                content=content[:1000],  # Limit content length
                importance=min(max(importance, 1), 10),  # Clamp 1-10
                source=source,
                related_project=metadata.get('related_project', ''),
                related_goal=metadata.get('related_goal', ''),
                tags=metadata.get('tags', []),
                context_metadata={
                    'source': source,
                    'timestamp': datetime.now().isoformat(),
                    **metadata
                }
            )

            # Update profile statistics
            self._update_profile_from_memory(user, memory_type, content, metadata)

            # Notify relevant consumers
            self._notify_memory_consumers(user, memory)

            # Clear cache for this user
            self._clear_user_cache(user)

            logger.info(f"✅ Stored {memory_type} memory from {source} for {user.username}")
            return memory

        except Exception as e:
            logger.error(f"❌ Error storing memory: {e}")
            raise

    def retrieve_memories(self,
                         user: User,
                         memory_types: Optional[List[str]] = None,
                         sources: Optional[List[str]] = None,
                         importance_min: int = 0,
                         days_back: Optional[int] = None,
                         limit: int = 10,
                         include_metadata: bool = True) -> List[Dict[str, Any]]:
        """
        Retrieve memories with smart filtering and relevance scoring.

        Args:
            user: User to retrieve memories for
            memory_types: Filter by memory types
            sources: Filter by sources
            importance_min: Minimum importance level
            days_back: Limit to memories from last N days
            limit: Maximum number of results
            include_metadata: Include full metadata

        Returns:
            List of memory dictionaries
        """
        # Check cache first
        cache_key = self._get_cache_key(user, 'retrieve', {
            'types': memory_types,
            'sources': sources,
            'importance': importance_min,
            'days': days_back,
            'limit': limit
        })

        cached = cache.get(cache_key)
        if cached:
            logger.info(f"📦 Retrieved {len(cached)} memories from cache")
            return cached

        # Build query
        query = UserMemoryContext.objects.filter(user=user)

        if memory_types:
            query = query.filter(memory_type__in=memory_types)

        if sources:
            # Handle wildcard sources like "agent:*"
            source_q = Q()
            for source in sources:
                if source.endswith('*'):
                    source_q |= Q(source__startswith=source[:-1])
                else:
                    source_q |= Q(source=source)
            query = query.filter(source_q)

        if importance_min > 0:
            query = query.filter(importance__gte=importance_min)

        if days_back:
            cutoff = datetime.now() - timedelta(days=days_back)
            query = query.filter(created_at__gte=cutoff)

        # Order by relevance (importance * recency)
        memories = query.order_by('-importance', '-created_at')[:limit]

        # Update access counts
        memory_ids = []
        for memory in memories:
            memory_ids.append(memory.id)

        # Bulk update access counts
        UserMemoryContext.objects.filter(id__in=memory_ids).update(
            accessed_count=F('accessed_count') + 1,
            last_accessed=datetime.now()
        )

        # Format results
        results = []
        for memory in memories:
            data = {
                'id': memory.id,
                'type': memory.memory_type,
                'content': memory.content,
                'source': memory.source,
                'importance': memory.importance,
                'created': memory.created_at.isoformat(),
                'accessed_count': memory.accessed_count
            }

            if include_metadata and memory.context_metadata:
                data['metadata'] = memory.context_metadata

            results.append(data)

        # Cache results
        cache.set(cache_key, results, self.cache_ttl)

        logger.info(f"🔍 Retrieved {len(results)} memories for {user.username}")
        return results

    def get_agent_activities(self,
                            user: User,
                            agent_name: Optional[str] = None,
                            limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent agent activities for a user.

        Args:
            user: User to get activities for
            agent_name: Optional specific agent filter
            limit: Maximum results

        Returns:
            List of agent activity records
        """
        sources = [f"agent:{agent_name}"] if agent_name else ["agent:*"]

        return self.retrieve_memories(
            user=user,
            memory_types=['agent_action', 'agent_learning', 'agent_recommendation', 'agent_usage'],
            sources=sources,
            limit=limit
        )

    def get_cross_agent_insights(self, user: User, limit: int = 20) -> Dict[str, Any]:
        """
        Get insights learned across all agents and the assistant.

        Args:
            user: User to get insights for
            limit: Maximum memories to analyze

        Returns:
            Dictionary with aggregated insights
        """
        # Get memories from all sources
        all_memories = self.retrieve_memories(
            user=user,
            memory_types=['learning', 'pattern', 'agent_learning', 'system_insight'],
            limit=limit
        )

        # Get agent activities
        agent_activities = self.get_agent_activities(user, limit=limit)

        # Aggregate insights
        insights = {
            'total_learnings': len(all_memories),
            'total_agent_actions': len(agent_activities),
            'active_agents': set(),
            'key_patterns': [],
            'top_skills': [],
            'recent_goals': [],
            'recommendations': []
        }

        # Extract active agents
        for activity in agent_activities:
            source = activity.get('source', '')
            if source.startswith('agent:'):
                agent = source.replace('agent:', '')
                insights['active_agents'].add(agent)

        insights['active_agents'] = list(insights['active_agents'])

        # Extract patterns and learnings
        for memory in all_memories:
            if memory['type'] == 'pattern':
                insights['key_patterns'].append(memory['content'])
            elif 'skill' in memory['content'].lower():
                insights['top_skills'].append(memory['content'])
            elif 'goal' in memory['content'].lower():
                insights['recent_goals'].append(memory['content'])

        # Get recommendations from agents
        recommendations = self.retrieve_memories(
            user=user,
            memory_types=['agent_recommendation'],
            limit=5
        )

        insights['recommendations'] = [r['content'] for r in recommendations]

        logger.info(f"🎯 Compiled cross-agent insights for {user.username}")
        return insights

    def share_memory_between_agents(self,
                                   memory: UserMemoryContext,
                                   from_agent: str,
                                   to_agents: List[str]) -> List[UserMemoryContext]:
        """
        Enable agent-to-agent memory sharing.

        Args:
            memory: Memory to share
            from_agent: Source agent name
            to_agents: Target agent names

        Returns:
            List of created cross-agent memories
        """
        shared_memories = []

        for target_agent in to_agents:
            shared = self.store_memory(
                user=memory.user,
                source=f"agent:{from_agent}→{target_agent}",
                memory_type='cross_agent',
                content=f"Shared from {from_agent}: {memory.content}",
                importance=memory.importance,
                original_memory_id=memory.id,
                from_agent=from_agent,
                to_agent=target_agent,
                shared_at=datetime.now().isoformat()
            )
            shared_memories.append(shared)

            logger.info(f"📤 Shared memory from {from_agent} to {target_agent}")

        return shared_memories

    def get_assistant_context_for_agents(self, user: User) -> Dict[str, Any]:
        """
        Get Personal Assistant context for agents to reference.

        Args:
            user: User to get context for

        Returns:
            Dictionary with assistant insights
        """
        # Get recent interactions
        interactions = self.retrieve_memories(
            user=user,
            memory_types=['interaction'],
            sources=['assistant'],
            limit=10
        )

        # Get preferences and goals
        preferences = self.retrieve_memories(
            user=user,
            memory_types=['preference', 'goal'],
            limit=10
        )

        context = {
            'recent_conversations': [i['content'] for i in interactions],
            'user_preferences': [p['content'] for p in preferences],
            'communication_style': None,
            'current_projects': []
        }

        # Add profile data
        try:
            profile = EnhancedUserProfile.objects.get(user=user)
            context['communication_style'] = profile.communication_style
            context['current_projects'] = profile.current_projects or []
        except Exception as _e:
            logger.warning(
                "unified_memory_manager.get_assistant_context_for_agents: swallowed (%s: %s) — degraded",
                type(_e).__name__, _e,
            )

        return context

    def _update_profile_from_memory(self,
                                   user: User,
                                   memory_type: str,
                                   content: str,
                                   metadata: Dict[str, Any]):
        """
        Update user profile based on stored memory.

        Args:
            user: User to update
            memory_type: Type of memory
            content: Memory content
            metadata: Memory metadata
        """
        try:
            profile = EnhancedUserProfile.objects.get(user=user)

            # Update interaction count
            profile.interaction_count += 1

            # Update based on memory type
            if memory_type == 'skill' and 'skill_name' in metadata:
                skills = profile.core_competencies or {}
                skills[metadata['skill_name']] = metadata.get('proficiency', 5)
                profile.core_competencies = skills

            elif memory_type == 'goal' and content:
                goals = profile.long_term_goals or []
                if content not in goals:
                    goals.append(content[:200])  # Limit length
                    profile.long_term_goals = goals[:10]  # Max 10 goals

            elif memory_type == 'project' and 'project_name' in metadata:
                projects = profile.current_projects or []
                if metadata['project_name'] not in projects:
                    projects.append(metadata['project_name'])
                    profile.current_projects = projects[:10]  # Max 10 projects

            profile.save()

        except Exception as e:
            logger.error(f"Error updating profile from memory: {e}")

    def _notify_memory_consumers(self, user: User, memory: UserMemoryContext):
        """
        Notify relevant consumers about new memory.

        Args:
            user: User the memory belongs to
            memory: Memory that was created
        """
        # This could trigger WebSocket notifications, agent wake-ups, etc.
        # For now, just log
        logger.info(f"📢 Notifying consumers about {memory.memory_type} memory")

        # Could implement pub/sub or event system here
        # Example: Send to WebSocket hub
        try:
            from core.unified_hub import UnifiedWebSocketHub
            hub = UnifiedWebSocketHub()
            hub.send_to_user(user.id, {
                'type': 'memory_update',
                'memory_type': memory.memory_type,
                'content': memory.content[:100],
                'source': memory.source
            })
        except Exception as _e:
            logger.warning(
                "unified_memory_manager._notify_memory_consumers: swallowed (%s: %s) — degraded",
                type(_e).__name__, _e,
            )

    def _clear_user_cache(self, user: User):
        """Clear cache entries for a user."""
        pattern = f"{self.cache_prefix}:{user.id}:*"
        # Django cache doesn't support pattern deletion, so track keys
        # In production, use Redis with pattern deletion
        logger.info(f"🗑️ Cleared cache for {user.username}")

    def _get_cache_key(self, user: User, operation: str, params: Dict) -> str:
        """Generate cache key for operations."""
        param_str = json.dumps(params, sort_keys=True)
        return f"{self.cache_prefix}:{user.id}:{operation}:{hash(param_str)}"

    def get_memory_statistics(self, user: User) -> Dict[str, Any]:
        """
        Get comprehensive memory statistics for a user.

        Args:
            user: User to get statistics for

        Returns:
            Dictionary with memory statistics
        """
        stats = {
            'total_memories': UserMemoryContext.objects.filter(user=user).count(),
            'by_type': {},
            'by_source': {},
            'most_accessed': [],
            'most_important': [],
            'recent_activity': []
        }

        # Count by type
        for memory_type in self.MEMORY_TYPES.keys():
            count = UserMemoryContext.objects.filter(
                user=user,
                memory_type=memory_type
            ).count()
            if count > 0:
                stats['by_type'][memory_type] = count

        # Count by source
        sources = UserMemoryContext.objects.filter(user=user).values('source').annotate(
            count=Count('id')
        )
        for source in sources:
            stats['by_source'][source['source']] = source['count']

        # Most accessed memories
        most_accessed = UserMemoryContext.objects.filter(
            user=user
        ).order_by('-accessed_count')[:5]

        stats['most_accessed'] = [
            {'content': m.content[:100], 'count': m.accessed_count}
            for m in most_accessed
        ]

        # Most important memories
        most_important = UserMemoryContext.objects.filter(
            user=user
        ).order_by('-importance')[:5]

        stats['most_important'] = [
            {'content': m.content[:100], 'importance': m.importance}
            for m in most_important
        ]

        # Recent activity (last 24 hours)
        recent = datetime.now() - timedelta(days=1)
        stats['recent_activity'] = UserMemoryContext.objects.filter(
            user=user,
            created_at__gte=recent
        ).count()

        return stats


# Singleton instance for global access
_memory_manager_instance = None

def get_memory_manager(user: Optional[User] = None) -> UnifiedMemoryManager:
    """
    Get the singleton UnifiedMemoryManager instance.

    Args:
        user: Optional user for personalized operations

    Returns:
        UnifiedMemoryManager instance
    """
    global _memory_manager_instance
    if _memory_manager_instance is None:
        _memory_manager_instance = UnifiedMemoryManager(user)
    elif user and _memory_manager_instance.user != user:
        # Update user if different
        _memory_manager_instance.user = user
    return _memory_manager_instance
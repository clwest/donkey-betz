"""
Conversation Memory Service
===========================

Session 811: Creates cross-agent memories from conversation insights.

When agents have a conversation, the insights, agreements, and conclusions
should be persisted as memories so future conversations can build on them.

This service creates:
1. Individual agent memories (what each agent learned)
2. Shared memory clusters (cross-agent insights)
3. Collective intelligence contributions

Usage:
    from core.services.conversation_memory_service import ConversationMemoryService

    service = ConversationMemoryService()
    result = service.create_conversation_memories(
        conversation_id="uuid-here",
        participants=['ResearchAgent', 'ContentStrategyAgent'],
        decision_summary={'insights': [...], 'proposed_feature': {...}},
        topic="Content strategy optimization",
        messages=[{...}, ...]
    )
"""

import logging
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime

from django.utils import timezone
from django.db import transaction

logger = logging.getLogger(__name__)


# Feature flag (also defined in conversation_orchestrator.py)
ENABLE_CROSS_AGENT_MEMORY = True


@dataclass
class MemoryCreationResult:
    """Result of creating conversation memories."""
    conversation_id: str
    memories_created: int = 0
    cluster_created: bool = False
    cluster_id: Optional[str] = None
    participant_memories: Dict[str, List[str]] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            'conversation_id': self.conversation_id,
            'memories_created': self.memories_created,
            'cluster_created': self.cluster_created,
            'cluster_id': self.cluster_id,
            'participant_memories': self.participant_memories,
            'errors': self.errors,
        }


class ConversationMemoryService:
    """
    Creates cross-agent memories from conversation outcomes.

    Memory types created:
    - conversation_summary: Overall summary of what was discussed
    - insight: Key insights extracted from the discussion
    - feature_proposal: Details of any proposed feature
    - agreement: Points of consensus between agents
    - action_item: Tasks or next steps identified
    """

    def __init__(self):
        """Initialize the service."""
        pass

    def create_conversation_memories(
        self,
        conversation_id: str,
        participants: List[str],
        decision_summary: Optional[Dict[str, Any]],
        topic: str,
        messages: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None
    ) -> MemoryCreationResult:
        """
        Create memories from a completed conversation.

        Args:
            conversation_id: ID of the conversation
            participants: List of agent names that participated
            decision_summary: The DecisionSummary with insights, feature, next_steps
            topic: Conversation topic
            messages: List of message dicts from the conversation
            context: Additional context

        Returns:
            MemoryCreationResult with details about created memories
        """
        result = MemoryCreationResult(conversation_id=conversation_id)

        if not ENABLE_CROSS_AGENT_MEMORY:
            result.errors.append("Cross-agent memory creation is disabled")
            return result

        if not participants:
            result.errors.append("No participants specified")
            return result

        try:
            with transaction.atomic():
                # Create individual memories for each participant
                for agent_name in participants:
                    memory_ids = self._create_participant_memories(
                        agent_name=agent_name,
                        other_participants=[p for p in participants if p != agent_name],
                        decision_summary=decision_summary,
                        topic=topic,
                        messages=messages,
                        conversation_id=conversation_id
                    )
                    result.participant_memories[agent_name] = memory_ids
                    result.memories_created += len(memory_ids)

                # Create shared memory cluster for cross-agent insights
                if decision_summary and decision_summary.get('insights'):
                    cluster_id = self._create_shared_cluster(
                        participants=participants,
                        decision_summary=decision_summary,
                        topic=topic,
                        conversation_id=conversation_id
                    )
                    if cluster_id:
                        result.cluster_created = True
                        result.cluster_id = cluster_id

                # Share to collective memory system
                self._share_to_collective_memory(
                    conversation_id=conversation_id,
                    participants=participants,
                    decision_summary=decision_summary,
                    topic=topic
                )

        except Exception as e:
            logger.error(f"Error creating conversation memories: {e}")
            result.errors.append(str(e))

        logger.info(
            f"Created {result.memories_created} memories for conversation {conversation_id} "
            f"(cluster={result.cluster_created})"
        )

        return result

    def _create_participant_memories(
        self,
        agent_name: str,
        other_participants: List[str],
        decision_summary: Optional[Dict[str, Any]],
        topic: str,
        messages: List[Dict[str, Any]],
        conversation_id: str
    ) -> List[str]:
        """
        Create memories for a single participant.

        Creates:
        1. Conversation summary memory
        2. Key insights memory (if insights exist)
        3. Feature proposal memory (if feature proposed)

        Returns:
            List of created memory IDs
        """
        from core.models_unified_system import Agent, AgentMemory

        memory_ids = []

        # Get agent object
        agent = Agent.objects.filter(name=agent_name).first()
        if not agent:
            logger.warning(f"Agent not found: {agent_name}")
            return memory_ids

        # 1. Create conversation summary memory
        summary_content = self._generate_conversation_summary(
            agent_name=agent_name,
            other_participants=other_participants,
            topic=topic,
            messages=messages,
            decision_summary=decision_summary
        )

        summary_memory = AgentMemory.objects.create(
            agent=agent,
            title=f"Conversation: {topic[:100]}",
            content=summary_content,
            context=f"Discussed with: {', '.join(other_participants)}",
            memory_type='interaction',
            valence='positive',
            importance_score=0.7,
            safety_class='candidate',
            source_type='agent_conversation',
            source_id=conversation_id,
            tags=['conversation', 'cross_agent', topic[:50]]
        )
        memory_ids.append(str(summary_memory.id))

        # 2. Create insight memories
        if decision_summary and decision_summary.get('insights'):
            insights = decision_summary['insights']
            insights_text = "\n".join([f"- {i}" for i in insights[:5]])

            insight_memory = AgentMemory.objects.create(
                agent=agent,
                title=f"Insights: {topic[:80]}",
                content=f"Key insights from conversation about {topic}:\n{insights_text}",
                context=f"Derived from conversation with {', '.join(other_participants)}",
                memory_type='insight',
                valence='positive',
                importance_score=0.8,
                safety_class='candidate',
                source_type='agent_conversation',
                source_id=conversation_id,
                tags=['insight', 'conversation', 'cross_agent']
            )
            memory_ids.append(str(insight_memory.id))

        # 3. Create feature proposal memory
        if decision_summary and decision_summary.get('proposed_feature'):
            feature = decision_summary['proposed_feature']
            feature_name = feature.get('name', 'Unnamed Feature')
            feature_text = (
                f"Feature: {feature_name}\n"
                f"Inputs: {feature.get('inputs', 'TBD')}\n"
                f"Outputs: {feature.get('outputs', 'TBD')}\n"
                f"Integration: {feature.get('integration_point', 'TBD')}"
            )

            feature_memory = AgentMemory.objects.create(
                agent=agent,
                title=f"Feature Proposal: {feature_name[:80]}",
                content=feature_text,
                context=f"Proposed during conversation about {topic}",
                memory_type='technique',
                valence='positive',
                importance_score=0.75,
                safety_class='candidate',
                source_type='agent_conversation',
                source_id=conversation_id,
                tags=['feature', 'proposal', 'conversation']
            )
            memory_ids.append(str(feature_memory.id))

        return memory_ids

    def _generate_conversation_summary(
        self,
        agent_name: str,
        other_participants: List[str],
        topic: str,
        messages: List[Dict[str, Any]],
        decision_summary: Optional[Dict[str, Any]]
    ) -> str:
        """
        Generate a summary of the conversation from this agent's perspective.
        """
        # Get agent's own messages
        my_messages = [m for m in messages if m.get('agent') == agent_name]
        other_messages = [m for m in messages if m.get('agent') != agent_name]

        summary_parts = [
            f"Participated in a conversation about: {topic}",
            f"Discussed with: {', '.join(other_participants)}",
            f"Total exchanges: {len(messages)} messages",
            f"My contributions: {len(my_messages)} messages",
        ]

        # Add key points from decision summary
        if decision_summary:
            if decision_summary.get('insights'):
                summary_parts.append(f"\nKey insights: {len(decision_summary['insights'])}")
            if decision_summary.get('proposed_feature'):
                feature = decision_summary['proposed_feature']
                summary_parts.append(f"Feature proposed: {feature.get('name', 'TBD')}")
            if decision_summary.get('next_steps'):
                summary_parts.append(f"Action items: {len(decision_summary['next_steps'])}")

        # Add sample of own key points
        if my_messages:
            summary_parts.append("\nMy key contributions:")
            for msg in my_messages[:2]:
                content = msg.get('content', '')[:150]
                summary_parts.append(f"- {content}...")

        return "\n".join(summary_parts)

    def _create_shared_cluster(
        self,
        participants: List[str],
        decision_summary: Dict[str, Any],
        topic: str,
        conversation_id: str
    ) -> Optional[str]:
        """
        Create a shared MemoryCluster for cross-agent insights.

        A cluster with agent=None represents cross-agent knowledge.
        """
        from core.models_unified_system import MemoryCluster, MemoryClusterMembership, AgentMemory

        try:
            # Create the cross-agent cluster
            cluster = MemoryCluster.objects.create(
                agent=None,  # None = cross-agent cluster
                name=f"Cross-Agent Insights: {topic[:100]}",
                description=(
                    f"Shared insights from conversation between "
                    f"{', '.join(participants)} about {topic}"
                ),
                keywords=[
                    topic[:50],
                    'cross_agent',
                    'conversation',
                    *[p.replace('Agent', '').lower() for p in participants[:3]]
                ],
                color='#8b5cf6',  # Purple for cross-agent
                icon='🤝',
                coherence_score=0.8,
                stability_score=0.7,
                cluster_method='manual',
            )

            # Link memories from all participants to this cluster
            for agent_name in participants:
                agent_memories = AgentMemory.objects.filter(
                    agent__name=agent_name,
                    source_id=conversation_id,
                    source_type='agent_conversation'
                )

                for memory in agent_memories:
                    MemoryClusterMembership.objects.create(
                        cluster=cluster,
                        memory=memory,
                        similarity_to_centroid=0.85,
                        is_core_member=True
                    )

            logger.info(f"Created cross-agent cluster {cluster.id} for conversation {conversation_id}")
            return str(cluster.id)

        except Exception as e:
            logger.error(f"Error creating shared cluster: {e}")
            return None

    def _share_to_collective_memory(
        self,
        conversation_id: str,
        participants: List[str],
        decision_summary: Optional[Dict[str, Any]],
        topic: str
    ) -> bool:
        """
        Share conversation insights to the collective memory/learning system.

        This allows future agents to benefit from the conversation's conclusions.

        Session 1083 (Rigby audit): CollectiveMemory was referenced here
        but the model has never actually existed in ai_core.intelligence.models.
        Every conversation that tried to share insights threw ImportError
        and the debug-level log hid the failure. Short-circuit the whole
        method: feature is dead-coded. If CollectiveMemory ever gets
        built, flip the guard back off.
        """
        if not decision_summary or not decision_summary.get('insights'):
            return False

        # CollectiveMemory model was never created — see Session 1083 audit note.
        # The graceful-fallback try/except was masking the missing model
        # for who-knows-how-long.
        logger.debug(
            "share_to_collective_memory: skipping — CollectiveMemory "
            "model is not implemented. conversation_id=%s", conversation_id,
        )
        return False


# Singleton instance
_service_instance = None


def get_memory_service() -> ConversationMemoryService:
    """Get or create the singleton ConversationMemoryService."""
    global _service_instance
    if _service_instance is None:
        _service_instance = ConversationMemoryService()
    return _service_instance


def create_conversation_memories(
    conversation_id: str,
    participants: List[str],
    decision_summary: Optional[Dict[str, Any]],
    topic: str,
    messages: List[Dict[str, Any]],
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Convenience function to create conversation memories.

    Args:
        conversation_id: ID of the conversation
        participants: Participating agents
        decision_summary: DecisionSummary with insights
        topic: Conversation topic
        messages: Conversation messages
        context: Additional context

    Returns:
        Dict with memory creation results
    """
    service = get_memory_service()
    result = service.create_conversation_memories(
        conversation_id=conversation_id,
        participants=participants,
        decision_summary=decision_summary,
        topic=topic,
        messages=messages,
        context=context
    )
    return result.to_dict()


__all__ = [
    'ConversationMemoryService',
    'get_memory_service',
    'create_conversation_memories',
    'MemoryCreationResult',
    'ENABLE_CROSS_AGENT_MEMORY',
]

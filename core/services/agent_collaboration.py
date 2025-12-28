"""
Agent Collaboration Service
============================

Session 214: Comprehensive agent-to-agent collaboration system.

This service enables:
- Agent-to-agent communication protocol
- Collaborative workflow patterns
- Agent performance metrics and tracking
- Agent learning from each other (knowledge transfer)
- Multi-agent orchestration for complex tasks

The collaboration system allows agents to:
1. Request help from other agents with specialized capabilities
2. Share knowledge and insights
3. Delegate subtasks to more specialized agents
4. Learn from successful collaborations
5. Track performance metrics across collaborations
"""

import logging
import uuid
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from django.db.models import Q, Count, Avg
from django.utils import timezone
from django.core.cache import cache

logger = logging.getLogger(__name__)


# =============================================================================
# ENUMS AND DATA CLASSES
# =============================================================================

class CollaborationType(str, Enum):
    """Types of agent collaboration"""
    DELEGATION = 'delegation'  # Agent delegates subtask to another
    CONSULTATION = 'consultation'  # Agent asks for advice/input
    HANDOFF = 'handoff'  # Agent hands off entire task
    PARALLEL = 'parallel'  # Multiple agents work in parallel
    SEQUENTIAL = 'sequential'  # Agents work in sequence
    CONSENSUS = 'consensus'  # Multiple agents vote on decision


class MessageType(str, Enum):
    """Types of inter-agent messages"""
    REQUEST = 'request'
    RESPONSE = 'response'
    NOTIFICATION = 'notification'
    KNOWLEDGE_SHARE = 'knowledge_share'
    FEEDBACK = 'feedback'
    ERROR = 'error'


class CollaborationStatus(str, Enum):
    """Status of a collaboration"""
    PENDING = 'pending'
    ACTIVE = 'active'
    COMPLETED = 'completed'
    FAILED = 'failed'
    CANCELLED = 'cancelled'


@dataclass
class AgentMessage:
    """Message between agents"""
    id: str
    sender_agent: str
    receiver_agent: str
    message_type: MessageType
    content: Dict[str, Any]
    context: Dict[str, Any] = field(default_factory=dict)
    priority: int = 5  # 1-10, 10 is highest
    timestamp: datetime = field(default_factory=timezone.now)
    correlation_id: Optional[str] = None  # Links related messages
    response_to: Optional[str] = None  # ID of message this responds to

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'sender_agent': self.sender_agent,
            'receiver_agent': self.receiver_agent,
            'message_type': self.message_type.value,
            'content': self.content,
            'context': self.context,
            'priority': self.priority,
            'timestamp': self.timestamp.isoformat(),
            'correlation_id': self.correlation_id,
            'response_to': self.response_to
        }


@dataclass
class CollaborationRequest:
    """Request for agent collaboration"""
    id: str
    requester_agent: str
    target_agents: List[str]
    collaboration_type: CollaborationType
    task_description: str
    input_data: Dict[str, Any]
    expected_output: Dict[str, Any] = field(default_factory=dict)
    deadline: Optional[datetime] = None
    priority: int = 5
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CollaborationResult:
    """Result of a collaboration"""
    collaboration_id: str
    success: bool
    output_data: Dict[str, Any]
    participating_agents: List[str]
    execution_time_ms: float
    quality_score: float = 0.0
    knowledge_gained: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None


@dataclass
class AgentPerformanceMetrics:
    """Performance metrics for an agent"""
    agent_name: str
    total_executions: int = 0
    successful_executions: int = 0
    failed_executions: int = 0
    total_collaborations: int = 0
    collaboration_success_rate: float = 0.0
    avg_response_time_ms: float = 0.0
    knowledge_contributions: int = 0
    knowledge_consumed: int = 0
    delegation_count: int = 0
    consultation_count: int = 0
    specialization_scores: Dict[str, float] = field(default_factory=dict)
    last_active: Optional[datetime] = None


@dataclass
class KnowledgeTransfer:
    """Knowledge transfer between agents"""
    id: str
    source_agent: str
    target_agent: str
    knowledge_type: str  # 'technique', 'pattern', 'insight', 'skill'
    knowledge_content: Dict[str, Any]
    effectiveness_score: float = 0.0
    applied_count: int = 0
    created_at: datetime = field(default_factory=timezone.now)


# =============================================================================
# IMPORT MODELS
# =============================================================================

# Import from models_unified_system
from core.models_unified_system import (
    CollaborationSession,
    InterAgentMessage,
    SharedKnowledge,
    AgentPerformanceMetric,
)


# =============================================================================
# AGENT COLLABORATION SERVICE
# =============================================================================

class AgentCollaborationService:
    """
    Service for managing agent-to-agent collaboration.

    This service provides:
    - Message routing between agents
    - Collaboration orchestration
    - Performance tracking
    - Knowledge sharing and learning
    """

    def __init__(self, user=None):
        self.user = user
        self.logger = logging.getLogger(__name__)

    # =========================================================================
    # AGENT COMMUNICATION
    # =========================================================================

    def send_message(
        self,
        sender: str,
        receiver: str,
        message_type: MessageType,
        content: Dict[str, Any],
        context: Dict[str, Any] = None,
        priority: int = 5,
        correlation_id: str = None,
        response_to: str = None
    ) -> AgentMessage:
        """Send a message from one agent to another."""
        message_id = str(uuid.uuid4())

        # Create message record
        message = InterAgentMessage.objects.create(
            id=message_id,
            sender_agent=sender,
            receiver_agent=receiver,
            message_type=message_type.value,
            content=content,
            context=context or {},
            priority=priority,
            correlation_id=correlation_id,
            response_to=response_to
        )

        self.logger.info(
            f"📨 Message sent: {sender} -> {receiver} ({message_type.value})"
        )

        # Cache for quick retrieval
        cache_key = f"agent_messages_{receiver}"
        cached_messages = cache.get(cache_key, [])
        cached_messages.append(message_id)
        cache.set(cache_key, cached_messages[-100:], 300)  # Keep last 100

        return message

    def get_messages(
        self,
        agent_name: str,
        unread_only: bool = True,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get messages for an agent."""
        query = InterAgentMessage.objects.filter(receiver_agent=agent_name)

        if unread_only:
            query = query.filter(is_processed=False)

        messages = query.order_by('-priority', '-created_at')[:limit]

        return [
            {
                'id': str(m.id),
                'sender': m.sender_agent,
                'type': m.message_type,
                'content': m.content,
                'context': m.context,
                'priority': m.priority,
                'created_at': m.created_at.isoformat()
            }
            for m in messages
        ]

    def mark_message_processed(self, message_id: str) -> bool:
        """Mark a message as processed."""
        try:
            message = InterAgentMessage.objects.get(id=message_id)
            message.is_processed = True
            message.processed_at = timezone.now()
            message.save()
            return True
        except InterAgentMessage.DoesNotExist:
            return False

    # =========================================================================
    # COLLABORATION ORCHESTRATION
    # =========================================================================

    def request_collaboration(
        self,
        requester: str,
        target_agents: List[str],
        collaboration_type: CollaborationType,
        task_description: str,
        input_data: Dict[str, Any],
        context: Dict[str, Any] = None
    ) -> str:
        """Request a collaboration between agents."""
        collaboration_id = str(uuid.uuid4())

        # Create collaboration record
        collaboration = CollaborationSession.objects.create(
            id=collaboration_id,
            requester_agent=requester,
            collaboration_type=collaboration_type.value,
            task_description=task_description,
            input_data=input_data,
            participating_agents=target_agents,
            status=CollaborationStatus.PENDING.value,
            user=self.user
        )

        # Send collaboration request messages to target agents
        for agent in target_agents:
            self.send_message(
                sender=requester,
                receiver=agent,
                message_type=MessageType.REQUEST,
                content={
                    'collaboration_id': collaboration_id,
                    'collaboration_type': collaboration_type.value,
                    'task': task_description,
                    'input': input_data
                },
                context=context or {},
                correlation_id=collaboration_id
            )

        self.logger.info(
            f"🤝 Collaboration requested: {requester} -> {target_agents} "
            f"({collaboration_type.value})"
        )

        return collaboration_id

    def respond_to_collaboration(
        self,
        collaboration_id: str,
        agent_name: str,
        response_data: Dict[str, Any],
        success: bool = True
    ) -> bool:
        """Respond to a collaboration request."""
        try:
            collaboration = CollaborationSession.objects.get(id=collaboration_id)

            # Update output data with this agent's contribution
            output = collaboration.output_data or {}
            output[agent_name] = {
                'data': response_data,
                'success': success,
                'responded_at': timezone.now().isoformat()
            }
            collaboration.output_data = output

            # Check if all agents have responded
            all_responded = all(
                agent in output
                for agent in collaboration.participating_agents
            )

            if all_responded:
                collaboration.status = CollaborationStatus.COMPLETED.value
                collaboration.completed_at = timezone.now()
                collaboration.execution_time_ms = (
                    collaboration.completed_at - collaboration.started_at
                ).total_seconds() * 1000

                # Calculate quality score
                successful = sum(
                    1 for v in output.values() if v.get('success', False)
                )
                collaboration.quality_score = successful / len(output) * 100

                self.logger.info(
                    f"✅ Collaboration completed: {collaboration_id} "
                    f"(quality: {collaboration.quality_score}%)"
                )
            else:
                collaboration.status = CollaborationStatus.ACTIVE.value

            collaboration.save()

            # Send notification to requester
            self.send_message(
                sender=agent_name,
                receiver=collaboration.requester_agent,
                message_type=MessageType.RESPONSE,
                content={
                    'collaboration_id': collaboration_id,
                    'response': response_data,
                    'success': success,
                    'completed': all_responded
                },
                correlation_id=collaboration_id
            )

            return True

        except CollaborationSession.DoesNotExist:
            self.logger.error(f"Collaboration not found: {collaboration_id}")
            return False

    def get_collaboration_status(self, collaboration_id: str) -> Optional[Dict[str, Any]]:
        """Get the status of a collaboration."""
        try:
            collab = CollaborationSession.objects.get(id=collaboration_id)
            return {
                'id': str(collab.id),
                'requester': collab.requester_agent,
                'type': collab.collaboration_type,
                'status': collab.status,
                'participants': collab.participating_agents,
                'output': collab.output_data,
                'quality_score': collab.quality_score,
                'execution_time_ms': collab.execution_time_ms,
                'started_at': collab.started_at.isoformat(),
                'completed_at': collab.completed_at.isoformat() if collab.completed_at else None
            }
        except CollaborationSession.DoesNotExist:
            return None

    # =========================================================================
    # DELEGATION AND CONSULTATION PATTERNS
    # =========================================================================

    def delegate_task(
        self,
        delegator: str,
        delegate_to: str,
        task: str,
        input_data: Dict[str, Any],
        context: Dict[str, Any] = None
    ) -> str:
        """Delegate a task to another agent."""
        return self.request_collaboration(
            requester=delegator,
            target_agents=[delegate_to],
            collaboration_type=CollaborationType.DELEGATION,
            task_description=task,
            input_data=input_data,
            context=context
        )

    def request_consultation(
        self,
        requester: str,
        experts: List[str],
        question: str,
        context_data: Dict[str, Any] = None
    ) -> str:
        """Request consultation from expert agents."""
        return self.request_collaboration(
            requester=requester,
            target_agents=experts,
            collaboration_type=CollaborationType.CONSULTATION,
            task_description=question,
            input_data=context_data or {},
            context={'consultation_type': 'expert_opinion'}
        )

    def request_consensus(
        self,
        coordinator: str,
        voters: List[str],
        decision_topic: str,
        options: List[str],
        context: Dict[str, Any] = None
    ) -> str:
        """Request consensus decision from multiple agents."""
        return self.request_collaboration(
            requester=coordinator,
            target_agents=voters,
            collaboration_type=CollaborationType.CONSENSUS,
            task_description=decision_topic,
            input_data={'options': options},
            context=context
        )

    # =========================================================================
    # FIND COLLABORATORS
    # =========================================================================

    def find_best_collaborator(
        self,
        task_description: str,
        required_capabilities: List[str] = None,
        preferred_domain: str = None,
        exclude_agents: List[str] = None
    ) -> Optional[str]:
        """Find the best agent to collaborate with for a task."""
        from core.agents.registry import get_agent_registry

        registry = get_agent_registry()

        # Get candidate agents
        agents = registry.list_agents()

        if exclude_agents:
            agents = [a for a in agents if a['name'] not in exclude_agents]

        if not agents:
            return None

        # Score each agent
        scored_agents = []
        for agent in agents:
            score = self._score_collaborator(
                agent, task_description, required_capabilities, preferred_domain
            )
            if score > 0:
                scored_agents.append((agent['name'], score))

        if not scored_agents:
            return None

        # Return best match
        scored_agents.sort(key=lambda x: x[1], reverse=True)
        best_agent = scored_agents[0][0]

        self.logger.info(
            f"🔍 Best collaborator for '{task_description[:50]}...': {best_agent}"
        )

        return best_agent

    def _score_collaborator(
        self,
        agent: Dict[str, Any],
        task: str,
        capabilities: List[str] = None,
        domain: str = None
    ) -> float:
        """Score an agent as a potential collaborator."""
        score = 0.0

        # Capability match
        if capabilities:
            agent_caps = agent.get('capabilities', [])
            matching = set(capabilities) & set(agent_caps)
            score += len(matching) * 10.0

        # Domain match
        if domain and agent.get('specialization') == domain:
            score += 15.0

        # Keyword matching
        keywords = agent.get('routing_keywords', [])
        task_lower = task.lower()
        for keyword in keywords:
            if keyword.lower() in task_lower:
                score += 3.0

        # Performance bonus
        try:
            perf = AgentPerformanceMetric.objects.get(agent_name=agent['name'])
            if perf.total_collaborations > 0:
                success_rate = perf.successful_collaborations / perf.total_collaborations
                score += success_rate * 20.0
                score += min(perf.quality_score, 10.0)
        except AgentPerformanceMetric.DoesNotExist:
            pass

        return score

    # =========================================================================
    # KNOWLEDGE SHARING
    # =========================================================================

    def share_knowledge(
        self,
        source_agent: str,
        knowledge_type: str,
        title: str,
        description: str,
        content: Dict[str, Any],
        domain: str,
        tags: List[str] = None
    ) -> str:
        """Share knowledge from an agent to the knowledge base."""
        knowledge = SharedKnowledge.objects.create(
            source_agent=source_agent,
            knowledge_type=knowledge_type,
            title=title,
            description=description,
            knowledge_content=content,
            domain=domain,
            tags=tags or []
        )

        # Update agent's knowledge contribution count
        self._update_performance_metric(
            source_agent,
            'knowledge_contributions',
            increment=1
        )

        self.logger.info(
            f"📚 Knowledge shared by {source_agent}: {title} ({knowledge_type})"
        )

        return str(knowledge.id)

    def learn_knowledge(
        self,
        agent_name: str,
        knowledge_id: str
    ) -> Optional[Dict[str, Any]]:
        """Agent learns knowledge from the knowledge base."""
        try:
            knowledge = SharedKnowledge.objects.get(id=knowledge_id)

            # Add agent to learned list
            learned_by = knowledge.learned_by_agents or []
            if agent_name not in learned_by:
                learned_by.append(agent_name)
                knowledge.learned_by_agents = learned_by
                knowledge.applied_count += 1
                knowledge.save()

                # Update agent's knowledge consumed count
                self._update_performance_metric(
                    agent_name,
                    'knowledge_consumed',
                    increment=1
                )

                self.logger.info(
                    f"🎓 {agent_name} learned: {knowledge.title}"
                )

            return {
                'id': str(knowledge.id),
                'type': knowledge.knowledge_type,
                'title': knowledge.title,
                'description': knowledge.description,
                'content': knowledge.knowledge_content,
                'domain': knowledge.domain,
                'effectiveness': knowledge.effectiveness_score
            }

        except SharedKnowledge.DoesNotExist:
            return None

    def search_knowledge(
        self,
        query: str = None,
        domain: str = None,
        knowledge_type: str = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Search the knowledge base."""
        queryset = SharedKnowledge.objects.all()

        if domain:
            queryset = queryset.filter(domain=domain)

        if knowledge_type:
            queryset = queryset.filter(knowledge_type=knowledge_type)

        if query:
            queryset = queryset.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(tags__contains=[query])
            )

        knowledge_items = queryset.order_by(
            '-effectiveness_score', '-applied_count'
        )[:limit]

        return [
            {
                'id': str(k.id),
                'source': k.source_agent,
                'type': k.knowledge_type,
                'title': k.title,
                'description': k.description,
                'domain': k.domain,
                'tags': k.tags,
                'effectiveness': k.effectiveness_score,
                'applied_count': k.applied_count
            }
            for k in knowledge_items
        ]

    def rate_knowledge_effectiveness(
        self,
        knowledge_id: str,
        effectiveness: float,
        agent_name: str = None
    ) -> bool:
        """Rate the effectiveness of knowledge."""
        try:
            knowledge = SharedKnowledge.objects.get(id=knowledge_id)

            # Running average of effectiveness
            current = knowledge.effectiveness_score
            count = knowledge.applied_count or 1

            # Weighted average
            new_score = (current * (count - 1) + effectiveness) / count
            knowledge.effectiveness_score = new_score
            knowledge.save()

            self.logger.info(
                f"📊 Knowledge effectiveness updated: {knowledge.title} -> {new_score:.2f}"
            )

            return True

        except SharedKnowledge.DoesNotExist:
            return False

    # =========================================================================
    # PERFORMANCE TRACKING
    # =========================================================================

    def record_execution(
        self,
        agent_name: str,
        success: bool,
        execution_time_ms: float,
        domain: str = None,
        quality_score: float = None
    ):
        """Record an agent execution for performance tracking."""
        record, _ = AgentPerformanceMetric.objects.get_or_create(
            agent_name=agent_name
        )

        record.total_executions += 1
        if success:
            record.successful_executions += 1
        else:
            record.failed_executions += 1

        # Update average response time
        total = record.total_executions
        current_avg = record.avg_response_time_ms
        record.avg_response_time_ms = (current_avg * (total - 1) + execution_time_ms) / total

        # Update quality score if provided
        if quality_score is not None:
            current_quality = record.quality_score
            record.quality_score = (current_quality * (total - 1) + quality_score) / total

        # Update specialization scores
        if domain:
            scores = record.specialization_scores or {}
            domain_executions = scores.get(f"{domain}_count", 0) + 1
            domain_success = scores.get(f"{domain}_success", 0) + (1 if success else 0)
            scores[f"{domain}_count"] = domain_executions
            scores[f"{domain}_success"] = domain_success
            scores[domain] = domain_success / domain_executions
            record.specialization_scores = scores

        record.last_execution = timezone.now()
        record.save()

    def record_collaboration(
        self,
        agent_name: str,
        collaboration_type: CollaborationType,
        success: bool,
        role: str = 'participant'  # 'requester', 'participant', 'delegator', 'delegate'
    ):
        """Record a collaboration for an agent."""
        record, _ = AgentPerformanceMetric.objects.get_or_create(
            agent_name=agent_name
        )

        record.total_collaborations += 1
        if success:
            record.successful_collaborations += 1

        # Track by collaboration type
        if collaboration_type == CollaborationType.DELEGATION:
            if role == 'delegator':
                record.delegations_made += 1
            else:
                record.delegations_received += 1
        elif collaboration_type == CollaborationType.CONSULTATION:
            if role == 'requester':
                record.consultations_received += 1
            else:
                record.consultations_given += 1

        record.last_collaboration = timezone.now()
        record.save()

    def get_agent_performance(self, agent_name: str) -> Optional[AgentPerformanceMetrics]:
        """Get performance metrics for an agent."""
        try:
            record = AgentPerformanceMetric.objects.get(agent_name=agent_name)

            success_rate = (
                record.successful_collaborations / record.total_collaborations
                if record.total_collaborations > 0 else 0.0
            )

            return AgentPerformanceMetrics(
                agent_name=agent_name,
                total_executions=record.total_executions,
                successful_executions=record.successful_executions,
                failed_executions=record.failed_executions,
                total_collaborations=record.total_collaborations,
                collaboration_success_rate=success_rate,
                avg_response_time_ms=record.avg_response_time_ms,
                knowledge_contributions=record.knowledge_contributions,
                knowledge_consumed=record.knowledge_consumed,
                delegation_count=record.delegations_made + record.delegations_received,
                consultation_count=record.consultations_given + record.consultations_received,
                specialization_scores=record.specialization_scores,
                last_active=record.last_execution or record.last_collaboration
            )

        except AgentPerformanceMetric.DoesNotExist:
            return None

    def get_top_performers(
        self,
        domain: str = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get top performing agents."""
        queryset = AgentPerformanceMetric.objects.filter(
            total_executions__gt=0
        )

        if domain:
            queryset = queryset.filter(
                specialization_scores__has_key=domain
            ).order_by(f'-specialization_scores__{domain}')
        else:
            queryset = queryset.order_by('-quality_score', '-successful_executions')

        records = queryset[:limit]

        return [
            {
                'agent': r.agent_name,
                'total_executions': r.total_executions,
                'success_rate': r.successful_executions / r.total_executions if r.total_executions > 0 else 0,
                'quality_score': r.quality_score,
                'collaborations': r.total_collaborations,
                'knowledge_contributed': r.knowledge_contributions,
                'specialization_scores': r.specialization_scores
            }
            for r in records
        ]

    def _update_performance_metric(
        self,
        agent_name: str,
        metric: str,
        increment: int = 1
    ):
        """Update a specific performance metric."""
        record, _ = AgentPerformanceMetric.objects.get_or_create(
            agent_name=agent_name
        )

        current = getattr(record, metric, 0)
        setattr(record, metric, current + increment)
        record.save()

    # =========================================================================
    # COLLABORATION HISTORY AND ANALYTICS
    # =========================================================================

    def get_collaboration_history(
        self,
        agent_name: str = None,
        collaboration_type: str = None,
        status: str = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get collaboration history."""
        queryset = CollaborationSession.objects.all()

        if agent_name:
            queryset = queryset.filter(
                Q(requester_agent=agent_name) |
                Q(participating_agents__contains=[agent_name])
            )

        if collaboration_type:
            queryset = queryset.filter(collaboration_type=collaboration_type)

        if status:
            queryset = queryset.filter(status=status)

        if self.user:
            queryset = queryset.filter(user=self.user)

        collaborations = queryset.order_by('-started_at')[:limit]

        return [
            {
                'id': str(c.id),
                'requester': c.requester_agent,
                'type': c.collaboration_type,
                'task': c.task_description[:100],
                'participants': c.participating_agents,
                'status': c.status,
                'quality_score': c.quality_score,
                'execution_time_ms': c.execution_time_ms,
                'started_at': c.started_at.isoformat(),
                'completed_at': c.completed_at.isoformat() if c.completed_at else None
            }
            for c in collaborations
        ]

    def get_collaboration_stats(self) -> Dict[str, Any]:
        """Get overall collaboration statistics."""
        total = CollaborationSession.objects.count()
        completed = CollaborationSession.objects.filter(
            status=CollaborationStatus.COMPLETED.value
        ).count()

        avg_quality = CollaborationSession.objects.filter(
            status=CollaborationStatus.COMPLETED.value
        ).aggregate(avg=Avg('quality_score'))['avg'] or 0

        avg_time = CollaborationSession.objects.filter(
            status=CollaborationStatus.COMPLETED.value
        ).aggregate(avg=Avg('execution_time_ms'))['avg'] or 0

        by_type = CollaborationSession.objects.values(
            'collaboration_type'
        ).annotate(count=Count('id'))

        return {
            'total_collaborations': total,
            'completed': completed,
            'success_rate': completed / total if total > 0 else 0,
            'avg_quality_score': avg_quality,
            'avg_execution_time_ms': avg_time,
            'by_type': {item['collaboration_type']: item['count'] for item in by_type},
            'knowledge_items': SharedKnowledge.objects.count(),
            'agents_tracked': AgentPerformanceMetric.objects.count()
        }


# =============================================================================
# SERVICE FACTORY
# =============================================================================

def get_collaboration_service(user=None) -> AgentCollaborationService:
    """Get an instance of the collaboration service."""
    return AgentCollaborationService(user=user)

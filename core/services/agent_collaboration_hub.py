"""
Agent Collaboration Hub
=======================

Session 219 Phase B: Agent-to-Agent Communication System

This service enables the 14 AI Content agents to:
1. Send messages to each other (B1)
2. Follow collaboration protocols (B2)
3. Build consensus on decisions (B3)
4. Share knowledge and insights (B4)

The hub acts as a central message broker and knowledge repository
for all agent interactions.
"""

import logging
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from collections import defaultdict
import json
import redis

logger = logging.getLogger(__name__)


class MessageType(Enum):
    """Types of messages agents can exchange"""
    REQUEST = "request"           # Asking for help/info
    RESPONSE = "response"         # Replying to a request
    BROADCAST = "broadcast"       # Message to all agents
    KNOWLEDGE = "knowledge"       # Sharing learned information
    CONSENSUS = "consensus"       # Voting/agreement request
    HANDOFF = "handoff"          # Passing task to another agent
    NOTIFICATION = "notification" # General notification


class CollaborationProtocol(Enum):
    """Standard collaboration protocols between agents"""
    CONSULT = "consult"           # Ask for expert opinion
    DELEGATE = "delegate"         # Hand off task completely
    COLLABORATE = "collaborate"   # Work together on task
    REVIEW = "review"            # Request review of work
    ESCALATE = "escalate"        # Escalate to higher priority agent
    INFORM = "inform"            # Just share information


@dataclass
class AgentMessage:
    """A message between agents"""
    id: str
    sender: str
    recipient: str  # Can be agent name or "all" for broadcast
    message_type: MessageType
    protocol: CollaborationProtocol
    subject: str
    content: Dict[str, Any]
    priority: int = 5  # 1-10, higher = more important
    requires_response: bool = False
    parent_message_id: Optional[str] = None  # For threading
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'sender': self.sender,
            'recipient': self.recipient,
            'message_type': self.message_type.value,
            'protocol': self.protocol.value,
            'subject': self.subject,
            'content': self.content,
            'priority': self.priority,
            'requires_response': self.requires_response,
            'parent_message_id': self.parent_message_id,
            'created_at': self.created_at.isoformat()
        }


@dataclass
class ConsensusVote:
    """A vote in a consensus request"""
    agent_name: str
    vote: str  # "approve", "reject", "abstain"
    reasoning: str
    confidence: float  # 0-1
    voted_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class KnowledgeItem:
    """A piece of shared knowledge"""
    id: str
    source_agent: str
    category: str
    title: str
    content: Dict[str, Any]
    confidence: float
    tags: List[str]
    referenced_by: List[str] = field(default_factory=list)  # Agents who used this
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class AgentCollaborationHub:
    """
    Central hub for agent-to-agent communication and collaboration.

    Features:
    - Message routing between agents
    - Protocol-based collaboration
    - Consensus building
    - Knowledge sharing repository
    """

    def __init__(self, redis_config: Dict[str, Any] = None):
        self.redis_config = redis_config or {
            'host': 'localhost',
            'port': 6379,
            'db': 0
        }

        # Message queues per agent
        self.message_queues: Dict[str, List[AgentMessage]] = defaultdict(list)

        # Active consensus requests
        self.consensus_requests: Dict[str, Dict[str, Any]] = {}

        # Knowledge repository
        self.knowledge_base: Dict[str, KnowledgeItem] = {}
        self.knowledge_by_category: Dict[str, List[str]] = defaultdict(list)
        self.knowledge_by_agent: Dict[str, List[str]] = defaultdict(list)

        # Message handlers per agent
        self.message_handlers: Dict[str, Callable] = {}

        # Collaboration statistics
        self.stats = {
            'messages_sent': 0,
            'messages_by_type': defaultdict(int),
            'collaborations_initiated': 0,
            'consensus_reached': 0,
            'knowledge_items_shared': 0,
            'agent_interactions': defaultdict(lambda: defaultdict(int))
        }

        # Redis client for persistence
        self.redis_client = None
        self._connect_redis()

        # Message counter for IDs
        self._message_counter = 0

        logger.info("Agent Collaboration Hub initialized")

    def _connect_redis(self):
        """Connect to Redis for persistence"""
        try:
            self.redis_client = redis.Redis(**self.redis_config)
            self.redis_client.ping()
            logger.info("Collaboration Hub connected to Redis")
        except Exception as e:
            logger.warning(f"Redis connection failed, using in-memory only: {e}")
            self.redis_client = None

    def _generate_message_id(self) -> str:
        """Generate unique message ID"""
        self._message_counter += 1
        return f"msg_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}_{self._message_counter}"

    # =========================================================================
    # B1: Agent-to-Agent Messaging
    # =========================================================================

    def send_message(
        self,
        sender: str,
        recipient: str,
        message_type: MessageType,
        protocol: CollaborationProtocol,
        subject: str,
        content: Dict[str, Any],
        priority: int = 5,
        requires_response: bool = False,
        parent_message_id: Optional[str] = None
    ) -> AgentMessage:
        """
        Send a message from one agent to another.

        Args:
            sender: Name of sending agent
            recipient: Name of receiving agent (or "all" for broadcast)
            message_type: Type of message
            protocol: Collaboration protocol being used
            subject: Message subject
            content: Message content
            priority: 1-10 importance
            requires_response: Whether response is expected
            parent_message_id: ID of message this is responding to

        Returns:
            The sent message
        """
        message = AgentMessage(
            id=self._generate_message_id(),
            sender=sender,
            recipient=recipient,
            message_type=message_type,
            protocol=protocol,
            subject=subject,
            content=content,
            priority=priority,
            requires_response=requires_response,
            parent_message_id=parent_message_id
        )

        # Route message
        if recipient == "all":
            # Broadcast to all agents
            from core.services.ai_content_agents import AI_CONTENT_AGENTS
            for agent_name in AI_CONTENT_AGENTS.keys():
                if agent_name != sender:
                    self.message_queues[agent_name].append(message)
        else:
            self.message_queues[recipient].append(message)

        # Update stats
        self.stats['messages_sent'] += 1
        self.stats['messages_by_type'][message_type.value] += 1
        self.stats['agent_interactions'][sender][recipient] += 1

        # Persist to Redis
        if self.redis_client:
            try:
                self.redis_client.lpush(
                    f"agent:messages:{recipient}",
                    json.dumps(message.to_dict())
                )
                # Publish for real-time
                self.redis_client.publish(
                    f"agent:channel:{recipient}",
                    json.dumps(message.to_dict())
                )
            except Exception as e:
                logger.error(f"Failed to persist message to Redis: {e}")

        logger.debug(f"Message sent: {sender} -> {recipient} ({protocol.value})")

        # Trigger handler if registered
        if recipient in self.message_handlers:
            try:
                self.message_handlers[recipient](message)
            except Exception as e:
                logger.error(f"Message handler error for {recipient}: {e}")

        return message

    def get_messages(self, agent_name: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get messages for an agent"""
        messages = self.message_queues.get(agent_name, [])[-limit:]
        return [m.to_dict() for m in messages]

    def register_handler(self, agent_name: str, handler: Callable):
        """Register a message handler for an agent"""
        self.message_handlers[agent_name] = handler
        logger.info(f"Registered message handler for {agent_name}")

    # =========================================================================
    # B2: Collaboration Protocols
    # =========================================================================

    def initiate_collaboration(
        self,
        initiator: str,
        collaborators: List[str],
        protocol: CollaborationProtocol,
        task: Dict[str, Any]
    ) -> str:
        """
        Initiate a collaboration between agents.

        Args:
            initiator: Agent starting the collaboration
            collaborators: List of agents to collaborate with
            protocol: The collaboration protocol to use
            task: The task details

        Returns:
            Collaboration session ID
        """
        session_id = f"collab_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}_{self._message_counter}"
        self._message_counter += 1

        # Notify all collaborators
        for agent in collaborators:
            self.send_message(
                sender=initiator,
                recipient=agent,
                message_type=MessageType.REQUEST,
                protocol=protocol,
                subject=f"Collaboration Request: {task.get('title', 'Task')}",
                content={
                    'session_id': session_id,
                    'task': task,
                    'collaborators': collaborators,
                    'protocol': protocol.value
                },
                priority=7,
                requires_response=True
            )

        self.stats['collaborations_initiated'] += 1

        logger.info(f"Collaboration initiated: {initiator} with {collaborators} using {protocol.value}")

        return session_id

    def consult_expert(
        self,
        requester: str,
        expert: str,
        question: str,
        context: Dict[str, Any] = None
    ) -> AgentMessage:
        """
        Quick consultation with an expert agent.

        Args:
            requester: Agent asking
            expert: Agent being consulted
            question: The question
            context: Additional context

        Returns:
            The consultation request message
        """
        return self.send_message(
            sender=requester,
            recipient=expert,
            message_type=MessageType.REQUEST,
            protocol=CollaborationProtocol.CONSULT,
            subject=f"Consultation: {question[:50]}...",
            content={
                'question': question,
                'context': context or {}
            },
            priority=6,
            requires_response=True
        )

    def delegate_task(
        self,
        delegator: str,
        delegate: str,
        task: Dict[str, Any]
    ) -> AgentMessage:
        """
        Delegate a task to another agent.

        Args:
            delegator: Agent delegating
            delegate: Agent receiving delegation
            task: Task details

        Returns:
            The delegation message
        """
        return self.send_message(
            sender=delegator,
            recipient=delegate,
            message_type=MessageType.HANDOFF,
            protocol=CollaborationProtocol.DELEGATE,
            subject=f"Task Delegation: {task.get('title', 'Task')}",
            content={'task': task},
            priority=8,
            requires_response=True
        )

    # =========================================================================
    # B3: Consensus Mechanisms
    # =========================================================================

    def request_consensus(
        self,
        requester: str,
        voters: List[str],
        topic: str,
        options: List[str],
        context: Dict[str, Any] = None,
        threshold: float = 0.6
    ) -> str:
        """
        Request consensus from multiple agents.

        Args:
            requester: Agent requesting consensus
            voters: Agents who should vote
            topic: What to vote on
            options: Available options
            context: Additional context
            threshold: Approval threshold (0-1)

        Returns:
            Consensus request ID
        """
        consensus_id = f"cons_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}_{self._message_counter}"
        self._message_counter += 1

        self.consensus_requests[consensus_id] = {
            'requester': requester,
            'topic': topic,
            'options': options,
            'context': context or {},
            'threshold': threshold,
            'voters': voters,
            'votes': {},
            'status': 'pending',
            'created_at': datetime.now(timezone.utc).isoformat()
        }

        # Send vote requests
        for voter in voters:
            self.send_message(
                sender=requester,
                recipient=voter,
                message_type=MessageType.CONSENSUS,
                protocol=CollaborationProtocol.COLLABORATE,
                subject=f"Vote Request: {topic}",
                content={
                    'consensus_id': consensus_id,
                    'topic': topic,
                    'options': options,
                    'context': context or {}
                },
                priority=8,
                requires_response=True
            )

        logger.info(f"Consensus requested: {topic} from {len(voters)} agents")

        return consensus_id

    def submit_vote(
        self,
        consensus_id: str,
        agent_name: str,
        vote: str,
        reasoning: str = "",
        confidence: float = 0.8
    ) -> Dict[str, Any]:
        """
        Submit a vote in a consensus request.

        Args:
            consensus_id: The consensus request ID
            agent_name: Voting agent
            vote: The vote (one of the options)
            reasoning: Explanation for vote
            confidence: Confidence in vote (0-1)

        Returns:
            Updated consensus status
        """
        if consensus_id not in self.consensus_requests:
            return {'error': 'Consensus request not found'}

        consensus = self.consensus_requests[consensus_id]

        if agent_name not in consensus['voters']:
            return {'error': 'Agent not in voters list'}

        consensus['votes'][agent_name] = ConsensusVote(
            agent_name=agent_name,
            vote=vote,
            reasoning=reasoning,
            confidence=confidence
        )

        # Check if consensus is reached
        result = self._evaluate_consensus(consensus_id)

        return result

    def _evaluate_consensus(self, consensus_id: str) -> Dict[str, Any]:
        """Evaluate if consensus has been reached"""
        consensus = self.consensus_requests[consensus_id]
        votes = consensus['votes']
        voters = consensus['voters']
        threshold = consensus['threshold']

        # Count votes
        vote_counts = defaultdict(int)
        total_confidence = defaultdict(float)

        for vote_obj in votes.values():
            vote_counts[vote_obj.vote] += 1
            total_confidence[vote_obj.vote] += vote_obj.confidence

        # Check for quorum (at least 50% voted)
        quorum = len(votes) / len(voters) >= 0.5

        # Find winning option
        winning_option = None
        winning_count = 0
        for option, count in vote_counts.items():
            if count > winning_count:
                winning_count = count
                winning_option = option

        # Check if threshold met
        approval_rate = winning_count / len(voters) if voters else 0
        consensus_reached = quorum and approval_rate >= threshold

        if consensus_reached:
            consensus['status'] = 'reached'
            consensus['result'] = winning_option
            self.stats['consensus_reached'] += 1
            logger.info(f"Consensus reached on {consensus['topic']}: {winning_option}")
        elif len(votes) == len(voters):
            consensus['status'] = 'no_consensus'
            logger.info(f"No consensus reached on {consensus['topic']}")

        return {
            'consensus_id': consensus_id,
            'status': consensus['status'],
            'votes_received': len(votes),
            'total_voters': len(voters),
            'vote_counts': dict(vote_counts),
            'winning_option': winning_option,
            'approval_rate': approval_rate,
            'quorum_met': quorum,
            'consensus_reached': consensus_reached
        }

    def get_consensus_status(self, consensus_id: str) -> Dict[str, Any]:
        """Get current status of a consensus request"""
        if consensus_id not in self.consensus_requests:
            return {'error': 'Consensus request not found'}
        return self._evaluate_consensus(consensus_id)

    # =========================================================================
    # B4: Knowledge Sharing
    # =========================================================================

    def share_knowledge(
        self,
        agent_name: str,
        category: str,
        title: str,
        content: Dict[str, Any],
        confidence: float = 0.8,
        tags: List[str] = None
    ) -> str:
        """
        Share knowledge with other agents.

        Args:
            agent_name: Agent sharing the knowledge
            category: Knowledge category
            title: Title of knowledge item
            content: The knowledge content
            confidence: Confidence in this knowledge (0-1)
            tags: Tags for categorization

        Returns:
            Knowledge item ID
        """
        knowledge_id = f"know_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}_{self._message_counter}"
        self._message_counter += 1

        knowledge = KnowledgeItem(
            id=knowledge_id,
            source_agent=agent_name,
            category=category,
            title=title,
            content=content,
            confidence=confidence,
            tags=tags or []
        )

        self.knowledge_base[knowledge_id] = knowledge
        self.knowledge_by_category[category].append(knowledge_id)
        self.knowledge_by_agent[agent_name].append(knowledge_id)

        self.stats['knowledge_items_shared'] += 1

        # Broadcast to interested agents
        self.send_message(
            sender=agent_name,
            recipient="all",
            message_type=MessageType.KNOWLEDGE,
            protocol=CollaborationProtocol.INFORM,
            subject=f"New Knowledge: {title}",
            content={
                'knowledge_id': knowledge_id,
                'category': category,
                'title': title,
                'summary': str(content)[:200],
                'confidence': confidence,
                'tags': tags or []
            },
            priority=4
        )

        # Persist to Redis
        if self.redis_client:
            try:
                self.redis_client.hset(
                    'knowledge_base',
                    knowledge_id,
                    json.dumps({
                        'id': knowledge_id,
                        'source_agent': agent_name,
                        'category': category,
                        'title': title,
                        'content': content,
                        'confidence': confidence,
                        'tags': tags or [],
                        'created_at': knowledge.created_at.isoformat()
                    })
                )
            except Exception as e:
                logger.error(f"Failed to persist knowledge to Redis: {e}")

        logger.info(f"Knowledge shared by {agent_name}: {title} ({category})")

        return knowledge_id

    def query_knowledge(
        self,
        category: str = None,
        tags: List[str] = None,
        source_agent: str = None,
        min_confidence: float = 0.0,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Query the knowledge base.

        Args:
            category: Filter by category
            tags: Filter by tags
            source_agent: Filter by source agent
            min_confidence: Minimum confidence threshold
            limit: Maximum results

        Returns:
            List of matching knowledge items
        """
        results = []

        # Get candidate IDs
        if category:
            candidate_ids = set(self.knowledge_by_category.get(category, []))
        elif source_agent:
            candidate_ids = set(self.knowledge_by_agent.get(source_agent, []))
        else:
            candidate_ids = set(self.knowledge_base.keys())

        for knowledge_id in candidate_ids:
            knowledge = self.knowledge_base.get(knowledge_id)
            if not knowledge:
                continue

            # Apply filters
            if min_confidence and knowledge.confidence < min_confidence:
                continue

            if tags and not any(t in knowledge.tags for t in tags):
                continue

            if source_agent and knowledge.source_agent != source_agent:
                continue

            results.append({
                'id': knowledge.id,
                'source_agent': knowledge.source_agent,
                'category': knowledge.category,
                'title': knowledge.title,
                'content': knowledge.content,
                'confidence': knowledge.confidence,
                'tags': knowledge.tags,
                'referenced_by': knowledge.referenced_by,
                'created_at': knowledge.created_at.isoformat()
            })

        # Sort by confidence and recency
        results.sort(key=lambda x: (x['confidence'], x['created_at']), reverse=True)

        return results[:limit]

    def reference_knowledge(self, knowledge_id: str, agent_name: str):
        """Mark that an agent referenced a knowledge item"""
        if knowledge_id in self.knowledge_base:
            if agent_name not in self.knowledge_base[knowledge_id].referenced_by:
                self.knowledge_base[knowledge_id].referenced_by.append(agent_name)

    # =========================================================================
    # Statistics and Status
    # =========================================================================

    def get_stats(self) -> Dict[str, Any]:
        """Get collaboration hub statistics"""
        return {
            'messages_sent': self.stats['messages_sent'],
            'messages_by_type': dict(self.stats['messages_by_type']),
            'collaborations_initiated': self.stats['collaborations_initiated'],
            'consensus_reached': self.stats['consensus_reached'],
            'knowledge_items_shared': self.stats['knowledge_items_shared'],
            'active_consensus_requests': len([c for c in self.consensus_requests.values() if c['status'] == 'pending']),
            'knowledge_base_size': len(self.knowledge_base),
            'agents_with_messages': len(self.message_queues)
        }

    def get_agent_activity(self, agent_name: str) -> Dict[str, Any]:
        """Get activity summary for an agent"""
        messages_sent = sum(
            1 for q in self.message_queues.values()
            for m in q if m.sender == agent_name
        )
        messages_received = len(self.message_queues.get(agent_name, []))
        knowledge_shared = len(self.knowledge_by_agent.get(agent_name, []))

        return {
            'agent_name': agent_name,
            'messages_sent': messages_sent,
            'messages_received': messages_received,
            'knowledge_shared': knowledge_shared,
            'interactions': dict(self.stats['agent_interactions'].get(agent_name, {}))
        }


# Global hub instance
_collaboration_hub: Optional[AgentCollaborationHub] = None


def get_collaboration_hub() -> AgentCollaborationHub:
    """Get the global collaboration hub instance"""
    global _collaboration_hub
    if _collaboration_hub is None:
        _collaboration_hub = AgentCollaborationHub()
    return _collaboration_hub


# Convenience functions
def send_agent_message(
    sender: str,
    recipient: str,
    message_type: str,
    protocol: str,
    subject: str,
    content: Dict[str, Any],
    **kwargs
) -> Dict[str, Any]:
    """Send a message between agents"""
    hub = get_collaboration_hub()
    msg = hub.send_message(
        sender=sender,
        recipient=recipient,
        message_type=MessageType(message_type),
        protocol=CollaborationProtocol(protocol),
        subject=subject,
        content=content,
        **kwargs
    )
    return msg.to_dict()


def share_agent_knowledge(
    agent_name: str,
    category: str,
    title: str,
    content: Dict[str, Any],
    **kwargs
) -> str:
    """Share knowledge from an agent"""
    hub = get_collaboration_hub()
    return hub.share_knowledge(agent_name, category, title, content, **kwargs)


logger.info("Agent Collaboration Hub module loaded")

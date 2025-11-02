"""
Agent Collaboration Tracking System

This module provides comprehensive tracking and proof of agent teamwork,
including handoffs, parallel execution, consensus building, and measurable outcomes.
"""

import json
import uuid
import asyncio
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import redis
from django.db import models
from django.utils import timezone
import logging
from intelligence.shared_memory import SharedMemorySystem, AgentMemoryInterface

logger = logging.getLogger(__name__)


class CollaborationType(Enum):
    """Types of agent collaboration"""
    SEQUENTIAL_HANDOFF = "sequential_handoff"  # Agent A → Agent B → Agent C
    PARALLEL_EXECUTION = "parallel_execution"  # Multiple agents working simultaneously
    CONSENSUS_BUILDING = "consensus_building"  # Agents voting/agreeing on decisions
    HIERARCHICAL_DELEGATION = "hierarchical_delegation"  # Lead agent delegating to sub-agents
    PEER_REVIEW = "peer_review"  # Agents reviewing each other's work
    KNOWLEDGE_SHARING = "knowledge_sharing"  # Agents sharing information/context


@dataclass
class CollaborationEvent:
    """Single collaboration event between agents"""
    event_id: str
    timestamp: datetime
    event_type: str
    source_agent: str
    target_agents: List[str]
    context: Dict[str, Any]
    data_exchanged: Dict[str, Any]
    outcome: Optional[str] = None

    def to_dict(self):
        return {
            'event_id': self.event_id,
            'timestamp': self.timestamp.isoformat(),
            'event_type': self.event_type,
            'source_agent': self.source_agent,
            'target_agents': self.target_agents,
            'context': self.context,
            'data_exchanged': self.data_exchanged,
            'outcome': self.outcome
        }


@dataclass
class CollaborationChain:
    """Complete chain of agent collaboration for a task"""
    chain_id: str
    task_id: str
    started_at: datetime
    completed_at: Optional[datetime]
    initiator_agent: str
    participating_agents: List[str]
    events: List[CollaborationEvent]
    collaboration_type: CollaborationType
    success_metrics: Dict[str, Any]

    def get_collaboration_proof(self) -> Dict[str, Any]:
        """Generate proof of collaboration"""
        return {
            'chain_id': self.chain_id,
            'task_id': self.task_id,
            'duration_seconds': (self.completed_at - self.started_at).total_seconds() if self.completed_at else None,
            'agent_count': len(self.participating_agents),
            'event_count': len(self.events),
            'collaboration_type': self.collaboration_type.value,
            'handoff_sequence': self._get_handoff_sequence(),
            'parallel_executions': self._get_parallel_executions(),
            'consensus_achieved': self._check_consensus(),
            'data_flow_volume': self._calculate_data_flow(),
            'success_metrics': self.success_metrics
        }

    def _get_handoff_sequence(self) -> List[Dict[str, str]]:
        """Extract handoff sequence from events"""
        handoffs = []
        for event in self.events:
            if 'handoff' in event.event_type.lower():
                handoffs.append({
                    'from': event.source_agent,
                    'to': event.target_agents[0] if event.target_agents else None,
                    'timestamp': event.timestamp.isoformat(),
                    'data_passed': list(event.data_exchanged.keys())
                })
        return handoffs

    def _get_parallel_executions(self) -> List[Dict[str, Any]]:
        """Identify parallel agent executions"""
        parallel_groups = []
        current_group = []
        last_timestamp = None

        for event in sorted(self.events, key=lambda x: x.timestamp):
            if last_timestamp and (event.timestamp - last_timestamp).total_seconds() < 1:
                current_group.append(event.source_agent)
            else:
                if len(current_group) > 1:
                    parallel_groups.append({
                        'agents': list(set(current_group)),
                        'timestamp': last_timestamp.isoformat() if last_timestamp else None
                    })
                current_group = [event.source_agent]
            last_timestamp = event.timestamp

        return parallel_groups

    def _check_consensus(self) -> Optional[Dict[str, Any]]:
        """Check if consensus was achieved"""
        consensus_events = [e for e in self.events if 'consensus' in e.event_type.lower()]
        if consensus_events:
            votes = {}
            for event in consensus_events:
                if 'vote' in event.data_exchanged:
                    votes[event.source_agent] = event.data_exchanged['vote']

            if votes:
                majority_vote = max(set(votes.values()), key=list(votes.values()).count)
                return {
                    'achieved': True,
                    'votes': votes,
                    'decision': majority_vote,
                    'agreement_percentage': (list(votes.values()).count(majority_vote) / len(votes)) * 100
                }
        return None

    def _calculate_data_flow(self) -> Dict[str, int]:
        """Calculate data flow between agents"""
        total_messages = len(self.events)
        total_data_size = sum(
            len(json.dumps(e.data_exchanged)) for e in self.events
        )
        unique_connections = set()
        for event in self.events:
            for target in event.target_agents:
                unique_connections.add((event.source_agent, target))

        return {
            'total_messages': total_messages,
            'total_data_bytes': total_data_size,
            'unique_connections': len(unique_connections),
            'avg_message_size': total_data_size // total_messages if total_messages > 0 else 0
        }


class CollaborationTracker:
    """Main tracker for agent collaboration"""

    def __init__(self):
        self.redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)
        self.active_chains: Dict[str, CollaborationChain] = {}
        self.memory_system = SharedMemorySystem()  # Integrated shared memory

    def start_collaboration(
        self,
        task_id: str,
        initiator_agent: str,
        collaboration_type: CollaborationType,
        context: Dict[str, Any]
    ) -> str:
        """Start tracking a new collaboration chain"""
        chain_id = str(uuid.uuid4())

        chain = CollaborationChain(
            chain_id=chain_id,
            task_id=task_id,
            started_at=datetime.now(),
            completed_at=None,
            initiator_agent=initiator_agent,
            participating_agents=[initiator_agent],
            events=[],
            collaboration_type=collaboration_type,
            success_metrics={}
        )

        self.active_chains[chain_id] = chain

        # Store in Redis for persistence
        self.redis_client.hset(
            f"collaboration:chain:{chain_id}",
            mapping={
                'task_id': task_id,
                'started_at': chain.started_at.isoformat(),
                'initiator': initiator_agent,
                'type': collaboration_type.value,
                'context': json.dumps(context)
            }
        )

        logger.info(f"Started collaboration chain {chain_id} for task {task_id}")
        return chain_id

    def record_handoff(
        self,
        chain_id: str,
        source_agent: str,
        target_agent: str,
        data: Dict[str, Any],
        context: Dict[str, Any]
    ):
        """Record a handoff between agents"""
        if chain_id not in self.active_chains:
            return

        event = CollaborationEvent(
            event_id=str(uuid.uuid4()),
            timestamp=datetime.now(),
            event_type="handoff",
            source_agent=source_agent,
            target_agents=[target_agent],
            context=context,
            data_exchanged=data
        )

        chain = self.active_chains[chain_id]
        chain.events.append(event)

        if target_agent not in chain.participating_agents:
            chain.participating_agents.append(target_agent)

        # Store event in Redis
        self.redis_client.lpush(
            f"collaboration:events:{chain_id}",
            json.dumps(event.to_dict())
        )

        # Store in shared memory for cross-agent learning
        self.memory_system.store_memory(
            entity_type='agent',
            entity_id=source_agent,
            memory_type='handoff',
            content={
                'to': target_agent,
                'data': data,
                'context': context,
                'chain_id': chain_id
            }
        )

        # Share the handoff experience
        self.memory_system.share_experience(
            entity_type='agent',
            entity_id=source_agent,
            experience={
                'type': 'handoff',
                'target': target_agent,
                'data_size': len(json.dumps(data)),
                'success': True
            }
        )

        # Add knowledge edge between collaborating agents
        self.memory_system.add_knowledge_edge(
            from_entity=f"agent/{source_agent}",
            to_entity=f"agent/{target_agent}",
            relationship="handed_off_to",
            strength=0.8
        )

        # Broadcast via WebSocket
        self._broadcast_collaboration_update(chain_id, event)

    def record_parallel_execution(
        self,
        chain_id: str,
        agents: List[str],
        task_division: Dict[str, Any]
    ):
        """Record parallel execution by multiple agents"""
        if chain_id not in self.active_chains:
            return

        chain = self.active_chains[chain_id]

        for agent in agents:
            if agent not in chain.participating_agents:
                chain.participating_agents.append(agent)

            event = CollaborationEvent(
                event_id=str(uuid.uuid4()),
                timestamp=datetime.now(),
                event_type="parallel_execution",
                source_agent=agent,
                target_agents=[],
                context={'task_division': task_division},
                data_exchanged={'assigned_task': task_division.get(agent, {})}
            )

            chain.events.append(event)

            # Store in Redis
            self.redis_client.lpush(
                f"collaboration:events:{chain_id}",
                json.dumps(event.to_dict())
            )

    def record_consensus(
        self,
        chain_id: str,
        agents: List[str],
        votes: Dict[str, Any],
        final_decision: Any
    ):
        """Record consensus building between agents"""
        if chain_id not in self.active_chains:
            return

        chain = self.active_chains[chain_id]

        for agent, vote in votes.items():
            event = CollaborationEvent(
                event_id=str(uuid.uuid4()),
                timestamp=datetime.now(),
                event_type="consensus_vote",
                source_agent=agent,
                target_agents=list(agents),
                context={'decision_topic': 'task_approach'},
                data_exchanged={'vote': vote, 'reasoning': f"{agent}'s analysis"},
                outcome=str(final_decision)
            )

            chain.events.append(event)

            if agent not in chain.participating_agents:
                chain.participating_agents.append(agent)

        # Store consensus result
        self.redis_client.hset(
            f"collaboration:consensus:{chain_id}",
            mapping={
                'agents': json.dumps(agents),
                'votes': json.dumps(votes),
                'decision': str(final_decision),
                'timestamp': datetime.now().isoformat()
            }
        )

    def complete_collaboration(
        self,
        chain_id: str,
        success_metrics: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Complete a collaboration chain and generate proof"""
        if chain_id not in self.active_chains:
            return {}

        chain = self.active_chains[chain_id]
        chain.completed_at = datetime.now()
        chain.success_metrics = success_metrics

        # Generate comprehensive proof
        proof = chain.get_collaboration_proof()

        # Store completed chain
        self.redis_client.hset(
            f"collaboration:completed:{chain_id}",
            mapping={
                'proof': json.dumps(proof),
                'completed_at': chain.completed_at.isoformat(),
                'metrics': json.dumps(success_metrics)
            }
        )

        # Clean up active chain
        del self.active_chains[chain_id]

        logger.info(f"Completed collaboration chain {chain_id} with proof: {proof}")
        return proof

    def _broadcast_collaboration_update(self, chain_id: str, event: CollaborationEvent):
        """Broadcast collaboration updates via WebSocket"""
        try:
            update_data = {
                'type': 'collaboration_update',
                'chain_id': chain_id,
                'event': event.to_dict(),
                'timestamp': datetime.now().isoformat()
            }

            # Store in Redis for WebSocket consumers
            self.redis_client.publish(
                'collaboration:updates',
                json.dumps(update_data)
            )
        except Exception as e:
            logger.error(f"Failed to broadcast collaboration update: {e}")

    def get_collaboration_history(
        self,
        task_id: Optional[str] = None,
        agent: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get collaboration history with filters"""
        completed_keys = self.redis_client.keys("collaboration:completed:*")

        history = []
        for key in completed_keys[-limit:]:
            data = self.redis_client.hgetall(key)
            if data and 'proof' in data:
                proof = json.loads(data['proof'])

                # Apply filters
                if task_id and proof.get('task_id') != task_id:
                    continue
                if agent and agent not in proof.get('participating_agents', []):
                    continue

                history.append(proof)

        return history


# Django Model for persistent storage
class AgentCollaboration(models.Model):
    """Django model for agent collaboration records"""
    chain_id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    task_id = models.CharField(max_length=100)
    collaboration_type = models.CharField(max_length=50)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    initiator_agent = models.CharField(max_length=100)
    participating_agents = models.JSONField(default=list)
    events = models.JSONField(default=list)
    success_metrics = models.JSONField(default=dict)
    collaboration_proof = models.JSONField(default=dict)

    class Meta:
        ordering = ['-started_at']
        indexes = [
            models.Index(fields=['task_id']),
            models.Index(fields=['collaboration_type']),
            models.Index(fields=['started_at']),
        ]

    def __str__(self):
        return f"Collaboration {self.chain_id} ({self.collaboration_type})"
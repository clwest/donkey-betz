"""
Shared Memory System for Agents, Advisors, and Assistants
===========================================================

This module implements a unified shared memory system that allows all AI entities
(Agents, Advisors, Assistants) to share knowledge and learn from each other's experiences.

Key Features:
- Centralized memory storage using Redis
- Cross-entity learning capabilities
- Experience replay for continuous improvement
- Context sharing across all AI components
"""

import json
import logging
import os
from typing import Dict, List, Any, Optional
from datetime import timedelta
from django.utils import timezone
from celery import shared_task
import redis
from django.conf import settings

logger = logging.getLogger(__name__)

# Redis connection for persistent shared memory
# Use REDIS_URL (set by Railway) with fallback to localhost for local dev
_redis_url = getattr(settings, 'REDIS_URL', os.environ.get('REDIS_URL', 'redis://localhost:6379/2'))
try:
    redis_client = redis.from_url(_redis_url, db=2, decode_responses=True)
except Exception as _e:
    # Session 1103c: was a silent fallback to localhost. In production
    # if REDIS_URL parsing failed, the SharedMemorySystem would
    # silently connect to localhost (which doesn't exist on Railway)
    # and ALL shared memory ops would fail forever with no clue why.
    logger.error(
        "intelligence.shared_memory: redis.from_url(%r) failed "
        "(%s: %s) — falling back to localhost:6379. On Railway "
        "this will silently break SharedMemorySystem.",
        _redis_url, type(_e).__name__, _e,
    )
    redis_client = redis.Redis(host='localhost', port=6379, db=2, decode_responses=True)


class SharedMemorySystem:
    """
    Unified memory system for all AI entities to share knowledge and experiences.
    """

    def __init__(self):
        self.memory_prefix = "shared_memory:"
        self.experience_prefix = "experience:"
        self.context_prefix = "context:"
        self.learning_prefix = "learning:"

    # ===== MEMORY STORAGE =====

    def store_memory(self, entity_type: str, entity_id: str, memory_type: str, content: Any) -> bool:
        """
        Store a memory from any entity (agent, advisor, assistant).

        Args:
            entity_type: 'agent', 'advisor', or 'assistant'
            entity_id: Unique identifier for the entity
            memory_type: Type of memory (e.g., 'decision', 'observation', 'interaction')
            content: The memory content to store

        Returns:
            Success status
        """
        try:
            key = f"{self.memory_prefix}{entity_type}:{entity_id}:{memory_type}"
            timestamp = timezone.now().isoformat()

            memory_entry = {
                'entity_type': entity_type,
                'entity_id': entity_id,
                'memory_type': memory_type,
                'content': content,
                'timestamp': timestamp
            }

            # Store in Redis with TTL of 30 days
            redis_client.setex(
                key,
                timedelta(days=30),
                json.dumps(memory_entry)
            )

            # Also add to global memory stream for cross-entity learning
            self._add_to_global_stream(memory_entry)

            logger.info(f"✅ Stored memory for {entity_type}/{entity_id}: {memory_type}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to store memory: {e}")
            return False

    def retrieve_memory(self, entity_type: str, entity_id: str, memory_type: str) -> Optional[Dict]:
        """Retrieve specific memory for an entity."""
        try:
            key = f"{self.memory_prefix}{entity_type}:{entity_id}:{memory_type}"
            data = redis_client.get(key)

            if data:
                return json.loads(data)
            return None

        except Exception as e:
            logger.error(f"❌ Failed to retrieve memory: {e}")
            return None

    # ===== EXPERIENCE SHARING =====

    def share_experience(self, entity_type: str, entity_id: str, experience: Dict) -> bool:
        """
        Share an experience that other entities can learn from.

        Args:
            entity_type: Source entity type
            entity_id: Source entity ID
            experience: Dictionary containing experience details
        """
        try:
            experience_id = f"{entity_type}:{entity_id}:{timezone.now().timestamp()}"
            key = f"{self.experience_prefix}{experience_id}"

            experience_data = {
                'source_entity': f"{entity_type}/{entity_id}",
                'experience': experience,
                'timestamp': timezone.now().isoformat(),
                'learned_by': []  # Track which entities have learned from this
            }

            # Store experience
            redis_client.setex(
                key,
                timedelta(days=7),  # Experiences expire after 7 days
                json.dumps(experience_data)
            )

            # Notify all entities about new experience
            self._broadcast_experience(experience_id, experience_data)

            logger.info(f"📚 Shared experience from {entity_type}/{entity_id}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to share experience: {e}")
            return False

    def learn_from_experiences(self, entity_type: str, entity_id: str, limit: int = 10) -> List[Dict]:
        """
        Get relevant experiences for an entity to learn from.

        Args:
            entity_type: Learning entity type
            entity_id: Learning entity ID
            limit: Maximum number of experiences to retrieve

        Returns:
            List of relevant experiences
        """
        try:
            # Get all experience keys
            pattern = f"{self.experience_prefix}*"
            experience_keys = redis_client.keys(pattern)

            experiences = []
            for key in experience_keys[:limit * 2]:  # Get more than needed for filtering
                data = redis_client.get(key)
                if data:
                    experience = json.loads(data)

                    # Skip if this entity already learned from it
                    if f"{entity_type}/{entity_id}" not in experience.get('learned_by', []):
                        experiences.append(experience)

                        # Mark as learned
                        experience['learned_by'].append(f"{entity_type}/{entity_id}")
                        redis_client.setex(
                            key,
                            timedelta(days=7),
                            json.dumps(experience)
                        )

                        if len(experiences) >= limit:
                            break

            logger.info(f"🎓 {entity_type}/{entity_id} learned from {len(experiences)} experiences")
            return experiences

        except Exception as e:
            logger.error(f"❌ Failed to learn from experiences: {e}")
            return []

    # ===== CONTEXT SHARING =====

    def share_context(self, entity_type: str, entity_id: str, context: Dict) -> bool:
        """
        Share current context that other entities can use.

        Args:
            entity_type: Entity sharing context
            entity_id: Entity ID
            context: Current context dictionary
        """
        try:
            key = f"{self.context_prefix}{entity_type}:{entity_id}"

            context_data = {
                'entity': f"{entity_type}/{entity_id}",
                'context': context,
                'timestamp': timezone.now().isoformat()
            }

            # Store with short TTL (1 hour) as context is temporary
            redis_client.setex(
                key,
                timedelta(hours=1),
                json.dumps(context_data)
            )

            logger.info(f"🔄 Shared context from {entity_type}/{entity_id}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to share context: {e}")
            return False

    def get_global_context(self) -> Dict[str, Any]:
        """
        Get aggregated context from all active entities.

        Returns:
            Dictionary of all current contexts
        """
        try:
            pattern = f"{self.context_prefix}*"
            context_keys = redis_client.keys(pattern)

            global_context = {
                'agents': {},
                'advisors': {},
                'assistants': {},
                'timestamp': timezone.now().isoformat()
            }

            for key in context_keys:
                data = redis_client.get(key)
                if data:
                    context_data = json.loads(data)
                    entity_parts = context_data['entity'].split('/')
                    if len(entity_parts) == 2:
                        entity_type = entity_parts[0] + 's'  # Pluralize
                        entity_id = entity_parts[1]

                        if entity_type in global_context:
                            global_context[entity_type][entity_id] = context_data['context']

            return global_context

        except Exception as e:
            logger.error(f"❌ Failed to get global context: {e}")
            return {}

    # ===== COLLABORATIVE LEARNING =====

    def record_learning(self, entity_type: str, entity_id: str, learning: Dict) -> bool:
        """
        Record a learning insight that improved performance.

        Args:
            entity_type: Entity that learned
            entity_id: Entity ID
            learning: Learning details (what was learned, impact, etc.)
        """
        try:
            learning_id = f"{timezone.now().timestamp()}"
            key = f"{self.learning_prefix}{learning_id}"

            learning_data = {
                'entity': f"{entity_type}/{entity_id}",
                'learning': learning,
                'timestamp': timezone.now().isoformat(),
                'applied_by': [f"{entity_type}/{entity_id}"]  # Track who has applied this
            }

            # Store learning permanently
            redis_client.set(key, json.dumps(learning_data))

            # Add to learning index
            redis_client.zadd(
                f"{self.learning_prefix}index",
                {learning_id: timezone.now().timestamp()}
            )

            logger.info(f"💡 Recorded learning from {entity_type}/{entity_id}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to record learning: {e}")
            return False

    def get_collective_learnings(self, limit: int = 20) -> List[Dict]:
        """
        Get the most recent collective learnings from all entities.

        Args:
            limit: Maximum number of learnings to retrieve

        Returns:
            List of learning insights
        """
        try:
            # Get recent learning IDs from index
            learning_ids = redis_client.zrevrange(
                f"{self.learning_prefix}index",
                0,
                limit - 1
            )

            learnings = []
            for learning_id in learning_ids:
                key = f"{self.learning_prefix}{learning_id}"
                data = redis_client.get(key)
                if data:
                    learnings.append(json.loads(data))

            return learnings

        except Exception as e:
            logger.error(f"❌ Failed to get collective learnings: {e}")
            return []

    # ===== KNOWLEDGE GRAPH =====

    def add_knowledge_edge(self, from_entity: str, to_entity: str, relationship: str, strength: float = 1.0):
        """
        Add a knowledge relationship between entities.

        Args:
            from_entity: Source entity (e.g., 'agent/orchestrator')
            to_entity: Target entity (e.g., 'advisor/warren_buffett')
            relationship: Type of relationship (e.g., 'consults', 'collaborates')
            strength: Strength of the relationship (0.0 to 1.0)
        """
        try:
            edge_key = f"knowledge_edge:{from_entity}:{to_entity}"

            edge_data = {
                'from': from_entity,
                'to': to_entity,
                'relationship': relationship,
                'strength': strength,
                'created': timezone.now().isoformat(),
                'interactions': 1
            }

            # Check if edge exists and update interaction count
            existing = redis_client.get(edge_key)
            if existing:
                existing_data = json.loads(existing)
                edge_data['interactions'] = existing_data.get('interactions', 0) + 1
                edge_data['strength'] = min(1.0, strength + 0.1)  # Strengthen over time

            redis_client.set(edge_key, json.dumps(edge_data))

            logger.info(f"🔗 Added knowledge edge: {from_entity} --{relationship}--> {to_entity}")

        except Exception as e:
            logger.error(f"❌ Failed to add knowledge edge: {e}")

    def get_entity_network(self, entity: str) -> Dict[str, List[Dict]]:
        """
        Get all entities connected to a specific entity.

        Args:
            entity: Entity to get network for

        Returns:
            Dictionary with incoming and outgoing connections
        """
        try:
            # Get outgoing connections
            outgoing_pattern = f"knowledge_edge:{entity}:*"
            outgoing_keys = redis_client.keys(outgoing_pattern)

            # Get incoming connections
            incoming_pattern = f"knowledge_edge:*:{entity}"
            incoming_keys = redis_client.keys(incoming_pattern)

            network = {
                'outgoing': [],
                'incoming': []
            }

            for key in outgoing_keys:
                data = redis_client.get(key)
                if data:
                    network['outgoing'].append(json.loads(data))

            for key in incoming_keys:
                data = redis_client.get(key)
                if data:
                    network['incoming'].append(json.loads(data))

            return network

        except Exception as e:
            logger.error(f"❌ Failed to get entity network: {e}")
            return {'outgoing': [], 'incoming': []}

    # ===== PRIVATE METHODS =====

    def _add_to_global_stream(self, memory_entry: Dict):
        """Add memory to global stream for cross-entity access."""
        try:
            stream_key = f"{self.memory_prefix}global_stream"
            redis_client.xadd(
                stream_key,
                memory_entry,
                maxlen=10000  # Keep last 10,000 entries
            )
        except Exception as e:
            logger.error(f"Failed to add to global stream: {e}")

    def _broadcast_experience(self, experience_id: str, experience_data: Dict):
        """Broadcast new experience to all active entities."""
        try:
            # Use Redis pub/sub for real-time notifications
            channel = "shared_memory:new_experience"
            message = json.dumps({
                'experience_id': experience_id,
                'source': experience_data['source_entity'],
                'timestamp': experience_data['timestamp']
            })
            redis_client.publish(channel, message)
        except Exception as e:
            logger.error(f"Failed to broadcast experience: {e}")


# ===== ENTITY INTERFACES =====

class AgentMemoryInterface:
    """Interface for agents to interact with shared memory."""

    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.entity_type = 'agent'
        self.memory = SharedMemorySystem()

    def remember(self, memory_type: str, content: Any) -> bool:
        """Store a memory."""
        return self.memory.store_memory(self.entity_type, self.agent_id, memory_type, content)

    def recall(self, memory_type: str) -> Optional[Dict]:
        """Recall a specific memory."""
        return self.memory.retrieve_memory(self.entity_type, self.agent_id, memory_type)

    def share_learning(self, learning: Dict) -> bool:
        """Share a learning with other entities."""
        return self.memory.record_learning(self.entity_type, self.agent_id, learning)

    def learn_from_others(self, limit: int = 5) -> List[Dict]:
        """Learn from other entities' experiences."""
        return self.memory.learn_from_experiences(self.entity_type, self.agent_id, limit)


class AdvisorMemoryInterface:
    """Interface for advisors to interact with shared memory."""

    def __init__(self, advisor_id: str):
        self.advisor_id = advisor_id
        self.entity_type = 'advisor'
        self.memory = SharedMemorySystem()

    def provide_wisdom(self, wisdom: Dict) -> bool:
        """Share wisdom with the network."""
        return self.memory.share_experience(self.entity_type, self.advisor_id, wisdom)

    def get_agent_contexts(self) -> Dict:
        """Get contexts from all agents for better advice."""
        return self.memory.get_global_context().get('agents', {})

    def record_consultation(self, agent_id: str, advice_given: Dict) -> bool:
        """Record a consultation with an agent."""
        self.memory.add_knowledge_edge(
            f"agent/{agent_id}",
            f"advisor/{self.advisor_id}",
            "consulted",
            strength=0.8
        )
        return self.memory.store_memory(
            self.entity_type,
            self.advisor_id,
            'consultation',
            {'agent': agent_id, 'advice': advice_given}
        )


class AssistantMemoryInterface:
    """Interface for assistants to interact with shared memory."""

    def __init__(self, assistant_id: str = 'personal_assistant'):
        self.assistant_id = assistant_id
        self.entity_type = 'assistant'
        self.memory = SharedMemorySystem()

    def remember_user_preference(self, user_id: str, preference: Dict) -> bool:
        """Remember user preferences."""
        return self.memory.store_memory(
            self.entity_type,
            self.assistant_id,
            f'user_preference:{user_id}',
            preference
        )

    def get_user_context(self, user_id: str) -> Optional[Dict]:
        """Get stored user context."""
        return self.memory.retrieve_memory(
            self.entity_type,
            self.assistant_id,
            f'user_preference:{user_id}'
        )

    def learn_from_all(self) -> Dict:
        """Learn from all entities to better assist users."""
        return {
            'agent_learnings': self.memory.get_collective_learnings(10),
            'global_context': self.memory.get_global_context()
        }


# ===== CELERY TASKS =====

@shared_task
def sync_all_entity_memories():
    """
    Periodic task to sync memories across all entities.
    Runs every 10 minutes via Celery Beat.
    """
    try:
        memory_system = SharedMemorySystem()

        # Get global context
        global_context = memory_system.get_global_context()

        # Count active entities
        active_agents = len(global_context.get('agents', {}))
        active_advisors = len(global_context.get('advisors', {}))
        active_assistants = len(global_context.get('assistants', {}))

        logger.info(
            f"🔄 Memory sync complete: "
            f"{active_agents} agents, {active_advisors} advisors, {active_assistants} assistants"
        )

        return {
            'success': True,
            'active_entities': {
                'agents': active_agents,
                'advisors': active_advisors,
                'assistants': active_assistants
            }
        }

    except Exception as e:
        logger.error(f"❌ Memory sync failed: {e}")
        return {'success': False, 'error': str(e)}


# ===== SINGLETON INSTANCE =====

# Global shared memory instance
shared_memory = SharedMemorySystem()

# Export interfaces
__all__ = [
    'SharedMemorySystem',
    'AgentMemoryInterface',
    'AdvisorMemoryInterface',
    'AssistantMemoryInterface',
    'shared_memory',
    'sync_all_entity_memories'
]
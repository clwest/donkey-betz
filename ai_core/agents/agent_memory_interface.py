"""
Agent Memory Interface for Session 90 Agents
Provides Redis-based state management for all agents
"""
import redis
import json
import logging
import uuid
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class AgentMemoryInterface:
    """
    Redis-based memory interface for agents

    Session 90: All agents use Redis db=3 for state management
    Key pattern: {agent_name}:user_{user_id}:{resource_type}:{id}
    """

    def __init__(self, agent_name: str, user_id: int, agent_id: Optional[str] = None, redis_db: int = 3):
        """
        Initialize agent memory interface

        Args:
            agent_name: Name of agent (e.g., 'creative_director', 'template_manager')
            user_id: User ID for isolation
            agent_id: Optional agent session ID (defaults to UUID)
            redis_db: Redis database number (default: 3)
        """
        self.agent_name = agent_name
        self.user_id = user_id
        self.agent_id = agent_id or str(uuid.uuid4())

        # Connect to Redis
        self.redis = redis.Redis(
            host='localhost',
            port=6379,
            db=redis_db,
            decode_responses=True
        )

        logger.info(f"✅ {agent_name} agent memory initialized (user={user_id}, db={redis_db})")

    def _make_key(self, resource_type: str, resource_id: str = None) -> str:
        """Generate Redis key with consistent pattern"""
        if resource_id:
            return f"{self.agent_name}:user_{self.user_id}:{resource_type}:{resource_id}"
        return f"{self.agent_name}:user_{self.user_id}:{resource_type}"

    def set(self, resource_type: str, resource_id: str, data: Dict[str, Any], ttl: Optional[int] = None) -> bool:
        """
        Store data in Redis

        Args:
            resource_type: Type of resource (e.g., 'templates', 'batches')
            resource_id: Unique ID for this resource
            data: Dictionary to store
            ttl: Optional time-to-live in seconds

        Returns:
            bool: Success status
        """
        try:
            key = self._make_key(resource_type, resource_id)
            json_data = json.dumps(data)

            if ttl:
                self.redis.setex(key, ttl, json_data)
            else:
                self.redis.set(key, json_data)

            return True
        except Exception as e:
            logger.error(f"❌ Error setting {resource_type}:{resource_id}: {e}")
            return False

    def get(self, resource_type: str, resource_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve data from Redis

        Args:
            resource_type: Type of resource
            resource_id: Unique ID

        Returns:
            dict or None if not found
        """
        try:
            key = self._make_key(resource_type, resource_id)
            data = self.redis.get(key)

            if data:
                return json.loads(data)
            return None
        except Exception as e:
            logger.error(f"❌ Error getting {resource_type}:{resource_id}: {e}")
            return None

    def delete(self, resource_type: str, resource_id: str) -> bool:
        """Delete data from Redis"""
        try:
            key = self._make_key(resource_type, resource_id)
            self.redis.delete(key)
            return True
        except Exception as e:
            logger.error(f"❌ Error deleting {resource_type}:{resource_id}: {e}")
            return False

    def list_ids(self, resource_type: str) -> List[str]:
        """
        List all resource IDs of a given type for this user

        Args:
            resource_type: Type of resource

        Returns:
            List of resource IDs
        """
        try:
            pattern = self._make_key(resource_type, "*")
            keys = self.redis.keys(pattern)

            # Extract IDs from keys
            ids = []
            for key in keys:
                # Key format: agent_name:user_X:resource_type:ID
                parts = key.split(':')
                if len(parts) >= 4:
                    ids.append(parts[3])

            return ids
        except Exception as e:
            logger.error(f"❌ Error listing {resource_type}: {e}")
            return []

    def add_to_set(self, set_name: str, value: str) -> bool:
        """Add value to a Redis set"""
        try:
            key = self._make_key('sets', set_name)
            self.redis.sadd(key, value)
            return True
        except Exception as e:
            logger.error(f"❌ Error adding to set {set_name}: {e}")
            return False

    def get_set(self, set_name: str) -> List[str]:
        """Get all values in a Redis set"""
        try:
            key = self._make_key('sets', set_name)
            return list(self.redis.smembers(key))
        except Exception as e:
            logger.error(f"❌ Error getting set {set_name}: {e}")
            return []

    def remove_from_set(self, set_name: str, value: str) -> bool:
        """Remove value from Redis set"""
        try:
            key = self._make_key('sets', set_name)
            self.redis.srem(key, value)
            return True
        except Exception as e:
            logger.error(f"❌ Error removing from set {set_name}: {e}")
            return False

    def increment(self, counter_name: str) -> int:
        """Increment a counter"""
        try:
            key = self._make_key('counters', counter_name)
            return self.redis.incr(key)
        except Exception as e:
            logger.error(f"❌ Error incrementing {counter_name}: {e}")
            return 0

    def get_counter(self, counter_name: str) -> int:
        """Get counter value"""
        try:
            key = self._make_key('counters', counter_name)
            value = self.redis.get(key)
            return int(value) if value else 0
        except Exception as e:
            logger.error(f"❌ Error getting counter {counter_name}: {e}")
            return 0

    def clear_all(self) -> bool:
        """Clear all data for this agent/user (use with caution!)"""
        try:
            pattern = f"{self.agent_name}:user_{self.user_id}:*"
            keys = self.redis.keys(pattern)

            if keys:
                self.redis.delete(*keys)
                logger.info(f"🧹 Cleared {len(keys)} keys for {self.agent_name}")

            return True
        except Exception as e:
            logger.error(f"❌ Error clearing agent data: {e}")
            return False

    def log_agent_action(self, action: str, details: Dict[str, Any] = None):
        """
        Log agent action (stub - logging not implemented yet).

        Args:
            action: Action name
            details: Action details dictionary
        """
        # TODO: Implement proper action logging

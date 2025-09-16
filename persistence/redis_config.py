"""
Redis configuration and persistence setup for the Data Persistence system.

Provides:
- Persistent Redis configuration for agent memory
- Agent collaboration channels and pub/sub
- Cached data persistence and recovery
- Distributed locking for concurrent operations
"""

import json
import logging
import redis
import pickle
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

from django.conf import settings
from django.core.cache import cache
from django.utils import timezone

logger = logging.getLogger(__name__)


class RedisPersistenceManager:
    """
    Manager for Redis-based data persistence and caching.
    """

    def __init__(self):
        self.redis_url = getattr(settings, 'REDIS_URL', 'redis://localhost:6379/1')
        self.redis_client = redis.from_url(self.redis_url, decode_responses=True)
        self.binary_client = redis.from_url(self.redis_url, decode_responses=False)

        # Test connection
        try:
            self.redis_client.ping()
            logger.info("✅ Redis connection established for persistence")
        except redis.ConnectionError as e:
            logger.error(f"❌ Redis connection failed: {e}")
            raise

        # Configure persistence
        self._configure_persistence()

    def _configure_persistence(self):
        """Configure Redis for data persistence."""
        try:
            # Enable RDB snapshots (save every 15 minutes if at least 1 change)
            # Save every 5 minutes if at least 10 changes
            # Save every 60 seconds if at least 1000 changes
            self.redis_client.config_set('save', '900 1 300 10 60 1000')

            # Enable AOF (Append Only File) for maximum durability
            self.redis_client.config_set('appendonly', 'yes')
            self.redis_client.config_set('appendfsync', 'everysec')

            # Set memory policy for intelligent eviction
            self.redis_client.config_set('maxmemory-policy', 'allkeys-lru')

            # Configure max memory (optional - set to 2GB if not configured)
            try:
                current_maxmem = self.redis_client.config_get('maxmemory')['maxmemory']
                if current_maxmem == '0':  # 0 means no limit
                    self.redis_client.config_set('maxmemory', '2gb')
            except Exception:
                pass  # Ignore if we can't set maxmemory

            logger.info("✅ Redis persistence configuration applied")

        except Exception as e:
            logger.warning(f"⚠️  Could not configure Redis persistence: {e}")

    # =================================================================
    # AGENT MEMORY PERSISTENCE
    # =================================================================

    def store_agent_memory(self, agent_name: str, memory_type: str,
                          data: Dict[str, Any], ttl: int = 86400) -> bool:
        """
        Store agent memory with persistence.

        Args:
            agent_name: Name of the agent
            memory_type: Type of memory (context, knowledge, state, etc.)
            data: Data to store
            ttl: Time to live in seconds (default 24 hours)

        Returns:
            True if successful, False otherwise
        """
        try:
            key = f"agent_memory:{agent_name}:{memory_type}"
            value = json.dumps(data, default=str)

            # Store with TTL
            self.redis_client.setex(key, ttl, value)

            # Also store in persistent backup key (no TTL)
            backup_key = f"agent_memory_backup:{agent_name}:{memory_type}"
            self.redis_client.set(backup_key, value)

            logger.debug(f"Stored agent memory: {agent_name}:{memory_type}")
            return True

        except Exception as e:
            logger.error(f"Failed to store agent memory: {e}")
            return False

    def get_agent_memory(self, agent_name: str, memory_type: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve agent memory with fallback to backup.

        Args:
            agent_name: Name of the agent
            memory_type: Type of memory to retrieve

        Returns:
            Memory data if found, None otherwise
        """
        try:
            key = f"agent_memory:{agent_name}:{memory_type}"
            value = self.redis_client.get(key)

            if value is None:
                # Try backup key
                backup_key = f"agent_memory_backup:{agent_name}:{memory_type}"
                value = self.redis_client.get(backup_key)

            if value:
                return json.loads(value)

            return None

        except Exception as e:
            logger.error(f"Failed to get agent memory: {e}")
            return None

    def delete_agent_memory(self, agent_name: str, memory_type: str = None) -> bool:
        """
        Delete agent memory.

        Args:
            agent_name: Name of the agent
            memory_type: Specific memory type to delete (None for all)

        Returns:
            True if successful, False otherwise
        """
        try:
            if memory_type:
                # Delete specific memory type
                keys = [
                    f"agent_memory:{agent_name}:{memory_type}",
                    f"agent_memory_backup:{agent_name}:{memory_type}"
                ]
            else:
                # Delete all memory for agent
                pattern = f"agent_memory*:{agent_name}:*"
                keys = self.redis_client.keys(pattern)

            if keys:
                self.redis_client.delete(*keys)
                logger.info(f"Deleted agent memory for {agent_name}:{memory_type or 'all'}")

            return True

        except Exception as e:
            logger.error(f"Failed to delete agent memory: {e}")
            return False

    def list_agent_memories(self, agent_name: str) -> List[str]:
        """
        List all memory types for an agent.

        Args:
            agent_name: Name of the agent

        Returns:
            List of memory type names
        """
        try:
            pattern = f"agent_memory:{agent_name}:*"
            keys = self.redis_client.keys(pattern)

            # Extract memory types from keys
            memory_types = []
            for key in keys:
                parts = key.split(':')
                if len(parts) >= 3:
                    memory_types.append(parts[2])

            return list(set(memory_types))

        except Exception as e:
            logger.error(f"Failed to list agent memories: {e}")
            return []

    # =================================================================
    # AGENT COLLABORATION
    # =================================================================

    def create_collaboration_channel(self, session_id: str, participating_agents: List[str]) -> bool:
        """
        Create a collaboration channel for agents.

        Args:
            session_id: Unique session identifier
            participating_agents: List of agent names

        Returns:
            True if successful, False otherwise
        """
        try:
            channel_key = f"collaboration:{session_id}"
            participants_key = f"collaboration_participants:{session_id}"

            # Store session metadata
            session_data = {
                'session_id': session_id,
                'participants': participating_agents,
                'created_at': timezone.now().isoformat(),
                'status': 'active'
            }

            self.redis_client.setex(channel_key, 86400, json.dumps(session_data))  # 24 hours
            self.redis_client.setex(participants_key, 86400, json.dumps(participating_agents))

            logger.info(f"Created collaboration channel: {session_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to create collaboration channel: {e}")
            return False

    def send_collaboration_message(self, session_id: str, sender_agent: str,
                                 message: Dict[str, Any]) -> bool:
        """
        Send message to collaboration channel.

        Args:
            session_id: Session identifier
            sender_agent: Agent sending the message
            message: Message data

        Returns:
            True if successful, False otherwise
        """
        try:
            channel_name = f"collaboration_channel:{session_id}"
            message_data = {
                'sender': sender_agent,
                'timestamp': timezone.now().isoformat(),
                'message': message,
                'session_id': session_id
            }

            # Publish to channel
            self.redis_client.publish(channel_name, json.dumps(message_data))

            # Also store in message history
            history_key = f"collaboration_history:{session_id}"
            self.redis_client.lpush(history_key, json.dumps(message_data))
            self.redis_client.ltrim(history_key, 0, 999)  # Keep last 1000 messages
            self.redis_client.expire(history_key, 86400)  # 24 hours

            logger.debug(f"Sent collaboration message from {sender_agent} to {session_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to send collaboration message: {e}")
            return False

    def get_collaboration_history(self, session_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get collaboration message history.

        Args:
            session_id: Session identifier
            limit: Maximum number of messages to retrieve

        Returns:
            List of message dictionaries
        """
        try:
            history_key = f"collaboration_history:{session_id}"
            messages = self.redis_client.lrange(history_key, 0, limit - 1)

            history = []
            for msg in messages:
                try:
                    history.append(json.loads(msg))
                except json.JSONDecodeError:
                    continue

            return history

        except Exception as e:
            logger.error(f"Failed to get collaboration history: {e}")
            return []

    # =================================================================
    # DISTRIBUTED LOCKING
    # =================================================================

    def acquire_lock(self, lock_name: str, timeout: int = 30) -> bool:
        """
        Acquire a distributed lock for concurrent operations.

        Args:
            lock_name: Name of the lock
            timeout: Lock timeout in seconds

        Returns:
            True if lock acquired, False otherwise
        """
        try:
            lock_key = f"lock:{lock_name}"
            lock_value = f"{timezone.now().timestamp()}"

            # Try to acquire lock with NX (only if not exists) and EX (expire)
            result = self.redis_client.set(lock_key, lock_value, nx=True, ex=timeout)

            if result:
                logger.debug(f"Acquired lock: {lock_name}")
                return True
            else:
                logger.debug(f"Failed to acquire lock: {lock_name}")
                return False

        except Exception as e:
            logger.error(f"Failed to acquire lock {lock_name}: {e}")
            return False

    def release_lock(self, lock_name: str) -> bool:
        """
        Release a distributed lock.

        Args:
            lock_name: Name of the lock to release

        Returns:
            True if released, False otherwise
        """
        try:
            lock_key = f"lock:{lock_name}"
            self.redis_client.delete(lock_key)
            logger.debug(f"Released lock: {lock_name}")
            return True

        except Exception as e:
            logger.error(f"Failed to release lock {lock_name}: {e}")
            return False

    # =================================================================
    # SPIDER DATA CACHING
    # =================================================================

    def cache_spider_discovery(self, spider_name: str, discovery_data: Dict[str, Any],
                             ttl: int = 3600) -> bool:
        """
        Cache spider discovery data for fast access.

        Args:
            spider_name: Name of the spider
            discovery_data: Discovery data to cache
            ttl: Time to live in seconds

        Returns:
            True if successful, False otherwise
        """
        try:
            # Create cache key with timestamp for uniqueness
            timestamp = int(timezone.now().timestamp())
            cache_key = f"spider_discovery:{spider_name}:{timestamp}"

            # Store with TTL
            self.redis_client.setex(cache_key, ttl, json.dumps(discovery_data, default=str))

            # Add to spider's discovery list
            list_key = f"spider_discoveries:{spider_name}"
            self.redis_client.lpush(list_key, cache_key)
            self.redis_client.ltrim(list_key, 0, 999)  # Keep last 1000 discoveries
            self.redis_client.expire(list_key, 86400)  # 24 hours

            logger.debug(f"Cached spider discovery: {spider_name}")
            return True

        except Exception as e:
            logger.error(f"Failed to cache spider discovery: {e}")
            return False

    def get_spider_discoveries(self, spider_name: str, limit: int = 50) -> List[Dict[str, Any]]:
        """
        Get recent spider discoveries from cache.

        Args:
            spider_name: Name of the spider
            limit: Maximum number of discoveries to retrieve

        Returns:
            List of discovery dictionaries
        """
        try:
            list_key = f"spider_discoveries:{spider_name}"
            discovery_keys = self.redis_client.lrange(list_key, 0, limit - 1)

            discoveries = []
            for key in discovery_keys:
                try:
                    data = self.redis_client.get(key)
                    if data:
                        discoveries.append(json.loads(data))
                except (json.JSONDecodeError, TypeError):
                    continue

            return discoveries

        except Exception as e:
            logger.error(f"Failed to get spider discoveries: {e}")
            return []

    # =================================================================
    # EMBEDDING CACHE
    # =================================================================

    def cache_embedding(self, content_hash: str, embedding_vector: List[float],
                       model: str, ttl: int = 86400) -> bool:
        """
        Cache embedding vector for reuse.

        Args:
            content_hash: Hash of the content
            embedding_vector: The embedding vector
            model: Model used to generate embedding
            ttl: Time to live in seconds

        Returns:
            True if successful, False otherwise
        """
        try:
            cache_key = f"embedding_cache:{model}:{content_hash}"

            # Use binary client for efficient storage of vectors
            vector_data = pickle.dumps(embedding_vector)
            self.binary_client.setex(cache_key, ttl, vector_data)

            logger.debug(f"Cached embedding: {model}:{content_hash[:8]}")
            return True

        except Exception as e:
            logger.error(f"Failed to cache embedding: {e}")
            return False

    def get_cached_embedding(self, content_hash: str, model: str) -> Optional[List[float]]:
        """
        Retrieve cached embedding vector.

        Args:
            content_hash: Hash of the content
            model: Model used to generate embedding

        Returns:
            Embedding vector if found, None otherwise
        """
        try:
            cache_key = f"embedding_cache:{model}:{content_hash}"
            vector_data = self.binary_client.get(cache_key)

            if vector_data:
                return pickle.loads(vector_data)

            return None

        except Exception as e:
            logger.error(f"Failed to get cached embedding: {e}")
            return None

    # =================================================================
    # SYSTEM MONITORING
    # =================================================================

    def get_redis_info(self) -> Dict[str, Any]:
        """Get Redis server information and statistics."""
        try:
            info = self.redis_client.info()
            return {
                'redis_version': info.get('redis_version'),
                'used_memory_human': info.get('used_memory_human'),
                'connected_clients': info.get('connected_clients'),
                'total_commands_processed': info.get('total_commands_processed'),
                'keyspace_hits': info.get('keyspace_hits'),
                'keyspace_misses': info.get('keyspace_misses'),
                'persistence_enabled': {
                    'rdb': info.get('rdb_last_save_time', 0) > 0,
                    'aof': info.get('aof_enabled', 0) == 1
                }
            }
        except Exception as e:
            logger.error(f"Failed to get Redis info: {e}")
            return {}

    def cleanup_expired_data(self) -> Dict[str, int]:
        """Clean up expired data and get cleanup statistics."""
        try:
            stats = {'deleted_keys': 0, 'errors': 0}

            # Patterns to clean
            patterns = [
                'agent_memory:*',
                'collaboration:*',
                'spider_discovery:*',
                'embedding_cache:*',
                'lock:*'
            ]

            for pattern in patterns:
                try:
                    keys = self.redis_client.keys(pattern)
                    for key in keys:
                        # Check if key has TTL
                        ttl = self.redis_client.ttl(key)
                        if ttl == -1:  # No expiration set
                            # Set reasonable TTL based on key type
                            if 'agent_memory' in key:
                                self.redis_client.expire(key, 86400)  # 24 hours
                            elif 'collaboration' in key:
                                self.redis_client.expire(key, 86400)  # 24 hours
                            elif 'spider_discovery' in key:
                                self.redis_client.expire(key, 3600)   # 1 hour
                            elif 'embedding_cache' in key:
                                self.redis_client.expire(key, 86400)  # 24 hours
                            elif 'lock' in key:
                                self.redis_client.expire(key, 300)    # 5 minutes

                except Exception as e:
                    stats['errors'] += 1
                    logger.error(f"Error cleaning pattern {pattern}: {e}")

            return stats

        except Exception as e:
            logger.error(f"Failed to cleanup expired data: {e}")
            return {'deleted_keys': 0, 'errors': 1}


# Global instance
redis_persistence = RedisPersistenceManager()
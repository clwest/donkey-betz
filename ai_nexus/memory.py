"""
AI Memory and Learning System
Persistent memory storage and pattern learning for AI Nexus
"""

import json
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import redis.asyncio as redis
import hashlib

logger = logging.getLogger(__name__)


class AIMemorySystem:
    """
    Advanced memory system for AI Nexus
    Stores conversations, learned patterns, and user context
    """

    def __init__(self):
        self.redis_client = None
        self.memory_prefix = "ai_nexus:memory:"
        self.pattern_prefix = "ai_nexus:patterns:"
        self.context_prefix = "ai_nexus:context:"

    async def initialize(self):
        """Initialize Redis connection"""
        try:
            redis_url = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
            self.redis_client = await redis.from_url(redis_url)
            logger.info("AI Memory System initialized")
        except Exception as e:
            logger.error(f"Memory System Redis connection failed: {e}")

    async def store_conversation(self, user_id: str, message: Dict[str, Any]):
        """
        Store conversation message with metadata
        Maintains conversation history per user
        """
        if not self.redis_client:
            return False

        try:
            # Create conversation entry
            conversation_entry = {
                'message': message.get('content', ''),
                'role': message.get('role', 'user'),
                'agent': message.get('agent'),
                'timestamp': datetime.now().isoformat(),
                'metadata': message.get('metadata', {})
            }

            # Store in conversation list
            key = f"{self.memory_prefix}{user_id}:conversations"
            await self.redis_client.lpush(key, json.dumps(conversation_entry))

            # Keep only last 20 messages (memory optimization)
            await self.redis_client.ltrim(key, 0, 19)

            # Set TTL to 30 days
            await self.redis_client.expire(key, 2592000)

            # Update last activity
            await self.update_user_activity(user_id)

            return True

        except Exception as e:
            logger.error(f"Error storing conversation: {e}")
            return False

    async def retrieve_conversation_history(
        self,
        user_id: str,
        count: int = 10
    ) -> List[Dict[str, Any]]:
        """Retrieve recent conversation history for a user"""
        if not self.redis_client:
            return []

        try:
            key = f"{self.memory_prefix}{user_id}:conversations"
            messages = await self.redis_client.lrange(key, 0, count - 1)

            history = []
            for msg in messages:
                if isinstance(msg, bytes):
                    msg = msg.decode('utf-8')
                history.append(json.loads(msg))

            # Return in chronological order (newest first in Redis)
            return history

        except Exception as e:
            logger.error(f"Error retrieving conversation history: {e}")
            return []

    async def store_learned_pattern(
        self,
        pattern_type: str,
        pattern_data: Dict[str, Any]
    ):
        """
        Store learned patterns for future use
        Patterns help the AI improve over time
        """
        if not self.redis_client:
            return

        try:
            # Create pattern entry
            pattern_entry = {
                'type': pattern_type,
                'data': pattern_data,
                'timestamp': datetime.now().isoformat(),
                'usage_count': 0,
                'success_rate': 0.0
            }

            # Generate pattern ID
            pattern_id = self.generate_pattern_id(pattern_type, pattern_data)

            # Store pattern
            key = f"{self.pattern_prefix}{pattern_type}:{pattern_id}"
            await self.redis_client.set(key, json.dumps(pattern_entry))

            # Add to pattern index
            await self.redis_client.sadd(f"{self.pattern_prefix}index:{pattern_type}", pattern_id)

            # Set TTL to 90 days
            await self.redis_client.expire(key, 7776000)

            logger.info(f"Stored learned pattern: {pattern_type}/{pattern_id}")

        except Exception as e:
            logger.error(f"Error storing learned pattern: {e}")

    async def retrieve_patterns(
        self,
        pattern_type: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Retrieve learned patterns of a specific type"""
        if not self.redis_client:
            return []

        try:
            # Get pattern IDs from index
            pattern_ids = await self.redis_client.smembers(
                f"{self.pattern_prefix}index:{pattern_type}"
            )

            patterns = []
            for pid in list(pattern_ids)[:limit]:
                if isinstance(pid, bytes):
                    pid = pid.decode('utf-8')

                key = f"{self.pattern_prefix}{pattern_type}:{pid}"
                data = await self.redis_client.get(key)

                if data:
                    if isinstance(data, bytes):
                        data = data.decode('utf-8')
                    patterns.append(json.loads(data))

            # Sort by usage count
            patterns.sort(key=lambda x: x.get('usage_count', 0), reverse=True)

            return patterns

        except Exception as e:
            logger.error(f"Error retrieving patterns: {e}")
            return []

    async def store_user_context(self, user_id: str, context: Dict[str, Any]):
        """
        Store user context (preferences, skills, goals)
        This helps personalize AI responses
        """
        if not self.redis_client:
            return

        try:
            # Merge with existing context
            existing = await self.retrieve_user_context(user_id)
            if existing:
                context = {**existing, **context}

            # Add metadata
            context['last_updated'] = datetime.now().isoformat()

            # Store context
            key = f"{self.context_prefix}{user_id}"
            await self.redis_client.set(key, json.dumps(context))

            # Set TTL to 180 days
            await self.redis_client.expire(key, 15552000)

            logger.info(f"Updated user context for {user_id}")

        except Exception as e:
            logger.error(f"Error storing user context: {e}")

    async def retrieve_user_context(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve user context"""
        if not self.redis_client:
            return None

        try:
            key = f"{self.context_prefix}{user_id}"
            data = await self.redis_client.get(key)

            if data:
                if isinstance(data, bytes):
                    data = data.decode('utf-8')
                return json.loads(data)

            return None

        except Exception as e:
            logger.error(f"Error retrieving user context: {e}")
            return None

    async def store_decision(
        self,
        user_id: str,
        decision: Dict[str, Any]
    ):
        """Store decision made by AI for learning"""
        if not self.redis_client:
            return

        try:
            # Create decision entry
            decision_entry = {
                'user_id': user_id,
                'decision': decision.get('decision'),
                'context': decision.get('context'),
                'outcome': decision.get('outcome'),
                'confidence': decision.get('confidence', 0.5),
                'timestamp': datetime.now().isoformat()
            }

            # Store in decisions list
            key = f"{self.memory_prefix}decisions"
            await self.redis_client.lpush(key, json.dumps(decision_entry))

            # Keep only last 100 decisions (memory optimization)
            await self.redis_client.ltrim(key, 0, 99)

            # If outcome is known, update pattern learning
            if decision.get('outcome'):
                await self.update_pattern_performance(
                    decision.get('pattern_id'),
                    decision.get('outcome') == 'success'
                )

        except Exception as e:
            logger.error(f"Error storing decision: {e}")

    async def update_pattern_performance(
        self,
        pattern_id: str,
        success: bool
    ):
        """Update pattern performance metrics"""
        if not self.redis_client or not pattern_id:
            return

        try:
            # Increment usage count
            usage_key = f"{self.pattern_prefix}usage:{pattern_id}"
            total = await self.redis_client.incr(usage_key)

            # Update success count
            if success:
                success_key = f"{self.pattern_prefix}success:{pattern_id}"
                successes = await self.redis_client.incr(success_key)
            else:
                success_key = f"{self.pattern_prefix}success:{pattern_id}"
                successes = await self.redis_client.get(success_key) or 0
                if isinstance(successes, bytes):
                    successes = int(successes.decode('utf-8'))

            # Calculate success rate
            success_rate = successes / total if total > 0 else 0

            logger.info(f"Pattern {pattern_id}: {total} uses, {success_rate:.2%} success")

        except Exception as e:
            logger.error(f"Error updating pattern performance: {e}")

    async def get_agent_memory(
        self,
        agent_name: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get memory specific to an agent"""
        if not self.redis_client:
            return []

        try:
            key = f"{self.memory_prefix}agents:{agent_name}"
            memories = await self.redis_client.lrange(key, 0, limit - 1)

            agent_memory = []
            for mem in memories:
                if isinstance(mem, bytes):
                    mem = mem.decode('utf-8')
                agent_memory.append(json.loads(mem))

            return agent_memory

        except Exception as e:
            logger.error(f"Error retrieving agent memory: {e}")
            return []

    async def store_agent_memory(
        self,
        agent_name: str,
        memory: Dict[str, Any]
    ):
        """Store memory for a specific agent"""
        if not self.redis_client:
            return

        try:
            memory_entry = {
                'agent': agent_name,
                'memory': memory,
                'timestamp': datetime.now().isoformat()
            }

            key = f"{self.memory_prefix}agents:{agent_name}"
            await self.redis_client.lpush(key, json.dumps(memory_entry))

            # Keep only last 20 memories per agent (memory optimization)
            await self.redis_client.ltrim(key, 0, 19)

            # Set TTL to 30 days
            await self.redis_client.expire(key, 2592000)

        except Exception as e:
            logger.error(f"Error storing agent memory: {e}")

    async def search_memories(
        self,
        user_id: str,
        query: str,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Search through user's memories"""
        if not self.redis_client:
            return []

        try:
            # Get all conversations
            conversations = await self.retrieve_conversation_history(user_id, 100)

            # Simple keyword search (can be enhanced with embeddings later)
            query_lower = query.lower()
            relevant_memories = []

            for conv in conversations:
                message = conv.get('message', '').lower()
                if any(word in message for word in query_lower.split()):
                    relevant_memories.append(conv)

                if len(relevant_memories) >= limit:
                    break

            return relevant_memories

        except Exception as e:
            logger.error(f"Error searching memories: {e}")
            return []

    async def update_user_activity(self, user_id: str):
        """Update user's last activity timestamp"""
        if not self.redis_client:
            return

        try:
            key = f"{self.memory_prefix}activity:{user_id}"
            await self.redis_client.set(key, datetime.now().isoformat())
            await self.redis_client.expire(key, 2592000)  # 30 days

        except Exception as e:
            logger.error(f"Error updating user activity: {e}")

    async def get_active_users(self, hours: int = 24) -> List[str]:
        """Get list of active users in the last N hours"""
        if not self.redis_client:
            return []

        try:
            pattern = f"{self.memory_prefix}activity:*"
            keys = []
            async for key in self.redis_client.scan_iter(match=pattern):
                if isinstance(key, bytes):
                    key = key.decode('utf-8')
                keys.append(key)

            active_users = []
            cutoff = datetime.now() - timedelta(hours=hours)

            for key in keys:
                timestamp = await self.redis_client.get(key)
                if timestamp:
                    if isinstance(timestamp, bytes):
                        timestamp = timestamp.decode('utf-8')

                    last_active = datetime.fromisoformat(timestamp)
                    if last_active > cutoff:
                        user_id = key.split(':')[-1]
                        active_users.append(user_id)

            return active_users

        except Exception as e:
            logger.error(f"Error getting active users: {e}")
            return []

    def generate_pattern_id(self, pattern_type: str, pattern_data: Dict) -> str:
        """Generate unique ID for a pattern"""
        content = f"{pattern_type}:{json.dumps(pattern_data, sort_keys=True)}"
        return hashlib.md5(content.encode()).hexdigest()[:12]

    async def cleanup(self):
        """Cleanup Redis connection"""
        if self.redis_client:
            await self.redis_client.close()
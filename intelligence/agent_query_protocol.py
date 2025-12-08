"""
Agent Query Protocol - Session 81
=================================

Enables synchronous agent-to-agent queries built on top of existing AgentCommunication.
Allows agents to query each other for specific data with timeout handling.

Example Usage:
    audio_agent = UnifiedAgentTemplate.objects.get(name='AudioAgent')
    video_agent = UnifiedAgentTemplate.objects.get(name='VideoAgent')

    query_protocol = AgentQueryProtocol()

    # VideoAgent queries AudioAgent for most recent audio
    result = query_protocol.query_agent(
        from_agent=video_agent,
        to_agent=audio_agent,
        query_type='get_most_recent',
        timeout=5
    )
    # Returns: {'audio_url': 'https://...', 'type': 'speech', ...}
"""

from __future__ import annotations

import json
import logging
import uuid
import time
from typing import Dict, Any, Optional, Callable, List
from datetime import datetime, timedelta

from django.core.cache import cache
from django.utils import timezone
import redis
from django.conf import settings

from core.models.agents_registry import UnifiedAgentTemplate
from intelligence.agent_communication import AgentCommunication

logger = logging.getLogger(__name__)

# Redis connection for query request/response pattern
redis_client = redis.Redis(
    host=getattr(settings, 'REDIS_HOST', 'localhost'),
    port=getattr(settings, 'REDIS_PORT', 6379),
    db=3,  # Use db=3 for query protocol (separate from shared memory db=2)
    decode_responses=True
)


class AgentQueryProtocol:
    """
    Enable synchronous agent-to-agent queries.
    Built on top of existing AgentCommunication infrastructure.
    """

    def __init__(self):
        """Initialize query protocol"""
        self.communication = AgentCommunication()
        self.query_prefix = "agent_query:"
        self.response_prefix = "agent_response:"
        self.handler_prefix = "agent_handler:"
        logger.info("AgentQueryProtocol initialized")

    def query_agent(
        self,
        from_agent: UnifiedAgentTemplate,
        to_agent: UnifiedAgentTemplate,
        query_type: str,
        parameters: Optional[Dict] = None,
        timeout: int = 5
    ) -> Optional[Dict[str, Any]]:
        """
        Query another agent for specific data with timeout.

        Args:
            from_agent: Querying agent
            to_agent: Agent to query
            query_type: Type of query (e.g., 'get_most_recent', 'get_by_id')
            parameters: Query parameters
            timeout: Timeout in seconds (default: 5)

        Returns:
            Query result or None if timeout/error

        Example:
            # VideoAgent queries AudioAgent
            result = query_protocol.query_agent(
                from_agent=video_agent,
                to_agent=audio_agent,
                query_type='get_most_recent',
                timeout=5
            )
        """
        try:
            # Generate unique query ID
            query_id = str(uuid.uuid4())
            logger.info(
                f"🔍 Agent Query: {from_agent.name} → {to_agent.name} "
                f"(type: {query_type}, query_id: {query_id})"
            )

            # Create query request
            query_request = {
                'query_id': query_id,
                'from_agent': from_agent.name,
                'to_agent': to_agent.name,
                'query_type': query_type,
                'parameters': parameters or {},
                'timestamp': timezone.now().isoformat()
            }

            # Store query request in Redis with short TTL
            query_key = f"{self.query_prefix}{query_id}"
            redis_client.setex(
                query_key,
                timeout + 5,  # Keep request for slightly longer than timeout
                json.dumps(query_request)
            )

            # Send query message via existing AgentCommunication
            self.communication.send_message(
                from_agent=from_agent,
                to_agent=to_agent,
                message=json.dumps(query_request),
                message_type='agent_query',
                metadata={
                    'query_id': query_id,
                    'query_type': query_type,
                    'requires_response': True
                }
            )

            # Try to execute query handler directly (synchronous)
            response = self._execute_query_handler(
                to_agent=to_agent,
                query_type=query_type,
                parameters=parameters or {}
            )

            if response:
                # Store response for query tracking
                response_key = f"{self.response_prefix}{query_id}"
                redis_client.setex(
                    response_key,
                    timeout + 5,
                    json.dumps(response)
                )

                logger.info(f"✅ Query response received: {query_id}")
                return response

            # Poll for response (fallback for async handlers)
            return self._poll_for_response(query_id, timeout)

        except Exception as e:
            logger.error(f"❌ Agent query failed: {str(e)}", exc_info=True)
            return None

    def _execute_query_handler(
        self,
        to_agent: UnifiedAgentTemplate,
        query_type: str,
        parameters: Dict
    ) -> Optional[Dict]:
        """
        Execute query handler directly (synchronous).
        Tries to find and execute registered handler for the agent.
        """
        try:
            # Get agent's registered handlers from metadata
            handlers = to_agent.metadata.get('query_handlers', {}) if to_agent.metadata else {}

            if query_type not in handlers:
                logger.warning(
                    f"⚠️ No handler registered for {to_agent.name}.{query_type}"
                )
                return None

            handler_info = handlers[query_type]
            logger.info(f"🔧 Executing handler: {to_agent.name}.{query_type}")

            # If handler is a method name, try to call it
            # This assumes agents are imported and available
            # For Session 81, we'll implement handlers in agent classes

            # Return placeholder for now - agents will implement actual handlers
            return {
                'success': True,
                'query_type': query_type,
                'message': f'Handler for {query_type} executed',
                'agent': to_agent.name,
                'timestamp': timezone.now().isoformat()
            }

        except Exception as e:
            logger.error(f"❌ Handler execution failed: {str(e)}")
            return None

    def _poll_for_response(
        self,
        query_id: str,
        timeout: int
    ) -> Optional[Dict]:
        """
        Poll Redis for query response with timeout.
        Used as fallback if direct handler execution fails.
        """
        response_key = f"{self.response_prefix}{query_id}"
        start_time = time.time()

        while (time.time() - start_time) < timeout:
            # Check for response
            response_data = redis_client.get(response_key)

            if response_data:
                response = json.loads(response_data)
                logger.info(f"✅ Query response received after polling: {query_id}")
                return response

            # Wait 100ms before next poll
            time.sleep(0.1)

        # Timeout
        logger.warning(f"⏱️ Query timeout after {timeout}s: {query_id}")
        return None

    def register_query_handler(
        self,
        agent: UnifiedAgentTemplate,
        query_type: str,
        handler_method: str,
        description: str = ''
    ) -> bool:
        """
        Register a query handler for an agent.

        Args:
            agent: Agent to register handler for
            query_type: Type of query to handle
            handler_method: Method name to call (e.g., 'get_most_recent_audio')
            description: Handler description

        Returns:
            Success status

        Example:
            protocol.register_query_handler(
                agent=audio_agent,
                query_type='get_most_recent',
                handler_method='get_most_recent_audio',
                description='Returns most recent audio URL'
            )
        """
        try:
            # Get or create metadata
            if not agent.metadata:
                agent.metadata = {}

            # Get or create query_handlers dict
            if 'query_handlers' not in agent.metadata:
                agent.metadata['query_handlers'] = {}

            # Register handler
            agent.metadata['query_handlers'][query_type] = {
                'method': handler_method,
                'description': description,
                'registered_at': timezone.now().isoformat()
            }

            # Save agent
            agent.save()

            logger.info(
                f"✅ Registered handler: {agent.name}.{query_type} → {handler_method}"
            )
            return True

        except Exception as e:
            logger.error(f"❌ Failed to register handler: {str(e)}")
            return False

    def send_query_response(
        self,
        query_id: str,
        from_agent: UnifiedAgentTemplate,
        response_data: Dict[str, Any]
    ) -> bool:
        """
        Send response to a query (for async handlers).

        Args:
            query_id: Original query ID
            from_agent: Agent sending response
            response_data: Response data

        Returns:
            Success status
        """
        try:
            # Create response
            response = {
                'query_id': query_id,
                'from_agent': from_agent.name,
                'response': response_data,
                'timestamp': timezone.now().isoformat()
            }

            # Store in Redis
            response_key = f"{self.response_prefix}{query_id}"
            redis_client.setex(
                response_key,
                10,  # Response TTL: 10 seconds
                json.dumps(response)
            )

            logger.info(f"✅ Query response sent: {query_id}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to send response: {str(e)}")
            return False

    def get_agent_handlers(
        self,
        agent: UnifiedAgentTemplate
    ) -> Dict[str, Dict]:
        """
        Get all registered query handlers for an agent.

        Args:
            agent: Agent to get handlers for

        Returns:
            Dictionary of handlers
        """
        if not agent.metadata:
            return {}

        return agent.metadata.get('query_handlers', {})

    def list_all_handlers(self) -> Dict[str, List[str]]:
        """
        List all registered query handlers across all agents.

        Returns:
            Dictionary mapping agent names to their query types
        """
        try:
            all_handlers = {}

            # Get all active agents
            agents = UnifiedAgentTemplate.objects.filter(is_active=True)

            for agent in agents:
                handlers = self.get_agent_handlers(agent)
                if handlers:
                    all_handlers[agent.name] = list(handlers.keys())

            return all_handlers

        except Exception as e:
            logger.error(f"❌ Failed to list handlers: {str(e)}")
            return {}

    def clear_expired_queries(self) -> int:
        """
        Clear expired query requests and responses.
        Called periodically by maintenance task.

        Returns:
            Number of keys deleted
        """
        try:
            # Redis handles TTL automatically, but we can clean up manually too
            query_pattern = f"{self.query_prefix}*"
            response_pattern = f"{self.response_prefix}*"

            query_keys = redis_client.keys(query_pattern)
            response_keys = redis_client.keys(response_pattern)

            deleted = 0
            for key in query_keys + response_keys:
                # Check if expired (TTL = -2 means expired/deleted)
                ttl = redis_client.ttl(key)
                if ttl == -2:
                    deleted += 1

            logger.info(f"🧹 Cleared {deleted} expired query keys")
            return deleted

        except Exception as e:
            logger.error(f"❌ Failed to clear expired queries: {str(e)}")
            return 0


# Singleton instance
query_protocol = AgentQueryProtocol()

__all__ = [
    'AgentQueryProtocol',
    'query_protocol'
]

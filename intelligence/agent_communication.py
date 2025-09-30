"""
Agent Communication - Session 28 Core Component

Enables agents to communicate with each other via WebSocket channels.
Supports real-time messaging, orchestration coordination, and agent collaboration.

Features:
- Send messages between agents
- Broadcast to all agents in an orchestration
- Track message history
- WebSocket channel management
- Real-time agent collaboration
"""

import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from django.utils import timezone
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from agents.models import (
    UnifiedAgentTemplate,
    AgentOrchestration,
    AgentChannel,
    AgentExecution
)

logger = logging.getLogger(__name__)


class AgentCommunication:
    """
    Enable agents to communicate via WebSocket channels

    Usage:
        comm = AgentCommunication()

        # Send message from one agent to another
        comm.send_message(
            from_agent=agent1,
            to_agent=agent2,
            message="I found 10 job opportunities",
            channel=channel
        )

        # Broadcast to all agents in orchestration
        comm.broadcast_to_orchestration(
            agent=agent1,
            orchestration=orchestration,
            message="Starting task execution"
        )
    """

    def __init__(self):
        """Initialize agent communication"""
        self.channel_layer = get_channel_layer()
        logger.info("AgentCommunication initialized")

    def send_message(
        self,
        from_agent: UnifiedAgentTemplate,
        to_agent: UnifiedAgentTemplate,
        message: str,
        channel: Optional[AgentChannel] = None,
        message_type: str = 'agent_message',
        metadata: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """
        Send message from one agent to another

        Args:
            from_agent: Sending agent
            to_agent: Receiving agent
            message: Message content
            channel: Optional channel (creates one if not provided)
            message_type: Type of message
            metadata: Additional metadata

        Returns:
            Message record
        """
        logger.info(f"Message: {from_agent.name} -> {to_agent.name}")

        # Create or get channel
        if not channel:
            channel = self._get_or_create_channel([from_agent, to_agent])

        # Create message record
        message_record = {
            'from_agent': from_agent.name,
            'to_agent': to_agent.name,
            'message': message,
            'message_type': message_type,
            'timestamp': datetime.now().isoformat(),
            'metadata': metadata or {}
        }

        # Create message record in channel
        # Note: AgentChannel uses related AgentChannelMessage model for messages
        # For now, store in metadata until we wire up the full message system
        metadata = channel.metadata or {}
        message_history = metadata.get('message_history', [])
        message_history.append(message_record)
        metadata['message_history'] = message_history
        channel.metadata = metadata
        channel.message_count += 1
        channel.save()

        # Send via WebSocket if channel layer available
        if self.channel_layer:
            self._send_websocket_message(
                channel_name=channel.name,
                message=message_record
            )

        logger.info(f"Message sent: {from_agent.name} -> {to_agent.name}")

        return message_record

    def broadcast_to_orchestration(
        self,
        agent: UnifiedAgentTemplate,
        orchestration: AgentOrchestration,
        message: str,
        message_type: str = 'orchestration_broadcast',
        metadata: Optional[Dict] = None
    ) -> List[Dict[str, Any]]:
        """
        Broadcast message to all agents in an orchestration

        Args:
            agent: Broadcasting agent
            orchestration: Orchestration
            message: Message content
            message_type: Type of message
            metadata: Additional metadata

        Returns:
            List of message records
        """
        logger.info(f"Broadcasting from {agent.name} to orchestration {orchestration.id}")

        # Get all agents in orchestration
        executions = AgentExecution.objects.filter(orchestration=orchestration)
        agents = [e.agent for e in executions if e.agent != agent]

        # Send message to each agent
        messages = []
        for to_agent in agents:
            message_record = self.send_message(
                from_agent=agent,
                to_agent=to_agent,
                message=message,
                message_type=message_type,
                metadata=metadata
            )
            messages.append(message_record)

        logger.info(f"Broadcast complete: {len(messages)} messages sent")

        return messages

    def get_channel_messages(
        self,
        channel: AgentChannel,
        limit: Optional[int] = None
    ) -> List[Dict]:
        """
        Get message history from a channel

        Args:
            channel: AgentChannel instance
            limit: Optional limit on number of messages

        Returns:
            List of message records
        """
        # Get messages from metadata (until full message system is wired up)
        metadata = channel.metadata or {}
        messages = metadata.get('message_history', [])

        if limit:
            messages = messages[-limit:]

        return messages

    def create_orchestration_channel(
        self,
        orchestration: AgentOrchestration,
        agents: List[UnifiedAgentTemplate]
    ) -> AgentChannel:
        """
        Create a channel for an orchestration

        Args:
            orchestration: AgentOrchestration instance
            agents: List of participating agents

        Returns:
            AgentChannel instance
        """
        channel_name = f"orchestration_{orchestration.id}"

        channel = AgentChannel.objects.create(
            name=channel_name,
            display_name=f"Orchestration {orchestration.id}",
            description=f"Agent collaboration channel for {orchestration.name}",
            channel_type='orchestration',
            orchestration=orchestration,
            is_public=False,
            metadata={
                'agents': [a.name for a in agents],
                'created_at': datetime.now().isoformat()
            }
        )

        # Store agent IDs in active_agents field
        channel.active_agents = [a.id for a in agents]
        channel.save()

        logger.info(f"Created orchestration channel: {channel_name} with {len(agents)} agents")

        return channel

    def _get_or_create_channel(
        self,
        agents: List[UnifiedAgentTemplate]
    ) -> AgentChannel:
        """Get or create a channel for agent communication"""
        # Create channel name from sorted agent names
        agent_names = sorted([a.name for a in agents])
        channel_name = f"agent_channel_{'_'.join(agent_names)}"

        # Try to get existing channel
        try:
            channel = AgentChannel.objects.get(name=channel_name, is_archived=False)
            logger.debug(f"Using existing channel: {channel_name}")
            return channel

        except AgentChannel.DoesNotExist:
            # Create new channel
            channel = AgentChannel.objects.create(
                name=channel_name,
                display_name=channel_name.replace('_', ' ').title(),
                description=f"Agent collaboration channel",
                channel_type='general',
                is_public=False,
                metadata={
                    'agents': agent_names,
                    'created_at': datetime.now().isoformat()
                }
            )

            # Store agent IDs in active_agents field
            channel.active_agents = [a.id for a in agents]
            channel.save()

            logger.info(f"Created new channel: {channel_name}")
            return channel

    def _send_websocket_message(
        self,
        channel_name: str,
        message: Dict[str, Any]
    ):
        """Send message via WebSocket channel layer"""
        try:
            async_to_sync(self.channel_layer.group_send)(
                channel_name,
                {
                    'type': 'agent_message',
                    'message': message
                }
            )
            logger.debug(f"WebSocket message sent to {channel_name}")

        except Exception as e:
            logger.error(f"WebSocket send failed: {str(e)}")

    def get_agent_channels(
        self,
        agent: UnifiedAgentTemplate,
        active_only: bool = True
    ) -> List[AgentChannel]:
        """
        Get all channels an agent is participating in

        Args:
            agent: UnifiedAgentTemplate instance
            active_only: Only return active channels

        Returns:
            List of AgentChannel instances
        """
        channels = AgentChannel.objects.filter(participants=agent)

        if active_only:
            channels = channels.filter(is_active=True)

        return list(channels)

    def close_channel(self, channel: AgentChannel):
        """Close an agent channel"""
        channel.is_active = False
        channel.save()

        logger.info(f"Closed channel: {channel.channel_name}")

    def send_execution_update(
        self,
        execution: AgentExecution,
        status: str,
        message: str,
        metadata: Optional[Dict] = None
    ):
        """
        Send execution status update

        Args:
            execution: AgentExecution instance
            status: Execution status
            message: Status message
            metadata: Additional metadata
        """
        if not execution.orchestration:
            return

        # Get orchestration channel
        try:
            channel = AgentChannel.objects.get(
                orchestration=execution.orchestration,
                is_active=True
            )

            # Send update
            update_message = {
                'agent': execution.agent.name,
                'execution_id': execution.id,
                'status': status,
                'message': message,
                'timestamp': datetime.now().isoformat(),
                'metadata': metadata or {}
            }

            # Add to message history in metadata
            metadata = channel.metadata or {}
            message_history = metadata.get('message_history', [])
            message_history.append(update_message)
            metadata['message_history'] = message_history
            channel.metadata = metadata
            channel.message_count += 1
            channel.save()

            # Send via WebSocket
            if self.channel_layer:
                self._send_websocket_message(
                    channel_name=channel.name,
                    message=update_message
                )

            logger.info(f"Execution update sent: {execution.agent.name} - {status}")

        except AgentChannel.DoesNotExist:
            logger.warning(f"No channel found for orchestration {execution.orchestration.id}")

    def get_orchestration_status(
        self,
        orchestration: AgentOrchestration
    ) -> Dict[str, Any]:
        """
        Get real-time status of orchestration

        Args:
            orchestration: AgentOrchestration instance

        Returns:
            Status summary
        """
        # Get all executions
        executions = AgentExecution.objects.filter(orchestration=orchestration)

        # Count by status
        status_counts = {}
        for execution in executions:
            status = execution.status
            status_counts[status] = status_counts.get(status, 0) + 1

        # Get channel messages
        try:
            channel = AgentChannel.objects.get(
                orchestration=orchestration,
                is_active=True
            )
            recent_messages = self.get_channel_messages(channel, limit=10)

        except AgentChannel.DoesNotExist:
            recent_messages = []

        return {
            'orchestration_id': orchestration.id,
            'status': orchestration.status,
            'total_agents': executions.count(),
            'status_counts': status_counts,
            'recent_messages': recent_messages,
            'created_at': orchestration.created_at.isoformat(),
            'completed_at': orchestration.completed_at.isoformat() if orchestration.completed_at else None
        }
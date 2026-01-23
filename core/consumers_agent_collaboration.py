"""
Agent Collaboration Monitor WebSocket Consumer

Session 794: Real-time monitoring of agent-to-agent collaborations.
Enables live view of active collaborations, message flow, and agent status
for all 213 agents (74 core + 139 persona) + 25 advisors.
"""

import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone

logger = logging.getLogger(__name__)


class AgentCollaborationMonitorConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time agent collaboration monitoring.

    Events sent to clients:
    - collaboration:started - New collaboration initiated
    - collaboration:updated - Status change on existing collaboration
    - collaboration:completed - Collaboration finished
    - collaboration:failed - Collaboration failed
    - message:sent - Inter-agent message sent
    - agent:status_changed - Agent status changed (idle/busy/collaborating)
    - stats:updated - Statistics update

    Events received from clients:
    - subscribe - Subscribe to collaboration updates
    - unsubscribe - Unsubscribe from updates
    - get_active - Get all active collaborations
    - get_agents - Get all agents with status
    - get_stats - Get collaboration statistics
    - ping - Keep-alive
    """

    async def connect(self):
        """Handle WebSocket connection"""
        self.room_group_name = 'agent_collaboration_monitor'
        self.subscribed_agents = set()  # Track specific agent subscriptions

        # Join the collaboration monitor room
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

        # Send initial state
        await self.send_initial_state()

        logger.info(f"Client connected to agent collaboration monitor")

    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        logger.info(f"Client disconnected from agent collaboration monitor")

    async def receive(self, text_data):
        """Handle incoming WebSocket messages"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')

            handlers = {
                'subscribe': self.handle_subscribe,
                'unsubscribe': self.handle_unsubscribe,
                'get_active': self.handle_get_active,
                'get_agents': self.handle_get_agents,
                'get_stats': self.handle_get_stats,
                'get_recent_messages': self.handle_get_recent_messages,
                'get_collaboration_detail': self.handle_get_collaboration_detail,
                'ping': self.handle_ping,
            }

            handler = handlers.get(message_type)
            if handler:
                await handler(data)
            else:
                await self.send(text_data=json.dumps({
                    'type': 'error',
                    'message': f'Unknown message type: {message_type}'
                }))

        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON'
            }))
        except Exception as e:
            logger.error(f"Error in collaboration monitor consumer: {e}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': str(e)
            }))

    # ========== Handler Methods ==========

    async def handle_subscribe(self, data):
        """Subscribe to specific agent(s) or all collaborations"""
        agent_names = data.get('agents', [])
        if agent_names:
            self.subscribed_agents.update(agent_names)
        await self.send(text_data=json.dumps({
            'type': 'subscribed',
            'agents': list(self.subscribed_agents)
        }))

    async def handle_unsubscribe(self, data):
        """Unsubscribe from specific agent(s)"""
        agent_names = data.get('agents', [])
        for name in agent_names:
            self.subscribed_agents.discard(name)
        await self.send(text_data=json.dumps({
            'type': 'unsubscribed',
            'agents': agent_names
        }))

    async def handle_get_active(self, data):
        """Get all active collaborations"""
        collaborations = await self.get_active_collaborations()
        await self.send(text_data=json.dumps({
            'type': 'active_collaborations',
            'collaborations': collaborations,
            'count': len(collaborations),
            'timestamp': datetime.now().isoformat()
        }))

    async def handle_get_agents(self, data):
        """Get all agents with their current status"""
        include_persona = data.get('include_persona', True)
        include_advisors = data.get('include_advisors', True)

        agents = await self.get_all_agents(include_persona, include_advisors)
        await self.send(text_data=json.dumps({
            'type': 'agents_list',
            'agents': agents,
            'counts': {
                'total': len(agents),
                'core': sum(1 for a in agents if a['type'] == 'core'),
                'persona': sum(1 for a in agents if a['type'] == 'persona'),
                'advisor': sum(1 for a in agents if a['type'] == 'advisor'),
                'active': sum(1 for a in agents if a['status'] == 'collaborating'),
                'idle': sum(1 for a in agents if a['status'] == 'idle'),
            },
            'timestamp': datetime.now().isoformat()
        }))

    async def handle_get_stats(self, data):
        """Get collaboration statistics"""
        hours = data.get('hours', 24)
        stats = await self.get_collaboration_stats(hours)
        await self.send(text_data=json.dumps({
            'type': 'collaboration_stats',
            'stats': stats,
            'period_hours': hours,
            'timestamp': datetime.now().isoformat()
        }))

    async def handle_get_recent_messages(self, data):
        """Get recent inter-agent messages"""
        limit = data.get('limit', 50)
        messages = await self.get_recent_messages(limit)
        await self.send(text_data=json.dumps({
            'type': 'recent_messages',
            'messages': messages,
            'count': len(messages),
            'timestamp': datetime.now().isoformat()
        }))

    async def handle_get_collaboration_detail(self, data):
        """Get detailed info about a specific collaboration"""
        collaboration_id = data.get('collaboration_id')
        if not collaboration_id:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'collaboration_id required'
            }))
            return

        detail = await self.get_collaboration_detail(collaboration_id)
        await self.send(text_data=json.dumps({
            'type': 'collaboration_detail',
            'collaboration': detail,
            'timestamp': datetime.now().isoformat()
        }))

    async def handle_ping(self, data):
        """Keep-alive ping"""
        await self.send(text_data=json.dumps({
            'type': 'pong',
            'timestamp': datetime.now().isoformat()
        }))

    # ========== Broadcast Methods ==========

    async def collaboration_started(self, event):
        """Broadcast when a new collaboration starts"""
        await self.send(text_data=json.dumps({
            'type': 'collaboration:started',
            'collaboration': event['collaboration'],
            'timestamp': event['timestamp']
        }))

    async def collaboration_updated(self, event):
        """Broadcast when a collaboration status changes"""
        await self.send(text_data=json.dumps({
            'type': 'collaboration:updated',
            'collaboration': event['collaboration'],
            'timestamp': event['timestamp']
        }))

    async def collaboration_completed(self, event):
        """Broadcast when a collaboration completes"""
        await self.send(text_data=json.dumps({
            'type': 'collaboration:completed',
            'collaboration': event['collaboration'],
            'timestamp': event['timestamp']
        }))

    async def collaboration_failed(self, event):
        """Broadcast when a collaboration fails"""
        await self.send(text_data=json.dumps({
            'type': 'collaboration:failed',
            'collaboration': event['collaboration'],
            'error': event.get('error'),
            'timestamp': event['timestamp']
        }))

    async def message_sent(self, event):
        """Broadcast when an inter-agent message is sent"""
        await self.send(text_data=json.dumps({
            'type': 'message:sent',
            'message': event['message'],
            'timestamp': event['timestamp']
        }))

    async def agent_status_changed(self, event):
        """Broadcast when an agent's status changes"""
        await self.send(text_data=json.dumps({
            'type': 'agent:status_changed',
            'agent_name': event['agent_name'],
            'old_status': event.get('old_status'),
            'new_status': event['new_status'],
            'timestamp': event['timestamp']
        }))

    async def stats_updated(self, event):
        """Broadcast statistics update"""
        await self.send(text_data=json.dumps({
            'type': 'stats:updated',
            'stats': event['stats'],
            'timestamp': event['timestamp']
        }))

    # ========== Database Methods ==========

    async def send_initial_state(self):
        """Send initial state to newly connected client"""
        active_collabs = await self.get_active_collaborations()
        stats = await self.get_collaboration_stats(24)
        agent_counts = await self.get_agent_counts()

        await self.send(text_data=json.dumps({
            'type': 'initial_state',
            'active_collaborations': active_collabs,
            'stats': stats,
            'agent_counts': agent_counts,
            'timestamp': datetime.now().isoformat()
        }))

    @database_sync_to_async
    def get_active_collaborations(self) -> List[Dict[str, Any]]:
        """Get all currently active collaborations"""
        from core.models_unified_system import CollaborationSession

        active = CollaborationSession.objects.filter(
            status__in=['pending', 'active']
        ).order_by('-started_at')[:50]

        return [{
            'id': str(c.id),
            'requester_agent': c.requester_agent,
            'collaboration_type': c.collaboration_type,
            'participating_agents': c.participating_agents or [],
            'status': c.status,
            'task_description': c.task_description[:200] if c.task_description else '',
            'started_at': c.started_at.isoformat(),
            'completed_at': c.completed_at.isoformat() if c.completed_at else None,
        } for c in active]

    @database_sync_to_async
    def get_all_agents(self, include_persona: bool, include_advisors: bool) -> List[Dict[str, Any]]:
        """Get all agents with their current status"""
        from core.models import Agent, Advisor
        from core.agent_router import AgentRouter

        agents = []
        router = AgentRouter()
        routable_names = set(router.AGENT_MAP.keys())

        # Get all agents from DB
        for agent in Agent.objects.filter(is_active=True):
            is_core = agent.name in routable_names

            if not include_persona and not is_core:
                continue

            agents.append({
                'id': str(agent.id),
                'name': agent.name,
                'type': 'core' if is_core else 'persona',
                'category': agent.agent_type or 'general',
                'description': agent.description or '',
                'status': self._get_agent_status(agent),
                'effectiveness_score': agent.effectiveness_score or 0,
                'last_active': agent.updated_at.isoformat() if agent.updated_at else None,
            })

        # Add advisors if requested
        if include_advisors:
            for advisor in Advisor.objects.filter(is_active=True):
                agents.append({
                    'id': f'advisor_{advisor.id}',
                    'name': advisor.name,
                    'type': 'advisor',
                    'category': advisor.category or 'advisor',
                    'description': advisor.expertise or '',
                    'status': 'available',
                    'effectiveness_score': advisor.influence_score or 0,
                    'last_active': advisor.updated_at.isoformat() if advisor.updated_at else None,
                })

        return agents

    def _get_agent_status(self, agent) -> str:
        """Determine agent's current status"""
        from core.models_unified_system import CollaborationSession

        # Check if agent is in any active collaboration
        active_count = CollaborationSession.objects.filter(
            status__in=['pending', 'active'],
            participating_agents__contains=[agent.name]
        ).count()

        if active_count > 0:
            return 'collaborating'

        # Check recent activity
        if agent.updated_at:
            if (timezone.now() - agent.updated_at).total_seconds() < 300:  # 5 minutes
                return 'active'

        return 'idle'

    @database_sync_to_async
    def get_agent_counts(self) -> Dict[str, int]:
        """Get agent counts by type"""
        from core.models import Agent, Advisor
        from core.agent_router import AgentRouter

        router = AgentRouter()
        routable_names = set(router.AGENT_MAP.keys())

        total_agents = Agent.objects.filter(is_active=True).count()
        all_agent_names = set(Agent.objects.filter(is_active=True).values_list('name', flat=True))

        core_count = len(routable_names & all_agent_names)
        persona_count = total_agents - core_count
        advisor_count = Advisor.objects.filter(is_active=True).count()

        return {
            'total': total_agents + advisor_count,
            'core': core_count,
            'persona': persona_count,
            'advisors': advisor_count,
        }

    @database_sync_to_async
    def get_collaboration_stats(self, hours: int) -> Dict[str, Any]:
        """Get collaboration statistics for the given time period"""
        from core.models_unified_system import CollaborationSession, InterAgentMessage
        from django.db.models import Count, Avg

        since = timezone.now() - timedelta(hours=hours)

        # Collaboration stats
        collabs = CollaborationSession.objects.filter(started_at__gte=since)

        total = collabs.count()
        completed = collabs.filter(status='completed').count()
        failed = collabs.filter(status='failed').count()
        active = collabs.filter(status__in=['pending', 'active']).count()

        # Average quality score
        avg_quality = collabs.filter(
            status='completed',
            quality_score__isnull=False
        ).aggregate(avg=Avg('quality_score'))['avg'] or 0

        # By type breakdown
        by_type = dict(collabs.values('collaboration_type').annotate(
            count=Count('id')
        ).values_list('collaboration_type', 'count'))

        # Message stats
        messages = InterAgentMessage.objects.filter(created_at__gte=since)
        message_count = messages.count()

        # Most active agents
        from collections import Counter
        agent_counts = Counter()
        for collab in collabs:
            if collab.participating_agents:
                for agent in collab.participating_agents:
                    agent_counts[agent] += 1

        most_active = [{'name': name, 'count': count}
                       for name, count in agent_counts.most_common(10)]

        return {
            'total_collaborations': total,
            'completed': completed,
            'failed': failed,
            'active': active,
            'success_rate': (completed / total * 100) if total > 0 else 0,
            'average_quality_score': round(avg_quality, 1),
            'by_type': by_type,
            'total_messages': message_count,
            'most_active_agents': most_active,
        }

    @database_sync_to_async
    def get_recent_messages(self, limit: int) -> List[Dict[str, Any]]:
        """Get recent inter-agent messages"""
        from core.models_unified_system import InterAgentMessage

        messages = InterAgentMessage.objects.order_by('-created_at')[:limit]

        return [{
            'id': str(m.id),
            'from_agent': m.sender_agent,
            'to_agent': m.receiver_agent,
            'message_type': m.message_type,
            'content_preview': str(m.content or '')[:200] if m.content else '',
            'priority': m.priority,
            'is_read': m.is_read,
            'created_at': m.created_at.isoformat(),
        } for m in messages]

    @database_sync_to_async
    def get_collaboration_detail(self, collaboration_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific collaboration"""
        from core.models_unified_system import CollaborationSession, InterAgentMessage

        try:
            collab = CollaborationSession.objects.get(id=collaboration_id)
        except CollaborationSession.DoesNotExist:
            return None

        # Get messages for this collaboration
        messages = InterAgentMessage.objects.filter(
            correlation_id=collaboration_id
        ).order_by('created_at')

        return {
            'id': str(collab.id),
            'requester_agent': collab.requester_agent,
            'collaboration_type': collab.collaboration_type,
            'participating_agents': collab.participating_agents or [],
            'status': collab.status,
            'task_description': collab.task_description,
            'input_data': collab.input_data,
            'output_data': collab.output_data,
            'quality_score': collab.quality_score,
            'execution_time_ms': collab.execution_time_ms,
            'started_at': collab.started_at.isoformat(),
            'completed_at': collab.completed_at.isoformat() if collab.completed_at else None,
            'messages': [{
                'id': str(m.id),
                'from_agent': m.sender_agent,
                'to_agent': m.receiver_agent,
                'message_type': m.message_type,
                'content': m.content,
                'created_at': m.created_at.isoformat(),
            } for m in messages],
        }


# ========== Helper Functions for Broadcasting ==========

async def broadcast_collaboration_event(event_type: str, collaboration_data: Dict[str, Any], error: str = None):
    """
    Broadcast a collaboration event to all connected clients.
    Call this from collaboration service when events occur.
    """
    from channels.layers import get_channel_layer

    channel_layer = get_channel_layer()
    if not channel_layer:
        logger.warning("No channel layer available for broadcasting")
        return

    event = {
        'type': event_type.replace(':', '_'),  # collaboration:started -> collaboration_started
        'collaboration': collaboration_data,
        'timestamp': datetime.now().isoformat(),
    }

    if error:
        event['error'] = error

    await channel_layer.group_send('agent_collaboration_monitor', event)


async def broadcast_message_event(message_data: Dict[str, Any]):
    """Broadcast an inter-agent message event"""
    from channels.layers import get_channel_layer

    channel_layer = get_channel_layer()
    if not channel_layer:
        return

    await channel_layer.group_send('agent_collaboration_monitor', {
        'type': 'message_sent',
        'message': message_data,
        'timestamp': datetime.now().isoformat(),
    })


async def broadcast_agent_status_change(agent_name: str, old_status: str, new_status: str):
    """Broadcast when an agent's status changes"""
    from channels.layers import get_channel_layer

    channel_layer = get_channel_layer()
    if not channel_layer:
        return

    await channel_layer.group_send('agent_collaboration_monitor', {
        'type': 'agent_status_changed',
        'agent_name': agent_name,
        'old_status': old_status,
        'new_status': new_status,
        'timestamp': datetime.now().isoformat(),
    })

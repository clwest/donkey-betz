"""
System Events Consumer - Real-time event broadcasting across all pages.

Session 714 - Phase 3: Event Broadcasting

This consumer broadcasts system-wide events to all connected clients,
enabling real-time updates across pages without polling.

Event Types:
- agent_execution_complete - Agent finished task
- agent_execution_failed - Agent task failed
- gate_became_critical - Gate needs attention
- body_status_changed - Body health changed
- file_modified - Workspace file changed
- pilot_started - New pilot started
- pilot_completed - Pilot finished
- dream_generated - Agent dream created
- level_up - Agent leveled up
- hive_mind_started - Hive mind session started
"""

import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async

logger = logging.getLogger(__name__)


class SystemEventsConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for system-wide event broadcasting.

    All connected clients join the 'system_events' group and receive
    real-time notifications about system state changes.
    """

    GROUP_NAME = "system_events"

    async def connect(self):
        """Accept connection and join the system_events group."""
        # Add to system events group
        await self.channel_layer.group_add(
            self.GROUP_NAME,
            self.channel_name
        )
        await self.accept()

        logger.info(f"System events client connected: {self.channel_name}")

        # Send initial connection confirmation
        await self.send(text_data=json.dumps({
            "type": "connection_established",
            "message": "Connected to system events stream",
            "channel": self.channel_name
        }))

    async def disconnect(self, close_code):
        """Leave the system_events group on disconnect."""
        await self.channel_layer.group_discard(
            self.GROUP_NAME,
            self.channel_name
        )
        logger.info(f"System events client disconnected: {self.channel_name} (code: {close_code})")

    async def receive(self, text_data):
        """
        Handle incoming messages from clients.

        Clients can subscribe to specific event types or request current state.
        """
        try:
            data = json.loads(text_data)
            action = data.get("action")

            if action == "ping":
                # Simple keepalive
                await self.send(text_data=json.dumps({
                    "type": "pong",
                    "timestamp": data.get("timestamp")
                }))

            elif action == "get_status":
                # Return current system status
                status = await self._get_system_status()
                await self.send(text_data=json.dumps({
                    "type": "system_status",
                    "data": status
                }))

        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                "type": "error",
                "message": "Invalid JSON"
            }))
        except Exception as e:
            logger.error(f"Error in system events receive: {e}")
            await self.send(text_data=json.dumps({
                "type": "error",
                "message": str(e)
            }))

    # ========== Event Handlers ==========
    # These methods are called when events are broadcast to the group

    async def system_event(self, event):
        """Generic system event handler."""
        await self.send(text_data=json.dumps({
            "type": event.get("event_type", "system_event"),
            "data": event.get("data", {}),
            "timestamp": event.get("timestamp")
        }))

    async def agent_execution_complete(self, event):
        """Agent finished executing a task."""
        await self.send(text_data=json.dumps({
            "type": "agent_execution_complete",
            "data": event.get("data", {}),
            "timestamp": event.get("timestamp")
        }))

    async def agent_execution_failed(self, event):
        """Agent task execution failed."""
        await self.send(text_data=json.dumps({
            "type": "agent_execution_failed",
            "data": event.get("data", {}),
            "timestamp": event.get("timestamp")
        }))

    async def gate_became_critical(self, event):
        """A gate became critical and needs attention."""
        await self.send(text_data=json.dumps({
            "type": "gate_became_critical",
            "data": event.get("data", {}),
            "timestamp": event.get("timestamp")
        }))

    async def body_status_changed(self, event):
        """Body health status changed."""
        await self.send(text_data=json.dumps({
            "type": "body_status_changed",
            "data": event.get("data", {}),
            "timestamp": event.get("timestamp")
        }))

    async def file_modified(self, event):
        """A workspace file was modified."""
        await self.send(text_data=json.dumps({
            "type": "file_modified",
            "data": event.get("data", {}),
            "timestamp": event.get("timestamp")
        }))

    async def pilot_started(self, event):
        """A new pilot was started."""
        await self.send(text_data=json.dumps({
            "type": "pilot_started",
            "data": event.get("data", {}),
            "timestamp": event.get("timestamp")
        }))

    async def pilot_completed(self, event):
        """A pilot was completed."""
        await self.send(text_data=json.dumps({
            "type": "pilot_completed",
            "data": event.get("data", {}),
            "timestamp": event.get("timestamp")
        }))

    async def dream_generated(self, event):
        """An agent dream was generated."""
        await self.send(text_data=json.dumps({
            "type": "dream_generated",
            "data": event.get("data", {}),
            "timestamp": event.get("timestamp")
        }))

    async def level_up(self, event):
        """An agent leveled up."""
        await self.send(text_data=json.dumps({
            "type": "level_up",
            "data": event.get("data", {}),
            "timestamp": event.get("timestamp")
        }))

    async def hive_mind_started(self, event):
        """A hive mind session was started."""
        await self.send(text_data=json.dumps({
            "type": "hive_mind_started",
            "data": event.get("data", {}),
            "timestamp": event.get("timestamp")
        }))

    # ========== Session 2734: Mission Completion Chain §1 ==========

    async def mission_verdict(self, event):
        """A MissionRunner emitted a terminal verdict.

        Fired by ``core/signals/mission_verdict_signals.py`` post_save
        receiver on ``OpsRunEvent(label='verdict_issued:*')``. Frontend
        CommandCenter NowHub invalidates the ``['active-work']`` query
        on receipt so the mission's ``run.status`` transition is
        visible without waiting for the 15s poll.
        """
        await self.send(text_data=json.dumps({
            "type": "mission_verdict",
            "data": event.get("data", {}),
            "timestamp": event.get("timestamp")
        }))

    # ========== Session 768: Orchestration Events ==========

    async def orchestration_started(self, event):
        """An orchestration workflow started."""
        await self.send(text_data=json.dumps({
            "type": "orchestration_started",
            "data": event.get("data", {}),
            "timestamp": event.get("timestamp")
        }))

    async def orchestration_step_started(self, event):
        """An orchestration step started."""
        await self.send(text_data=json.dumps({
            "type": "orchestration_step_started",
            "data": event.get("data", {}),
            "timestamp": event.get("timestamp")
        }))

    async def orchestration_step_completed(self, event):
        """An orchestration step completed."""
        await self.send(text_data=json.dumps({
            "type": "orchestration_step_completed",
            "data": event.get("data", {}),
            "timestamp": event.get("timestamp")
        }))

    async def orchestration_step_failed(self, event):
        """An orchestration step failed."""
        await self.send(text_data=json.dumps({
            "type": "orchestration_step_failed",
            "data": event.get("data", {}),
            "timestamp": event.get("timestamp")
        }))

    async def orchestration_paused(self, event):
        """An orchestration is waiting for approval."""
        await self.send(text_data=json.dumps({
            "type": "orchestration_paused",
            "data": event.get("data", {}),
            "timestamp": event.get("timestamp")
        }))

    async def orchestration_completed(self, event):
        """An orchestration workflow completed."""
        await self.send(text_data=json.dumps({
            "type": "orchestration_completed",
            "data": event.get("data", {}),
            "timestamp": event.get("timestamp")
        }))

    async def orchestration_failed(self, event):
        """An orchestration workflow failed."""
        await self.send(text_data=json.dumps({
            "type": "orchestration_failed",
            "data": event.get("data", {}),
            "timestamp": event.get("timestamp")
        }))

    # ========== Helper Methods ==========

    @sync_to_async
    def _get_system_status(self):
        """Get current system status for status requests."""
        try:
            from core.models_unified_system import Agent, AgentExecution
            from core.models_human_layer import Gate, Pilot
            from django.utils import timezone
            from datetime import timedelta

            now = timezone.now()
            last_24h = now - timedelta(hours=24)

            # Get counts
            total_agents = Agent.objects.filter(is_active=True).count()
            recent_executions = AgentExecution.objects.filter(
                created_at__gte=last_24h
            ).count()
            active_pilots = Pilot.objects.filter(status='running').count()
            critical_gates = Gate.objects.filter(
                status='critical',
                resolved_at__isnull=True
            ).count()

            return {
                "total_agents": total_agents,
                "recent_executions_24h": recent_executions,
                "active_pilots": active_pilots,
                "critical_gates": critical_gates,
                "timestamp": now.isoformat()
            }
        except Exception as e:
            logger.error(f"Error getting system status: {e}")
            return {"error": str(e)}


# ========== Event Emitter Utility ==========

async def emit_system_event(event_type: str, data: dict):
    """
    Emit a system event to all connected clients.

    Usage:
        from core.consumers.system_events_consumer import emit_system_event
        await emit_system_event('agent_execution_complete', {
            'agent_id': str(agent.id),
            'agent_name': agent.name,
            'execution_id': str(execution.id),
            'status': 'completed'
        })

    Or synchronously:
        from asgiref.sync import async_to_sync
        from channels.layers import get_channel_layer

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            'system_events',
            {
                'type': 'agent_execution_complete',
                'data': {...},
                'timestamp': timezone.now().isoformat()
            }
        )
    """
    from channels.layers import get_channel_layer
    from django.utils import timezone

    channel_layer = get_channel_layer()
    if channel_layer is None:
        logger.warning("No channel layer configured - cannot emit system event")
        return

    await channel_layer.group_send(
        SystemEventsConsumer.GROUP_NAME,
        {
            "type": event_type.replace("-", "_"),  # Convert to valid Python method name
            "data": data,
            "timestamp": timezone.now().isoformat()
        }
    )


def emit_system_event_sync(event_type: str, data: dict):
    """
    Synchronous version of emit_system_event for use in regular Django views/tasks.

    Usage:
        from core.consumers.system_events_consumer import emit_system_event_sync
        emit_system_event_sync('agent_execution_complete', {
            'agent_id': str(agent.id),
            'agent_name': agent.name
        })
    """
    from channels.layers import get_channel_layer
    from asgiref.sync import async_to_sync
    from django.utils import timezone

    channel_layer = get_channel_layer()
    if channel_layer is None:
        logger.warning("No channel layer configured - cannot emit system event")
        return

    async_to_sync(channel_layer.group_send)(
        SystemEventsConsumer.GROUP_NAME,
        {
            "type": event_type.replace("-", "_"),
            "data": data,
            "timestamp": timezone.now().isoformat()
        }
    )

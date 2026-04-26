<!-- ARCHIVED-DOC-V1 -->
> # ⛔ ARCHIVED — 2026-04-26 (Session 1100)
>
> This doc was retired during the Session 1099 → 1100 doc-drift cleanup
> because its stats diverged materially from runtime reality. **Content
> below is preserved unchanged for historical reference and potential
> future book material** (Chris's "how I learned to work with AI to build
> this platform").
>
> **What this used to be:** WebSocket consumer catalog
>
> **Where to look now:**
> - [core/consumers*.py (source)](/core/consumers*.py (source))
> - [docs/topics/frontend.md](/docs/topics/frontend.md)
>
> **Source of truth for live numbers:** `docs/PLATFORM_INVENTORY.md`
> (regenerable via `python manage.py generate_platform_inventory`).

---

# WebSocket Consumers Documentation

**Total Consumers:** 20+
**Location:** `core/consumers.py`
**Routing:** `core/routing.py`
**Last Updated:** January 2026

---

## Table of Contents

1. [Overview](#overview)
2. [Consumer List](#consumer-list)
3. [Key Consumers Detail](#key-consumers-detail)
4. [WebSocket Routes](#websocket-routes)
5. [Usage](#usage)

---

## Overview

WebSocket consumers provide real-time bidirectional communication for live updates, chat, and streaming features.

### Architecture

```
Browser/Client
     │
     │ WebSocket Connection
     ▼
Django Channels (ASGI)
     │
     ▼
URL Router (core/routing.py)
     │
     ▼
Consumer Class (core/consumers.py)
     │
     ├── connect() - Handle connection
     ├── receive() - Handle incoming messages
     ├── disconnect() - Handle disconnection
     └── Group messaging via Redis
```

### Technology Stack
- **Django Channels** - WebSocket framework
- **Redis** - Channel layer backend
- **ASGI** - Asynchronous server gateway

---

## Consumer List

### Agent & Execution (5)

| Consumer | Purpose | WebSocket Path |
|----------|---------|----------------|
| `AgentProgressConsumer` | Agent execution progress | `/ws/agents/<instance_id>/` |
| `AgentChannelsConsumer` | Agent channel updates | `/ws/agent-channels/` |
| `AgentExecutionConsumer` | Execution monitoring | `/ws/agent-execution/` |
| `AgentOrchestrationConsumer` | Orchestration updates | `/ws/agent-orchestration/` |
| `OrchestrationConsumer` | General orchestration | `/ws/orchestration/` |

### Dashboard & Monitoring (4)

| Consumer | Purpose | WebSocket Path |
|----------|---------|----------------|
| `DashboardConsumer` | Real-time dashboard updates | `/ws/dashboard/` |
| `CommandCenterConsumerLegacy` | Command center updates | `/ws/command-center/` |
| `NotificationConsumer` | Push notifications | `/ws/notifications/` |
| `NeuralOrchestraConsumer` | Neural orchestra visualization | `/ws/neural-orchestra/` |

### Sports & Betting (4)

| Consumer | Purpose | WebSocket Path |
|----------|---------|----------------|
| `LiveSportsConsumer` | Live sports updates | `/ws/live-sports/` |
| `SportsDashboardConsumer` | Sports dashboard updates | `/ws/sports-dashboard/` |
| `ArbitrageConsumer` | Arbitrage opportunity alerts | `/ws/arbitrage/` |
| `SportsArbitrageConsumer` | Sports arbitrage updates | `/ws/sports-arbitrage/` |
| `SportsRecommendationConsumer` | Sports recommendations | `/ws/sports-recommendations/` |

### Chat & Assistant (2)

| Consumer | Purpose | WebSocket Path |
|----------|---------|----------------|
| `AssistantChatConsumer` | AI assistant chat | `/ws/chat/<session_id>/` |
| `EnhancedAIAssistantConsumer` | Enhanced AI chat | `/ws/enhanced-chat/` |

### Content & Processing (3)

| Consumer | Purpose | WebSocket Path |
|----------|---------|----------------|
| `ContentProcessingConsumer` | Content generation progress | `/ws/content-processing/` |
| `ContentAnalyticsConsumer` | Content analytics updates | `/ws/content-analytics/` |
| `OpportunityScannerConsumer` | Opportunity scanning | `/ws/opportunity-scanner/` |

### Special (2)

| Consumer | Purpose | WebSocket Path |
|----------|---------|----------------|
| `MythologyConsumer` | Mythology features | `/ws/mythology/` |
| `TestEchoConsumer` | Testing/debugging | `/ws/test-echo/` |

---

## Key Consumers Detail

### AgentProgressConsumer

Real-time agent execution progress and status updates.

```python
class AgentProgressConsumer(SafeWebSocketMixin, AsyncWebsocketConsumer):
    """Real-time agent execution progress"""

    async def connect(self):
        self.instance_id = self.scope['url_route']['kwargs'].get('instance_id', 'all')
        self.room_group_name = 'agents_general'
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def agent_progress(self, event):
        """Handle agent progress updates"""
        await self.safe_send({
            'type': 'agent_progress',
            'agent': event['agent'],
            'progress': event['progress'],
            'status': event['status']
        })
```

**Events:**
- `agent_progress` - Progress percentage update
- `agent_started` - Execution started
- `agent_completed` - Execution completed
- `agent_error` - Error occurred

### DashboardConsumer

Real-time dashboard updates for system monitoring.

```python
class DashboardConsumer(SafeWebSocketMixin, AsyncWebsocketConsumer):
    """Real-time dashboard updates"""

    async def connect(self):
        await self.channel_layer.group_add('dashboard_updates', self.channel_name)
        await self.accept()

    async def dashboard_update(self, event):
        """Handle dashboard updates"""
        await self.safe_send(event['data'])
```

**Events:**
- `system_status` - System health update
- `agent_activity` - Agent activity update
- `spider_collection` - Spider data collected
- `metric_update` - Metric change

### AssistantChatConsumer

AI assistant real-time chat interface.

```python
class AssistantChatConsumer(SafeWebSocketMixin, AsyncWebsocketConsumer):
    """AI assistant chat"""

    async def connect(self):
        self.session_id = self.scope['url_route']['kwargs']['session_id']
        self.room_group_name = f'chat_{self.session_id}'
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def receive(self, text_data):
        """Handle incoming chat message"""
        data = json.loads(text_data)
        message = data['message']
        # Process with AI and stream response
        async for chunk in self.process_message(message):
            await self.safe_send({'type': 'chunk', 'content': chunk})
```

**Events:**
- `message` - User message
- `chunk` - AI response chunk (streaming)
- `complete` - Response complete
- `typing` - Typing indicator

### LiveSportsConsumer

Real-time sports scores and updates.

```python
class LiveSportsConsumer(SafeWebSocketMixin, AsyncWebsocketConsumer):
    """Live sports updates"""

    async def connect(self):
        await self.channel_layer.group_add('live_sports', self.channel_name)
        await self.accept()

    async def score_update(self, event):
        """Handle score updates"""
        await self.safe_send({
            'type': 'score_update',
            'game_id': event['game_id'],
            'scores': event['scores'],
            'timestamp': event['timestamp']
        })
```

**Events:**
- `score_update` - Score change
- `game_started` - Game started
- `game_ended` - Game ended
- `odds_update` - Odds changed

---

## WebSocket Routes

Defined in `core/routing.py`:

```python
from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    # Agents
    re_path(r'ws/agents/(?P<instance_id>\w+)/$', consumers.AgentProgressConsumer.as_asgi()),
    re_path(r'ws/agent-channels/$', consumers.AgentChannelsConsumer.as_asgi()),
    re_path(r'ws/agent-execution/$', consumers.AgentExecutionConsumer.as_asgi()),

    # Dashboard
    re_path(r'ws/dashboard/$', consumers.DashboardConsumer.as_asgi()),
    re_path(r'ws/command-center/$', consumers.CommandCenterConsumerLegacy.as_asgi()),

    # Chat
    re_path(r'ws/chat/(?P<session_id>\w+)/$', consumers.AssistantChatConsumer.as_asgi()),

    # Sports
    re_path(r'ws/live-sports/$', consumers.LiveSportsConsumer.as_asgi()),
    re_path(r'ws/sports-dashboard/$', consumers.SportsDashboardConsumer.as_asgi()),
    re_path(r'ws/arbitrage/$', consumers.ArbitrageConsumer.as_asgi()),

    # Content
    re_path(r'ws/content-processing/$', consumers.ContentProcessingConsumer.as_asgi()),

    # Notifications
    re_path(r'ws/notifications/$', consumers.NotificationConsumer.as_asgi()),

    # Testing
    re_path(r'ws/test-echo/$', consumers.TestEchoConsumer.as_asgi()),
]
```

---

## Usage

### JavaScript Client

```javascript
// Connect to WebSocket
const socket = new WebSocket('ws://localhost:8000/ws/dashboard/');

socket.onopen = function(e) {
    console.log('Connected to dashboard');
};

socket.onmessage = function(event) {
    const data = JSON.parse(event.data);
    console.log('Received:', data);

    switch(data.type) {
        case 'system_status':
            updateSystemStatus(data);
            break;
        case 'agent_activity':
            updateAgentActivity(data);
            break;
    }
};

socket.onclose = function(event) {
    console.log('Connection closed');
    // Implement reconnection logic
};

// Send message
socket.send(JSON.stringify({
    'action': 'subscribe',
    'channel': 'agents'
}));
```

### Python - Send from Backend

```python
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

channel_layer = get_channel_layer()

# Send to group
async_to_sync(channel_layer.group_send)(
    'dashboard_updates',
    {
        'type': 'dashboard_update',
        'data': {
            'metric': 'agent_count',
            'value': 71
        }
    }
)
```

### Python - In Celery Task

```python
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

@shared_task
def notify_agent_progress(agent_name, progress):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        'agents_general',
        {
            'type': 'agent_progress',
            'agent': agent_name,
            'progress': progress,
            'status': 'running'
        }
    )
```

---

## Configuration

### settings.py

```python
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [('127.0.0.1', 6379)],
        },
    },
}
```

### asgi.py

```python
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from core.routing import websocket_urlpatterns

application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    'websocket': AuthMiddlewareStack(
        URLRouter(websocket_urlpatterns)
    ),
})
```

---

## SafeWebSocketMixin

All consumers use `SafeWebSocketMixin` for error handling:

```python
class SafeWebSocketMixin:
    """Mixin for safe WebSocket send operations"""

    async def safe_send(self, data):
        """Safely send data, handling closed connections"""
        try:
            await self.send(text_data=json.dumps(data))
        except Exception as e:
            logger.error(f"[SafeWebSocket] Failed to send: {e}")
            if "connection" not in str(e).lower():
                raise
```

---

## Testing WebSockets

```bash
# Using websocat
websocat ws://localhost:8000/ws/test-echo/

# Send test message
{"action": "echo", "message": "hello"}
```

---

## Related Documentation

- [VIEWS.md](VIEWS.md) - HTTP views
- [API_ENDPOINTS.md](API_ENDPOINTS.md) - REST API
- [INFRASTRUCTURE.md](INFRASTRUCTURE.md) - Middleware and routing

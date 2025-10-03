# HIGH PRIORITY ISSUE: WebSocket Routing Failures

## Status: ❌ NOT ADDRESSED

## Issue Description
Memory timeline WebSocket route is missing, breaking real-time updates

## The Problem
- **Frontend trying to connect**: `ws://localhost:8001/ws/memory/2/`
- **Backend response**: Route not found
- **Result**: No real-time memory updates

## Impact
- **Memory Timeline**: No live updates
- **User Experience**: Must refresh to see new memories
- **Real-time Features**: Broken for memory system

## Missing WebSocket Consumer
```python
# Need to create memory consumer
# backend/shared_memory/consumers.py (doesn't exist)

from channels.generic.websocket import AsyncJsonWebsocketConsumer

class MemoryConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.user_id = self.scope['url_route']['kwargs']['user_id']
        self.group_name = f'memory_{self.user_id}'
        
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )
        await self.accept()
    
    async def receive_json(self, content):
        # Handle incoming messages
        pass
    
    async def memory_update(self, event):
        # Send memory updates to client
        await self.send_json(event['data'])
```

## Missing Routing Configuration
```python
# backend/shared_memory/routing.py (doesn't exist)
from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/memory/<int:user_id>/', consumers.MemoryConsumer.as_asgi()),
]
```

## Update Main Routing
```python
# backend/server/routing.py or asgi.py
from shared_memory.routing import websocket_urlpatterns as memory_ws

websocket_urlpatterns = [
    # ... existing routes ...
] + memory_ws
```

## Frontend WebSocket Connection
```typescript
// Current (might be correct if backend fixed)
const ws = new WebSocket(`ws://localhost:8001/ws/memory/${userId}/`);

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    // Update memory timeline
    updateMemoryTimeline(data);
};
```

## Required Actions
1. Create MemoryConsumer class
2. Create routing configuration
3. Update main ASGI routing
4. Test WebSocket connection
5. Implement memory update broadcasting

## Testing
```bash
# Test WebSocket connection
wscat -c ws://localhost:8001/ws/memory/2/

# Should connect successfully
# Should receive updates when memories change
```

## Related Issues
- May need authentication for WebSocket
- Need to broadcast updates when memories created/updated
- Consider using Redis channel layer for scaling
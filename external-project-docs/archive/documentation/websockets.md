# WebSocket API Documentation

The Donkey Betz platform provides real-time updates through WebSocket connections for various features including agent activity monitoring, stock price streaming, and chat notifications.

## Table of Contents
1. [Overview](#overview)
2. [Connection Setup](#connection-setup)
3. [Authentication](#authentication)
4. [Available Endpoints](#available-endpoints)
5. [Message Formats](#message-formats)
6. [Client Libraries](#client-libraries)
7. [Error Handling](#error-handling)
8. [Best Practices](#best-practices)

## Overview

### WebSocket Benefits
- **Real-time Updates**: Instant push notifications without polling
- **Bi-directional Communication**: Send and receive messages
- **Lower Overhead**: More efficient than HTTP polling
- **Persistent Connection**: Maintains state between messages

### Base URLs
```
Development: ws://localhost:8000/ws/
Production: wss://api.donkeybetz.com/ws/
```

## Connection Setup

### Basic Connection
```javascript
// JavaScript
const ws = new WebSocket('wss://api.donkeybetz.com/ws/agent-activity/');

ws.onopen = () => {
  console.log('Connected to WebSocket');
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Received:', data);
};

ws.onerror = (error) => {
  console.error('WebSocket error:', error);
};

ws.onclose = () => {
  console.log('WebSocket connection closed');
};
```

## Authentication

WebSocket connections require authentication via JWT token. There are two methods:

### Method 1: Query Parameter (Recommended)
```javascript
const token = 'your-jwt-token';
const ws = new WebSocket(`wss://api.donkeybetz.com/ws/agent-activity/?token=${token}`);
```

### Method 2: First Message Authentication
```javascript
const ws = new WebSocket('wss://api.donkeybetz.com/ws/agent-activity/');

ws.onopen = () => {
  // Send auth message immediately after connection
  ws.send(JSON.stringify({
    type: 'auth',
    token: 'your-jwt-token'
  }));
};
```

## Available Endpoints

### 1. Agent Activity Monitoring
Monitor real-time progress of AI agent orchestrations.

**Endpoint**: `/ws/agent-activity/{orchestration_id}/`

**Incoming Messages**:
```json
{
  "type": "agent_started",
  "agent_id": "123e4567-e89b-12d3-a456-426614174000",
  "agent_name": "Business Strategy Agent",
  "orchestration_id": "orch_123456",
  "timestamp": "2025-01-15T10:30:00Z"
}

{
  "type": "agent_progress",
  "agent_id": "123e4567-e89b-12d3-a456-426614174000",
  "progress": 45,
  "message": "Analyzing market trends...",
  "current_step": 3,
  "total_steps": 7
}

{
  "type": "agent_completed",
  "agent_id": "123e4567-e89b-12d3-a456-426614174000",
  "result": {
    "summary": "Analysis complete",
    "key_findings": ["Finding 1", "Finding 2"],
    "recommendations": ["Recommendation 1", "Recommendation 2"]
  }
}

{
  "type": "orchestration_completed",
  "orchestration_id": "orch_123456",
  "overall_status": "completed",
  "duration_seconds": 125,
  "agents_used": 5
}
```

### 2. Stock Price Streaming
Real-time stock price updates powered by Polygon.io.

**Endpoint**: `/ws/stocks/{ticker}/`

**Incoming Messages**:
```json
{
  "type": "price_update",
  "ticker": "AAPL",
  "price": 182.45,
  "change": 2.15,
  "change_percent": 1.19,
  "volume": 58234100,
  "timestamp": "2025-01-15T10:30:45Z"
}

{
  "type": "trade",
  "ticker": "AAPL",
  "price": 182.47,
  "size": 100,
  "conditions": ["regular"],
  "timestamp": "2025-01-15T10:30:45.123Z"
}

{
  "type": "quote",
  "ticker": "AAPL",
  "bid": 182.44,
  "bid_size": 300,
  "ask": 182.46,
  "ask_size": 500,
  "timestamp": "2025-01-15T10:30:45.456Z"
}
```

**Outgoing Messages**:
```json
// Subscribe to additional tickers
{
  "type": "subscribe",
  "tickers": ["GOOGL", "MSFT", "TSLA"]
}

// Unsubscribe from tickers
{
  "type": "unsubscribe",
  "tickers": ["TSLA"]
}
```

### 3. Chat Notifications
Real-time notifications for AI chat responses and updates.

**Endpoint**: `/ws/chat/{conversation_id}/`

**Incoming Messages**:
```json
{
  "type": "ai_response",
  "message": "Based on your recent searches...",
  "conversation_id": "conv_123456",
  "message_id": "msg_789",
  "timestamp": "2025-01-15T10:30:00Z"
}

{
  "type": "typing_indicator",
  "is_typing": true
}

{
  "type": "memory_added",
  "memory_id": "mem_456",
  "content": "User discussed product launch timeline",
  "category": "business_planning"
}
```

### 4. Reddit Scout Updates
Real-time updates from Reddit Scout agents.

**Endpoint**: `/ws/reddit-scout/{scout_id}/`

**Incoming Messages**:
```json
{
  "type": "idea_found",
  "idea": {
    "id": "idea_123",
    "title": "AI tool for automatic video editing",
    "subreddit": "startups",
    "score": 156,
    "url": "https://reddit.com/r/startups/...",
    "pain_point": "Video editing is time-consuming",
    "potential_solution": "AI-powered editing assistant"
  }
}

{
  "type": "scout_progress",
  "subreddits_scanned": 5,
  "total_subreddits": 10,
  "ideas_found": 23
}
```

### 5. Business Builder Progress
Track business generation progress in real-time.

**Endpoint**: `/ws/business-builder/{task_id}/`

**Incoming Messages**:
```json
{
  "type": "generation_progress",
  "stage": "creating_backend",
  "progress": 35,
  "message": "Setting up API endpoints...",
  "estimated_time_remaining": 120
}

{
  "type": "file_created",
  "filename": "app.py",
  "path": "/backend/app.py",
  "size_bytes": 4521
}

{
  "type": "generation_complete",
  "business_id": "biz_789",
  "download_url": "/api/universal-builder/businesses/biz_789/download/",
  "total_files": 47,
  "total_size_mb": 2.3
}
```

### 6. Global Activity Feed
Monitor all platform activity for the authenticated user.

**Endpoint**: `/ws/activity/`

**Incoming Messages**:
```json
{
  "type": "activity",
  "category": "agent_completed",
  "title": "Stock Analysis Complete",
  "description": "AAPL analysis finished with buy recommendation",
  "link": "/orchestrations/orch_123",
  "timestamp": "2025-01-15T10:30:00Z"
}
```

## Message Formats

### Standard Message Structure
All WebSocket messages follow this structure:
```json
{
  "type": "message_type",
  "timestamp": "ISO 8601 timestamp",
  "data": {
    // Message-specific data
  }
}
```

### Error Messages
```json
{
  "type": "error",
  "error_code": "INVALID_TICKER",
  "message": "Invalid stock ticker symbol",
  "details": {
    "ticker": "INVALID",
    "valid_format": "1-5 uppercase letters"
  }
}
```

## Client Libraries

### JavaScript/TypeScript
```typescript
class DonkeyBetzWebSocket {
  private ws: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000;
  private heartbeatInterval: number | null = null;
  
  constructor(
    private endpoint: string,
    private token: string,
    private handlers: {
      onMessage?: (data: any) => void;
      onError?: (error: any) => void;
      onClose?: () => void;
      onOpen?: () => void;
    }
  ) {}
  
  connect() {
    const url = `wss://api.donkeybetz.com/ws/${this.endpoint}/?token=${this.token}`;
    this.ws = new WebSocket(url);
    
    this.ws.onopen = () => {
      console.log('WebSocket connected');
      this.reconnectAttempts = 0;
      this.startHeartbeat();
      this.handlers.onOpen?.();
    };
    
    this.ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      this.handlers.onMessage?.(data);
    };
    
    this.ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      this.handlers.onError?.(error);
    };
    
    this.ws.onclose = () => {
      console.log('WebSocket closed');
      this.stopHeartbeat();
      this.handlers.onClose?.();
      this.attemptReconnect();
    };
  }
  
  private attemptReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);
      console.log(`Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts})`);
      
      setTimeout(() => this.connect(), delay);
    }
  }
  
  private startHeartbeat() {
    this.heartbeatInterval = window.setInterval(() => {
      if (this.ws?.readyState === WebSocket.OPEN) {
        this.ws.send(JSON.stringify({ type: 'ping' }));
      }
    }, 30000); // Every 30 seconds
  }
  
  private stopHeartbeat() {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval);
      this.heartbeatInterval = null;
    }
  }
  
  send(data: any) {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data));
    } else {
      console.error('WebSocket not connected');
    }
  }
  
  close() {
    this.stopHeartbeat();
    this.ws?.close();
  }
}

// Usage
const agentWs = new DonkeyBetzWebSocket(
  'agent-activity/orch_123',
  'your-token',
  {
    onMessage: (data) => {
      if (data.type === 'agent_progress') {
        updateProgressBar(data.progress);
      }
    },
    onError: (error) => {
      showErrorNotification('Connection error');
    }
  }
);

agentWs.connect();
```

### Python (asyncio)
```python
import asyncio
import json
import websockets
from typing import Optional, Callable, Dict, Any


class DonkeyBetzWebSocket:
    def __init__(
        self,
        endpoint: str,
        token: str,
        base_url: str = "wss://api.donkeybetz.com"
    ):
        self.endpoint = endpoint
        self.token = token
        self.base_url = base_url
        self.ws: Optional[websockets.WebSocketClientProtocol] = None
        self.running = False
        
    async def connect(self):
        """Establish WebSocket connection"""
        url = f"{self.base_url}/ws/{self.endpoint}/?token={self.token}"
        self.ws = await websockets.connect(url)
        self.running = True
        
    async def disconnect(self):
        """Close WebSocket connection"""
        self.running = False
        if self.ws:
            await self.ws.close()
            
    async def send(self, data: Dict[str, Any]):
        """Send message to server"""
        if self.ws:
            await self.ws.send(json.dumps(data))
            
    async def receive(self) -> Dict[str, Any]:
        """Receive and parse message from server"""
        if self.ws:
            message = await self.ws.recv()
            return json.loads(message)
        return {}
        
    async def listen(self, message_handler: Callable[[Dict[str, Any]], None]):
        """Listen for messages and handle them"""
        try:
            await self.connect()
            
            while self.running:
                try:
                    message = await self.receive()
                    await message_handler(message)
                except websockets.exceptions.ConnectionClosed:
                    print("Connection closed")
                    break
                except Exception as e:
                    print(f"Error: {e}")
                    
        finally:
            await self.disconnect()


# Usage example
async def handle_agent_message(message: Dict[str, Any]):
    if message['type'] == 'agent_progress':
        print(f"Progress: {message['progress']}% - {message['message']}")
    elif message['type'] == 'agent_completed':
        print(f"Agent completed: {message['result']}")


async def monitor_orchestration(orchestration_id: str, token: str):
    ws = DonkeyBetzWebSocket(f"agent-activity/{orchestration_id}", token)
    await ws.listen(handle_agent_message)


# Run the monitor
asyncio.run(monitor_orchestration("orch_123", "your-token"))
```

## Error Handling

### Connection Errors
```javascript
ws.onerror = (error) => {
  console.error('WebSocket error:', error);
  
  // Attempt to reconnect with exponential backoff
  let reconnectDelay = 1000;
  const maxDelay = 30000;
  
  function reconnect() {
    setTimeout(() => {
      console.log('Attempting to reconnect...');
      const newWs = new WebSocket(wsUrl);
      
      newWs.onerror = () => {
        reconnectDelay = Math.min(reconnectDelay * 2, maxDelay);
        reconnect();
      };
      
      newWs.onopen = () => {
        console.log('Reconnected successfully');
        reconnectDelay = 1000;
        // Re-attach handlers
      };
    }, reconnectDelay);
  }
  
  reconnect();
};
```

### Authentication Errors
```json
{
  "type": "auth_error",
  "error_code": "INVALID_TOKEN",
  "message": "Authentication token is invalid or expired"
}
```

Handle by refreshing the JWT token and reconnecting:
```javascript
if (message.type === 'auth_error') {
  // Refresh token
  const newToken = await refreshAccessToken();
  
  // Reconnect with new token
  ws.close();
  connectWithNewToken(newToken);
}
```

## Best Practices

### 1. Connection Management
- Implement automatic reconnection with exponential backoff
- Use heartbeat/ping messages to detect stale connections
- Close connections when not in use to save resources

### 2. Message Handling
- Always validate message structure before processing
- Use message queuing for critical messages during reconnection
- Implement idempotent message handling

### 3. Resource Management
```javascript
// Clean up on page unload
window.addEventListener('beforeunload', () => {
  ws.close();
});

// Reconnect on page visibility change
document.addEventListener('visibilitychange', () => {
  if (!document.hidden && ws.readyState !== WebSocket.OPEN) {
    reconnect();
  }
});
```

### 4. Security
- Never send sensitive data over non-TLS WebSocket connections
- Validate all incoming messages
- Implement rate limiting on client side to prevent spam

### 5. Monitoring
```javascript
// Track connection metrics
const metrics = {
  connectTime: null,
  messageCount: 0,
  errorCount: 0,
  reconnectCount: 0
};

ws.onopen = () => {
  metrics.connectTime = Date.now();
};

ws.onmessage = () => {
  metrics.messageCount++;
};

ws.onerror = () => {
  metrics.errorCount++;
};
```

## Testing WebSocket Connections

### Browser Console
```javascript
// Quick test in browser console
const ws = new WebSocket('wss://api.donkeybetz.com/ws/stocks/AAPL/?token=YOUR_TOKEN');
ws.onmessage = (e) => console.log(JSON.parse(e.data));
```

### Command Line (wscat)
```bash
# Install wscat
npm install -g wscat

# Connect to WebSocket
wscat -c "wss://api.donkeybetz.com/ws/stocks/AAPL/" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Python Script
```python
import asyncio
import websockets

async def test_connection():
    uri = "wss://api.donkeybetz.com/ws/stocks/AAPL/?token=YOUR_TOKEN"
    async with websockets.connect(uri) as ws:
        # Receive messages for 30 seconds
        for _ in range(30):
            message = await ws.recv()
            print(message)
            await asyncio.sleep(1)

asyncio.run(test_connection())
```
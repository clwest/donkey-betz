# WebSocket Integration Guide
## Unified Donkey Betz Platform

### 🚀 Overview

The Unified Donkey Betz Platform provides comprehensive WebSocket support for real-time communication across all platform components:

- **Sports Analytics**: Live odds updates, arbitrage alerts, betting recommendations
- **Agent Orchestration**: Real-time agent execution status and progress tracking  
- **Content Management**: Live content generation and processing updates
- **System Monitoring**: Real-time platform health and analytics

---

## ✅ WebSocket Infrastructure Status

**ALL SYSTEMS OPERATIONAL** ✅

- **Django Channels**: Configured and running
- **Daphne ASGI Server**: Running on port 8000
- **Redis Channel Layer**: Connected and functional
- **Authentication Middleware**: Active on all protected endpoints
- **Connection Management**: Supporting multiple concurrent connections
- **Real-time Messaging**: Verified with ping/pong heartbeat

---

## 🔌 Available WebSocket Endpoints

### Testing Endpoints
```
ws://localhost:8000/ws/test/echo/
```
- **Purpose**: Basic connectivity testing (no authentication required)
- **Features**: Echo messages, ping/pong, error handling

### Content Management WebSockets
```
ws://localhost:8000/ws/content/processing/     # Content processing updates
ws://localhost:8000/ws/content/analytics/      # Content analytics dashboard
```

### Agent System WebSockets
```
ws://localhost:8000/ws/agents/execution/       # Agent execution tracking
ws://localhost:8000/ws/agents/orchestration/   # Multi-agent orchestration
```

### Sports Analytics WebSockets
```
ws://localhost:8000/ws/sports/games/<game_id>/           # Live game updates
ws://localhost:8000/ws/sports/odds/market/<market_id>/   # Market-specific odds
ws://localhost:8000/ws/sports/odds/game/<game_id>/       # Game-wide odds
ws://localhost:8000/ws/sports/arbitrage/                 # Arbitrage alerts
ws://localhost:8000/ws/sports/recommendations/           # Betting recommendations
ws://localhost:8000/ws/sports/dashboard/                 # Sports dashboard
```

---

## 🔐 Authentication

All production endpoints require user authentication. WebSocket connections will receive HTTP 403 if not properly authenticated.

### Authentication Methods
1. **Session Authentication**: Use Django session cookies
2. **Token Authentication**: Pass token in WebSocket headers
3. **JWT Authentication**: Include JWT token in connection

---

## 📡 Message Protocol

All WebSocket messages use JSON format:

### Standard Message Structure
```json
{
  "type": "message_type",
  "data": {},
  "timestamp": "2023-XX-XX XX:XX:XX"
}
```

### Common Message Types

#### Client to Server
- `ping` - Heartbeat message
- `subscribe_*` - Subscribe to specific updates
- `unsubscribe_*` - Unsubscribe from updates
- `get_status` - Request current status

#### Server to Client
- `pong` - Heartbeat response
- `initial_data` - Initial connection data
- `*_update` - Real-time updates
- `error` - Error messages
- `status` - Status responses

---

## 🏗️ Frontend Implementation Examples

### Basic Connection (JavaScript)
```javascript
class UnifiedWebSocket {
  constructor(endpoint, options = {}) {
    this.endpoint = endpoint;
    this.websocket = null;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = options.maxReconnectAttempts || 5;
    this.reconnectDelay = options.reconnectDelay || 1000;
  }

  connect() {
    try {
      this.websocket = new WebSocket(this.endpoint);
      
      this.websocket.onopen = (event) => {
        console.log('WebSocket connected:', this.endpoint);
        this.reconnectAttempts = 0;
        this.setupHeartbeat();
      };

      this.websocket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        this.handleMessage(data);
      };

      this.websocket.onclose = (event) => {
        console.log('WebSocket closed:', event.code, event.reason);
        this.handleReconnection();
      };

      this.websocket.onerror = (error) => {
        console.error('WebSocket error:', error);
      };

    } catch (error) {
      console.error('Failed to create WebSocket:', error);
    }
  }

  handleMessage(data) {
    switch(data.type) {
      case 'pong':
        // Heartbeat response
        break;
      case 'initial_data':
        this.onInitialData(data);
        break;
      case 'execution_started':
      case 'execution_progress':
      case 'execution_completed':
        this.onAgentUpdate(data);
        break;
      case 'odds_update':
      case 'arbitrage_alert':
        this.onSportsUpdate(data);
        break;
      case 'error':
        this.onError(data);
        break;
      default:
        console.warn('Unknown message type:', data.type);
    }
  }

  setupHeartbeat() {
    setInterval(() => {
      if (this.websocket.readyState === WebSocket.OPEN) {
        this.send({ type: 'ping', timestamp: new Date().toISOString() });
      }
    }, 30000); // 30 seconds
  }

  handleReconnection() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);
      
      console.log(`Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts})`);
      setTimeout(() => this.connect(), delay);
    } else {
      console.error('Max reconnection attempts reached');
    }
  }

  send(data) {
    if (this.websocket.readyState === WebSocket.OPEN) {
      this.websocket.send(JSON.stringify(data));
    }
  }

  // Override these methods in your implementation
  onInitialData(data) {}
  onAgentUpdate(data) {}
  onSportsUpdate(data) {}
  onError(data) {}
}
```

### React Hook Example
```javascript
import { useState, useEffect, useCallback } from 'react';

export const useWebSocket = (endpoint, options = {}) => {
  const [socket, setSocket] = useState(null);
  const [isConnected, setIsConnected] = useState(false);
  const [messages, setMessages] = useState([]);

  const connect = useCallback(() => {
    const ws = new UnifiedWebSocket(endpoint, options);
    
    ws.onInitialData = (data) => {
      setMessages(prev => [...prev, data]);
    };
    
    ws.onAgentUpdate = (data) => {
      setMessages(prev => [...prev, data]);
    };
    
    ws.onSportsUpdate = (data) => {
      setMessages(prev => [...prev, data]);
    };

    ws.websocket.onopen = () => setIsConnected(true);
    ws.websocket.onclose = () => setIsConnected(false);
    
    ws.connect();
    setSocket(ws);
  }, [endpoint]);

  useEffect(() => {
    connect();
    return () => {
      if (socket?.websocket) {
        socket.websocket.close();
      }
    };
  }, [connect]);

  const sendMessage = useCallback((message) => {
    if (socket) {
      socket.send(message);
    }
  }, [socket]);

  return { isConnected, messages, sendMessage };
};
```

---

## 🔄 Connection Management Best Practices

### 1. Exponential Backoff Reconnection
```javascript
const reconnectDelays = [1000, 2000, 4000, 8000, 16000]; // ms
```

### 2. Heartbeat/Ping-Pong
```javascript
// Send ping every 30 seconds
setInterval(() => {
  ws.send(JSON.stringify({ type: 'ping' }));
}, 30000);
```

### 3. Connection State Management
```javascript
const ConnectionState = {
  CONNECTING: 'connecting',
  OPEN: 'open',
  CLOSING: 'closing',
  CLOSED: 'closed',
  ERROR: 'error'
};
```

### 4. Message Queue for Offline Messages
```javascript
class MessageQueue {
  constructor() {
    this.queue = [];
  }
  
  add(message) {
    this.queue.push(message);
  }
  
  flush(websocket) {
    while (this.queue.length > 0) {
      const message = this.queue.shift();
      websocket.send(JSON.stringify(message));
    }
  }
}
```

---

## 📊 Real-Time Use Cases

### Sports Analytics Dashboard
- **Live odds updates** across multiple sportsbooks
- **Arbitrage opportunity alerts** with profit calculations
- **Line movement notifications** for significant changes
- **Game status updates** with live scores

### Agent Execution Monitoring
- **Real-time progress tracking** for agent executions
- **Live log streaming** from running agents
- **Orchestration status** for multi-agent workflows
- **Performance metrics** and resource usage

### Content Generation
- **Live content processing** status updates
- **Generation progress** with token usage tracking
- **Workflow execution** step-by-step updates
- **Quality metrics** and completion notifications

---

## 🛠️ Development Tools

### Testing WebSocket Connections
```bash
# Run comprehensive test suite
python test_websocket_comprehensive.py

# Test basic connectivity
python test_websocket.py

# Start Daphne server
daphne -b 0.0.0.0 -p 8000 core.asgi:application
```

### Redis Channel Layer Monitoring
```bash
redis-cli monitor  # Monitor Redis commands
redis-cli info     # Redis server info
```

---

## 🚨 Error Handling

### Common Error Codes
- **HTTP 403**: Authentication required
- **HTTP 404**: Endpoint not found
- **1006**: Abnormal closure (check server logs)
- **1000**: Normal closure

### Error Message Format
```json
{
  "type": "error",
  "error_code": "authentication_required",
  "message": "WebSocket connection requires authentication",
  "timestamp": "2023-XX-XX XX:XX:XX"
}
```

---

## 📈 Performance Considerations

### Connection Limits
- **Current**: 5+ concurrent connections tested
- **Recommended**: Implement connection pooling for high-traffic scenarios
- **Monitor**: Connection count and Redis memory usage

### Message Throughput
- **Tested**: Multiple rapid messages handled correctly
- **Recommended**: Implement message throttling for high-frequency updates
- **Monitor**: Message queue sizes and processing latency

---

## 🔧 Configuration

### Environment Variables
```bash
# Redis Configuration
REDIS_URL=redis://localhost:6379
REDIS_CHANNELS_URL=redis://localhost:6379/3

# WebSocket Settings
WEBSOCKET_URL=ws://localhost:8000
CORS_ALLOWED_ORIGINS=http://localhost:3000

# Channel Layer Settings
CHANNEL_LAYERS_CAPACITY=300
CHANNEL_LAYERS_EXPIRY=60
```

### Django Settings
```python
# ASGI Configuration
ASGI_APPLICATION = 'core.asgi.application'

# Channel Layers
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [('localhost', 6379)],
            'capacity': 300,
            'expiry': 60,
        },
    },
}
```

---

## 📞 Support & Troubleshooting

### Common Issues

1. **Connection Refused**: Check if Daphne server is running
2. **HTTP 403**: Verify authentication credentials
3. **Redis Connection**: Ensure Redis server is running
4. **CORS Issues**: Check CORS_ALLOWED_ORIGINS setting

### Debug Commands
```bash
# Check Daphne process
lsof -i :8000

# Check Redis connectivity
redis-cli ping

# View Django logs
tail -f logs/unified_platform.log
```

---

*WebSocket infrastructure successfully configured and tested for the Unified Donkey Betz Platform* ✅
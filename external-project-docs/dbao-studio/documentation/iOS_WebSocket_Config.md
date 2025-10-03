# iOS WebSocket Connection Configuration Guide

## Issues Identified and Resolved

### 1. ✅ FIXED: Consumer Error Handling
- **Issue**: `AgentExecutionConsumer.connect()` had insufficient error handling
- **Fix**: Added comprehensive try-catch blocks and proper logging
- **Result**: WebSocket connections now handle errors gracefully instead of closing with code 1000

### 2. ⚠️ CRITICAL: Port Mismatch
- **Issue**: iOS app connecting to port `8001`, Django server running on port `8000`
- **Fix Required**: Update iOS app configuration

### 3. ⚠️ CRITICAL: iOS Localhost Issue
- **Issue**: iOS devices/simulators cannot connect to `localhost`
- **Fix Required**: Use actual IP address

## Required iOS App Changes

### Update Connection URLs

**Current (Incorrect):**
```javascript
// iOS React Native app
const API_URL = "http://localhost:8001/api"
const WS_URL = "ws://localhost:8001/ws/assistant/"
```

**Fixed (Correct):**
```javascript
// iOS React Native app
const API_URL = "http://10.0.0.108:8000/api"           // Use your machine's IP
const WS_URL = "ws://10.0.0.108:8000/ws/assistant/"    // Use your machine's IP
```

### WebSocket Connection Code Example

```javascript
// Recommended WebSocket connection with proper error handling
const connectWebSocket = () => {
  const ws = new WebSocket('ws://10.0.0.108:8000/ws/assistant/', [], {
    headers: {
      'Authorization': `Token ${authToken}`, // If using authentication
    }
  });

  ws.onopen = () => {
    console.log('WebSocket connected');
    // Send ping to test connection
    ws.send(JSON.stringify({
      type: 'ping',
      timestamp: new Date().toISOString()
    }));
  };

  ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    console.log('WebSocket message:', data);
    
    if (data.type === 'connection') {
      console.log('Connection established:', data.message);
    }
  };

  ws.onclose = (event) => {
    console.log(`WebSocket closed: ${event.code} - ${event.reason}`);
    
    // Implement reconnection logic
    if (event.code !== 1000) { // Not a normal closure
      setTimeout(connectWebSocket, 3000); // Retry after 3 seconds
    }
  };

  ws.onerror = (error) => {
    console.error('WebSocket error:', error);
  };

  return ws;
};
```

## Testing Commands

### 1. Test from iOS Simulator Terminal
```bash
# Test basic connectivity
curl -I http://10.0.0.108:8000/api/

# Test WebSocket upgrade (should return 426 - Upgrade Required)
curl -H "Upgrade: websocket" -H "Connection: upgrade" http://10.0.0.108:8000/ws/assistant/
```

### 2. Test with wscat (if installed)
```bash
# Install wscat
npm install -g wscat

# Test WebSocket connection
wscat -c ws://10.0.0.108:8000/ws/assistant/
```

### 3. Test Direct WebSocket Connection
Use this JavaScript code in Safari on your iOS device:

```javascript
// Open Safari on iOS device and go to any website
// Open developer console and run:
const ws = new WebSocket('ws://10.0.0.108:8000/ws/assistant/');
ws.onopen = () => console.log('Connected!');
ws.onmessage = (e) => console.log('Message:', e.data);
ws.onclose = (e) => console.log('Closed:', e.code, e.reason);
```

## Server Verification

### Check Server Status
```bash
# Check if server is running
ps aux | grep daphne

# Check port binding
lsof -i :8000

# Test WebSocket route
curl -H "Upgrade: websocket" -H "Connection: upgrade" http://localhost:8000/ws/assistant/
```

### Enable Logging
Add this to your Django settings for debugging:

```python
# In settings.py
LOGGING = {
    'version': 1,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'api.websocket_consumers': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}
```

## Network Configuration

### Allow External Connections
Make sure your Django server allows external connections:

```bash
# Start server to accept external connections
cd backend
python manage.py runserver 0.0.0.0:8000
```

### Firewall (if needed)
```bash
# macOS - Allow incoming connections on port 8000
sudo pfctl -f /dev/stdin <<< "pass in proto tcp from any to any port 8000"
```

## Common iOS WebSocket Issues

### 1. App Transport Security (iOS 9+)
Add to your iOS app's `Info.plist`:

```xml
<key>NSAppTransportSecurity</key>
<dict>
    <key>NSAllowsArbitraryLoads</key>
    <true/>
    <!-- Or more specific: -->
    <key>NSExceptionDomains</key>
    <dict>
        <key>10.0.0.108</key>
        <dict>
            <key>NSExceptionAllowsInsecureHTTPLoads</key>
            <true/>
        </dict>
    </dict>
</dict>
```

### 2. Background App Refresh
Ensure your app handles WebSocket reconnection when returning from background:

```javascript
// React Native
import { AppState } from 'react-native';

AppState.addEventListener('change', (nextAppState) => {
  if (nextAppState === 'active') {
    // Reconnect WebSocket when app becomes active
    reconnectWebSocket();
  }
});
```

## Expected Connection Flow

1. **Initial Connection**: WebSocket connects successfully
2. **Authentication**: Server checks for auth token (optional)
3. **Connection Message**: Server sends connection confirmation
4. **Ping/Pong**: Regular heartbeat messages
5. **Data Exchange**: Application-specific messages

## Error Codes Reference

- **1000**: Normal closure (should not occur immediately after connect)
- **1001**: Going away (server shutting down)
- **1006**: Abnormal closure (network issues, consumer crash)
- **1011**: Server error (internal server error)
- **4001**: Authentication required (custom code)

Your WebSocket consumer is now fixed and should maintain stable connections!
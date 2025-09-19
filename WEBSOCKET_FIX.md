# 🔌 WEBSOCKET FIX FOR UNIFIED DONKEY BETZ

## The Problem
When using `make unified-dev`, WebSockets don't initialize properly without a hard refresh because:
1. Frontend starts before backend is fully ready
2. WebSocket connections attempt to connect too early
3. Failed connections don't retry properly

## The Solution

### 1. Smart Startup Script
Use the new smart startup script instead of `make unified-dev`:
```bash
chmod +x start_smart.sh
./start_smart.sh
```

This script:
- Ensures backend is ready before starting frontend
- Uses Daphne if available (full WebSocket support)
- Waits for health check before proceeding

### 2. WebSocket Manager with Auto-Reconnect
Created `frontend/src/services/websocket-manager.ts` with:
- Automatic reconnection with exponential backoff
- Message queuing when disconnected
- Health check before connecting
- Heartbeat to keep connections alive

### 3. React Hook for WebSocket
Created `frontend/src/hooks/useWebSocket.tsx` with:
- `useWebSocket` hook for components
- `useBackendHealth` hook to check backend status
- Automatic retry logic
- Clean disconnection handling

### 4. WebSocket Initializer Component
Created `frontend/src/components/WebSocketInitializer.tsx`:
- Wraps your app to ensure WebSockets connect properly
- Shows loading state while connecting
- Handles errors gracefully
- Auto-reconnects on tab visibility change

## How to Integrate

### Step 1: Update your main App component

```tsx
// frontend/src/App.tsx or main.tsx
import { WebSocketInitializer } from './components/WebSocketInitializer';

function App() {
  return (
    <WebSocketInitializer showStatus={true}>
      {/* Your existing app content */}
      <YourAppContent />
    </WebSocketInitializer>
  );
}
```

### Step 2: Use the WebSocket hook in components

```tsx
// In any component that needs WebSocket
import { useWebSocket } from '../hooks/useWebSocket';

function DashboardComponent() {
  const ws = useWebSocket({
    endpoint: 'dashboard',
    onMessage: (data) => {
      console.log('Received:', data);
      // Handle the message
    },
    messageTypes: ['update', 'notification']
  });

  const handleSendMessage = () => {
    ws.sendMessage('request_data', { type: 'all' });
  };

  if (!ws.isConnected) {
    return <div>Connecting...</div>;
  }

  return (
    <div>
      <button onClick={handleSendMessage}>Send Message</button>
      {/* Your component UI */}
    </div>
  );
}
```

### Step 3: Add status indicator (optional)

```tsx
// In your layout or header
import { WebSocketStatusIndicator } from './components/WebSocketInitializer';

function Layout() {
  return (
    <div>
      <Header />
      <MainContent />
      <WebSocketStatusIndicator /> {/* Shows connection status */}
    </div>
  );
}
```

## Backend Health Check

The solution includes a health check endpoint that the frontend uses to verify the backend is ready:

**Endpoint:** `GET http://localhost:8000/api/v1/health/`

**Response:**
```json
{
  "status": "healthy",
  "services": {
    "database": "ok",
    "redis": "ok",
    "websocket": "ok"
  },
  "websocket_ready": true
}
```

## Testing WebSocket Connection

Run the test script to verify WebSockets are working:
```bash
python test_websocket_fixed.py
```

## Alternative: Using Original Makefile

If you prefer to keep using `make unified-dev`, the WebSocket components will still help by:
- Auto-reconnecting when backend becomes available
- Showing loading state instead of errors
- Eliminating the need for hard refresh

But for best results, use the smart startup script.

## Key Improvements

1. **No More Hard Refresh Required** - WebSockets auto-connect when backend is ready
2. **Graceful Degradation** - Shows loading/error states instead of breaking
3. **Auto-Recovery** - Reconnects automatically after connection loss
4. **Better UX** - Users see clear status and can manually retry if needed
5. **Network Awareness** - Handles online/offline events
6. **Tab Visibility** - Reconnects when user returns to tab

## Troubleshooting

### WebSocket Still Not Connecting?

1. **Check if backend is using Daphne:**
   ```bash
   curl http://localhost:8000/api/v1/health/
   ```
   Look for `websocket_ready: true`

2. **Install Daphne if missing:**
   ```bash
   pip install daphne
   ```

3. **Use the smart startup script:**
   ```bash
   ./start_smart.sh
   ```

4. **Check browser console for errors:**
   - Open DevTools (F12)
   - Look for WebSocket connection errors
   - Check Network tab for failed WS connections

5. **Verify correct ports:**
   - Backend: http://localhost:8000
   - WebSocket: ws://localhost:8000/ws/
   - Frontend: http://localhost:3000

## Summary

The WebSocket initialization issue is now fixed with:
- Smart startup sequence ensuring proper timing
- Auto-reconnect logic in the frontend
- Health checks before attempting connections
- Graceful error handling and recovery

No more hard refreshes needed! The system handles connection timing automatically.

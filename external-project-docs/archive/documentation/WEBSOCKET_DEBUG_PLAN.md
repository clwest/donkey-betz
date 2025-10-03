# WebSocket Connection Loop Debug Plan

## Problem Description
Multiple WebSocket connections are being created rapidly to `/ws/stock-prices/` endpoint, creating a connection loop that floods the server with connections.

## Symptoms
- Rapid creation of new WebSocket connections (multiple per second)
- Each connection gets a new port number
- Server logs show continuous "User 3 connected to stock price WebSocket" messages
- Performance degradation due to resource exhaustion

## Potential Root Causes

### 1. Multiple Component Instances
- Multiple components using `useStockPrices` hook simultaneously
- Each component instance creates its own connection
- React re-renders causing hook to reinitialize

**Debug Steps:**
```javascript
// Add to useStockPrices hook
console.log('useStockPrices hook initialized', { 
  componentId: Math.random(), 
  timestamp: new Date().toISOString() 
});
```

### 2. React Strict Mode
- React Strict Mode intentionally double-renders components in development
- This could cause hooks to initialize twice

**Debug Steps:**
- Check if `<React.StrictMode>` is enabled in the app
- Temporarily disable it to test

### 3. WebSocket Manager State Issues
- The singleton pattern might not be working correctly
- Multiple WebSocketManager instances being created

**Debug Steps:**
```javascript
// Add to WebSocketManager constructor
console.log('WebSocketManager instance created', { 
  instanceId: Math.random(), 
  timestamp: new Date().toISOString() 
});
```

### 4. Frontend Routing/Navigation
- Route changes causing components to remount
- Navigation causing cleanup issues

**Debug Steps:**
- Log component mount/unmount lifecycle
- Check if navigation is triggering re-renders

### 5. Hot Module Replacement (HMR)
- Vite's HMR might be causing issues with WebSocket connections
- Module updates not properly cleaning up connections

**Debug Steps:**
- Test with HMR disabled
- Run production build to eliminate HMR issues

## Immediate Workarounds

### 1. Connection Throttling
Add a global connection limit:
```javascript
// In WebSocketManager
private static connectionCount = 0;
private static readonly MAX_CONNECTIONS = 3;

connect(...) {
  if (WebSocketManager.connectionCount >= WebSocketManager.MAX_CONNECTIONS) {
    console.error('Max WebSocket connections reached');
    return null;
  }
  // ... rest of connection logic
}
```

### 2. Debounce Connection Attempts
```javascript
// In useStockPrices
const connectDebounced = useMemo(
  () => debounce(connectToStockPrices, 1000),
  []
);
```

### 3. Global State Management
Move WebSocket connection to a global state manager (Redux/Zustand) to ensure single instance.

## Debug Information to Collect

1. **Component Tree Analysis**
   - Which components are using the hook?
   - How many times is each component rendering?

2. **Connection Lifecycle Logs**
   ```javascript
   // Add comprehensive logging
   console.trace('WebSocket connection initiated');
   ```

3. **Browser DevTools Network Tab**
   - Monitor WebSocket connections
   - Check for connection close reasons

4. **React DevTools Profiler**
   - Record re-renders
   - Identify components causing multiple renders

## Long-term Solutions

### 1. Centralized WebSocket Service
Create a single WebSocket service that all components subscribe to:
```typescript
class StockPriceService {
  private static instance: StockPriceService;
  private connection: WebSocket | null = null;
  private subscribers: Map<string, Set<(data: any) => void>> = new Map();
  
  static getInstance() {
    if (!StockPriceService.instance) {
      StockPriceService.instance = new StockPriceService();
    }
    return StockPriceService.instance;
  }
  
  subscribe(symbol: string, callback: (data: any) => void) {
    // Add subscriber
    // Connect if not connected
    // Return unsubscribe function
  }
}
```

### 2. Connection Pool Pattern
Implement a connection pool with proper lifecycle management.

### 3. Server-Side Rate Limiting
Add rate limiting on the backend to prevent connection spam:
```python
from django.core.cache import cache
from django.conf import settings

class StockPriceConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Rate limit check
        user_key = f"ws_connections_{self.scope['user'].id}"
        connection_count = cache.get(user_key, 0)
        
        if connection_count > settings.MAX_WS_CONNECTIONS_PER_USER:
            await self.close(code=4029, reason="Too many connections")
            return
            
        cache.set(user_key, connection_count + 1, 60)
        # ... rest of connection logic
```

## Testing Strategy

1. **Isolated Component Test**
   - Create a minimal component using the hook
   - Test in isolation

2. **Production Build Test**
   - Build for production
   - Test without development tools

3. **Different Browsers**
   - Test in Chrome, Firefox, Safari
   - Check for browser-specific issues

4. **Network Conditions**
   - Test with throttled network
   - Test with intermittent connectivity

## Next Steps

1. Add debug logging as outlined above
2. Test with React Strict Mode disabled
3. Implement connection throttling
4. Monitor with browser DevTools
5. Consider implementing centralized WebSocket service

## References
- [React Strict Mode](https://react.dev/reference/react/StrictMode)
- [WebSocket API](https://developer.mozilla.org/en-US/docs/Web/API/WebSocket)
- [Vite HMR](https://vitejs.dev/guide/api-hmr.html)
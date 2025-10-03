# WebSocket Infrastructure Consolidation Plan

## Current State Analysis

### Existing WebSocket Implementations

1. **Core WebSocket Manager** (`/utils/WebSocketManager.ts`)
   - Basic WebSocket wrapper with EventEmitter
   - Supports reconnection and authentication
   - Used by some features

2. **Service WebSocket Manager** (`/services/websocket/WebSocketManager.ts`)
   - Another implementation (needs review)
   - Connection throttling support

3. **Feature-specific WebSocket Hooks**
   - `/features/business-chat-network/hooks/`
     - `useChannelWebSocket.ts`
     - `useNetworkWebSocket.ts`
     - `useAgentChannelWebSocket.ts`
   - `/features/ai-assistant-hub/hooks/useChatStream.ts`
   - `/features/reddit-scout/hooks/useRedditStream.ts`
   - `/hooks/useAgentWebSocket.ts`

4. **OBS WebSocket Service** (`/services/obsWebSocketService.ts`)
   - Separate WebSocket for OBS Studio integration
   - Uses port 4455 (different from main app)

5. **Legacy Implementation** (`/services/websocket-legacy.ts`)
   - Old implementation that needs migration

## Target Architecture

### 1. Unified WebSocket Manager
```typescript
// /services/websocket/UnifiedWebSocketManager.ts
class UnifiedWebSocketManager {
  private connections: Map<string, WebSocketConnection>
  private store: WebSocketStore // Zustand store
  
  // Single instance for app-wide use
  static instance: UnifiedWebSocketManager
  
  // Connection management
  connect(namespace: string, config: ConnectionConfig)
  disconnect(namespace: string)
  disconnectAll()
  
  // Message handling
  send(namespace: string, event: string, data: any)
  subscribe(namespace: string, event: string, handler: Function)
  unsubscribe(namespace: string, event: string, handler: Function)
  
  // State management
  getConnectionState(namespace: string): ConnectionState
  isConnected(namespace: string): boolean
  
  // Debugging
  getDebugInfo(): DebugInfo
  enableDebugMode(enabled: boolean)
}
```

### 2. Connection Configuration
```typescript
interface ConnectionConfig {
  url: string
  namespace: string
  auth?: AuthConfig
  reconnect?: ReconnectConfig
  debug?: boolean
  messageQueue?: boolean
}

interface ReconnectConfig {
  enabled: boolean
  maxAttempts: number
  initialDelay: number
  maxDelay: number
  backoffMultiplier: number
}
```

### 3. Zustand Store Structure
```typescript
interface WebSocketStore {
  connections: Map<string, ConnectionState>
  debugMode: boolean
  messageQueue: MessageQueue[]
  
  // Actions
  updateConnectionState: (namespace: string, state: ConnectionState) => void
  queueMessage: (message: QueuedMessage) => void
  clearMessageQueue: (namespace?: string) => void
  setDebugMode: (enabled: boolean) => void
}
```

### 4. Feature Hooks (Simplified)
```typescript
// Generic hook for any feature
function useWebSocket(namespace: string, config?: Partial<ConnectionConfig>) {
  const manager = useWebSocketManager()
  const connectionState = useWebSocketStore(state => state.connections.get(namespace))
  
  useEffect(() => {
    manager.connect(namespace, config)
    return () => manager.disconnect(namespace)
  }, [namespace])
  
  return {
    send: (event: string, data: any) => manager.send(namespace, event, data),
    subscribe: (event: string, handler: Function) => manager.subscribe(namespace, event, handler),
    state: connectionState,
    isConnected: connectionState?.status === 'connected'
  }
}
```

## Migration Plan

### Phase 1: Create New Infrastructure
1. Build UnifiedWebSocketManager class
2. Implement Zustand store for state management
3. Add exponential backoff reconnection logic
4. Create message queuing system
5. Build debug tools and monitoring

### Phase 2: Create Adapters
1. Create adapter for business-chat-network
2. Create adapter for agent orchestra
3. Create adapter for AI assistant streaming
4. Keep OBS WebSocket separate (different protocol)

### Phase 3: Gradual Migration
1. Update one feature at a time to use new system
2. Test thoroughly before moving to next feature
3. Remove old implementations once migrated

### Phase 4: Cleanup
1. Remove legacy websocket implementations
2. Update documentation
3. Add comprehensive tests

## Event Standardization

### Standard Event Format
```typescript
interface WebSocketMessage {
  event: string
  namespace: string
  data: any
  timestamp: number
  messageId?: string
}
```

### Standard Events (all namespaces)
- `connect` - Connection established
- `disconnect` - Connection lost
- `error` - Error occurred
- `reconnecting` - Attempting to reconnect
- `authenticate` - Authentication required/completed

## Debug Tools

### WebSocket Debug Panel
- Real-time connection status for all namespaces
- Message log with filtering
- Manual message sending
- Connection controls (connect/disconnect/reconnect)
- Performance metrics (latency, message rate)

### Console Utilities
```typescript
window.__ws = {
  getConnections: () => ConnectionInfo[],
  send: (namespace: string, event: string, data: any) => void,
  disconnect: (namespace: string) => void,
  reconnect: (namespace: string) => void,
  getMessageLog: (namespace?: string) => Message[],
  clearMessageLog: () => void
}
```

## Benefits

1. **Single Source of Truth**: One WebSocket manager for entire app
2. **Consistent Error Handling**: Unified reconnection and error strategies
3. **Better Debugging**: Centralized logging and monitoring
4. **Offline Support**: Message queuing for resilience
5. **Performance**: Connection pooling and throttling
6. **Type Safety**: Strongly typed events and messages
7. **Testing**: Easier to mock and test

## Implementation Priority

1. Core UnifiedWebSocketManager
2. Zustand store integration
3. Business Chat Network migration (highest real-time need)
4. Agent Orchestra migration
5. Other features
6. Debug tools
7. Documentation
# Detailed Investigation: Frontend Systems

## Common Issues to Investigate

### Issue 1: State Management Inconsistencies
**Problem**: State updates don't propagate correctly across components

**Investigation Steps:**

1. **Zustand Store Structure**
   ```
   Directory: donkey-betz-frontend/src/store/
   
   Check each store:
   - useAuthStore.ts
   - useAgentStore.ts
   - useMemoryStore.ts
   - useBusinessStore.ts
   
   Questions:
   - Are stores properly isolated?
   - Is there store interdependency?
   - Are actions async-safe?
   ```

2. **State Update Patterns**
   ```typescript
   // Look for problematic patterns
   // Bad: Direct mutation
   set((state) => {
       state.items.push(newItem); // Mutation!
       return state;
   });
   
   // Good: Immutable update
   set((state) => ({
       items: [...state.items, newItem]
   }));
   ```

3. **Component Re-render Issues**
   ```bash
   # Find components using stores
   grep -r "useStore\|use.*Store" donkey-betz-frontend/src/ --include="*.tsx"
   
   # Check for unnecessary re-renders
   # Look for missing dependency arrays or incorrect selectors
   ```

### Issue 2: WebSocket Connection Management
**Problem**: WebSocket connections not properly managed, causing memory leaks or missed updates

**Investigation Steps:**

1. **WebSocket Manager Implementation**
   ```
   File: donkey-betz-frontend/src/services/websocket/WebSocketManager.ts
   
   Check:
   - Connection lifecycle management
   - Reconnection logic
   - Message queue for offline
   - Cleanup on unmount
   ```

2. **Component WebSocket Usage**
   ```typescript
   // Find WebSocket usage
   grep -r "wsManager\|WebSocketManager" donkey-betz-frontend/src/ --include="*.tsx"
   
   // Check for cleanup
   // Look for missing unsubscribe in useEffect cleanup
   useEffect(() => {
       const unsubscribe = wsManager.subscribe(url, handler);
       // Missing: return () => unsubscribe();
   }, []);
   ```

3. **WebSocket Event Handling**
   ```
   Files to check:
   - CommandCenter components
   - ChatInterface components
   - AgentActivityVisualizer
   
   Look for:
   - Proper event type handling
   - Error boundary implementation
   - Loading states during connection
   ```

### Issue 3: API Error Handling
**Problem**: API errors not properly displayed to users or causing white screens

**Investigation Steps:**

1. **API Client Error Handling**
   ```
   File: donkey-betz-frontend/src/services/apiClient.ts
   
   Check:
   - Response interceptors
   - Error transformation
   - Token refresh logic
   - Network error handling
   ```

2. **Component Error States**
   ```bash
   # Find error handling patterns
   grep -r "catch\|error\|Error" donkey-betz-frontend/src/features/ --include="*.tsx"
   
   # Look for:
   - Missing try-catch blocks
   - Unhandled promise rejections
   - Error boundary usage
   ```

## Specific Code Queries

### Query 1: Find Performance Issues
```bash
# Find large component files (potential optimization targets)
find donkey-betz-frontend/src -name "*.tsx" -exec wc -l {} \; | sort -rn | head -20

# Find potential memory leaks
grep -r "addEventListener\|setInterval\|setTimeout" donkey-betz-frontend/src/ --include="*.tsx" | grep -v "clearInterval\|clearTimeout\|removeEventListener"

# Find missing React.memo
grep -r "export.*function.*Component" donkey-betz-frontend/src/components/ --include="*.tsx" | grep -v "memo("
```

### Query 2: State Management Analysis
```bash
# Find all Zustand stores
find donkey-betz-frontend/src/store -name "*.ts"

# Check store subscribers
grep -r "subscribe(" donkey-betz-frontend/src/ --include="*.ts*"

# Find direct state access (potential issues)
grep -r "get()\.state\|getState()" donkey-betz-frontend/src/ --include="*.tsx"
```

### Query 3: TypeScript Type Safety
```bash
# Find 'any' types
grep -r ": any\|as any" donkey-betz-frontend/src/ --include="*.ts*"

# Find missing types
grep -r "TODO.*type\|FIXME.*type\|@ts-ignore" donkey-betz-frontend/src/ --include="*.ts*"

# Find untyped API responses
grep -r "response\.data[^.]" donkey-betz-frontend/src/ --include="*.ts*"
```

## Testing Frontend Issues

### Test 1: Component Performance
```typescript
// Add performance monitoring
import { Profiler } from 'react';

function onRenderCallback(id, phase, actualDuration) {
    console.log(`${id} (${phase}) took ${actualDuration}ms`);
}

<Profiler id="SlowComponent" onRender={onRenderCallback}>
    <SlowComponent />
</Profiler>
```

### Test 2: Memory Leak Detection
```javascript
// Browser console
// Before using the app
console.log('Initial:', performance.memory.usedJSHeapSize);

// After heavy usage
console.log('After use:', performance.memory.usedJSHeapSize);

// Navigate away and back
console.log('After navigation:', performance.memory.usedJSHeapSize);
```

### Test 3: WebSocket Reliability
```typescript
// Test WebSocket reconnection
const testReconnection = () => {
    // Force disconnect
    wsManager.disconnect();
    
    // Wait and check reconnection
    setTimeout(() => {
        console.log('Connected:', wsManager.isConnected());
        console.log('Retry count:', wsManager.retryCount);
    }, 5000);
};
```

## Critical Files to Review

1. **State Management**
   - `donkey-betz-frontend/src/store/index.ts` - Store configuration
   - `donkey-betz-frontend/src/store/useAuthStore.ts` - Auth state
   - `donkey-betz-frontend/src/store/useAgentStore.ts` - Agent state

2. **API Integration**
   - `donkey-betz-frontend/src/services/apiClient.ts` - HTTP client
   - `donkey-betz-frontend/src/services/websocket/WebSocketManager.ts` - WS client
   - `donkey-betz-frontend/src/types/api.ts` - API types

3. **Key Components**
   - `donkey-betz-frontend/src/features/ai-assistant/components/ChatInterface.tsx`
   - `donkey-betz-frontend/src/features/command-center/components/AgentActivityVisualizer.tsx`
   - `donkey-betz-frontend/src/features/memory-palace/components/MemorySearch.tsx`

## Common Problems and Solutions

### Problem: Infinite Re-renders
```typescript
// Bad - causes infinite loop
useEffect(() => {
    fetchData().then(data => {
        setState(data); // This changes on every render
    });
}); // Missing dependency array!

// Good
useEffect(() => {
    fetchData().then(data => {
        setState(data);
    });
}, []); // Empty array = run once
```

### Problem: Memory Leaks in Components
```typescript
// Bad - no cleanup
useEffect(() => {
    const timer = setInterval(() => {
        updateData();
    }, 1000);
}, []);

// Good - with cleanup
useEffect(() => {
    const timer = setInterval(() => {
        updateData();
    }, 1000);
    
    return () => clearInterval(timer); // Cleanup!
}, []);
```

### Problem: Unhandled API Errors
```typescript
// Bad - no error handling
const fetchData = async () => {
    const response = await apiClient.get('/data');
    setData(response.data);
};

// Good - with error handling
const fetchData = async () => {
    try {
        setLoading(true);
        const response = await apiClient.get('/data');
        setData(response.data);
        setError(null);
    } catch (err) {
        setError(err.message);
        console.error('Fetch failed:', err);
    } finally {
        setLoading(false);
    }
};
```

## Performance Optimization

### Optimize Large Lists
```typescript
// Use React.memo for list items
const ListItem = React.memo(({ item, onClick }) => {
    return <div onClick={() => onClick(item.id)}>{item.name}</div>;
}, (prevProps, nextProps) => {
    // Custom comparison
    return prevProps.item.id === nextProps.item.id;
});

// Use virtualization for long lists
import { FixedSizeList } from 'react-window';

<FixedSizeList
    height={600}
    itemCount={items.length}
    itemSize={50}
    width="100%"
>
    {({ index, style }) => (
        <div style={style}>
            {items[index].name}
        </div>
    )}
</FixedSizeList>
```

### Optimize Store Subscriptions
```typescript
// Bad - subscribes to entire store
const store = useAgentStore();

// Good - subscribes to specific slice
const agents = useAgentStore(state => state.agents);
const isLoading = useAgentStore(state => state.isLoading);

// Even better - with shallow comparison
const { agents, isLoading } = useAgentStore(
    state => ({ agents: state.agents, isLoading: state.isLoading }),
    shallow
);
```

### Bundle Size Analysis
```bash
# Analyze bundle size
npm run build
npm run analyze

# Find large dependencies
du -sh node_modules/* | sort -hr | head -20

# Check for duplicate dependencies
npm ls --depth=0 | grep -E "deduped|UNMET"
```
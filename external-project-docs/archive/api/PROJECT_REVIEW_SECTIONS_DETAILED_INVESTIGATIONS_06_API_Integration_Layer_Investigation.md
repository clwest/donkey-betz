# Detailed Investigation: API & Integration Layer

## Common Issues to Investigate

### Issue 1: API Rate Limiting Causing Failures
**Problem**: External API calls fail due to rate limits, causing cascade failures

**Investigation Steps:**

1. **Rate Limiter Implementation**
   ```
   File: backend/api_services/rate_limiter.py
   
   Check:
   - How are rate limits tracked?
   - Is it per-API or global?
   - What happens when limit hit?
   ```

2. **Circuit Breaker Analysis**
   ```
   File: backend/api_services/circuit_breaker.py
   
   Questions:
   - When does circuit open?
   - How long before retry?
   - Is there exponential backoff?
   ```

3. **Cache Strategy Investigation**
   ```python
   # Check caching implementation
   File: backend/api_services/cache_service.py
   
   # Look for:
   - Cache TTL settings
   - Cache key patterns
   - Cache invalidation logic
   ```

### Issue 2: WebSocket Connection Instability
**Problem**: WebSocket connections drop frequently or fail to reconnect

**Investigation Steps:**

1. **WebSocket Configuration**
   ```
   File: backend/server/asgi.py
   
   Check:
   - Channel layers configuration
   - Redis connection settings
   - Timeout values
   ```

2. **Consumer Implementation**
   ```python
   # Check all consumers
   find backend -name "consumers.py" -exec grep -l "disconnect\|connect" {} \;
   
   # Look for:
   - Reconnection logic
   - Error handling in disconnect
   - Heartbeat/ping implementation
   ```

3. **Frontend WebSocket Manager**
   ```
   File: donkey-betz-frontend/src/services/websocket/WebSocketManager.ts
   
   Investigate:
   - Reconnection strategy
   - Error handling
   - Queue for failed messages
   ```

### Issue 3: API Response Inconsistencies
**Problem**: Same API endpoint returns different response formats

**Investigation Steps:**

1. **Serializer Validation**
   ```bash
   # Find all serializers
   find backend -name "serializers.py" -exec grep -l "ModelSerializer\|Serializer" {} \;
   
   # Check for:
   - Optional fields without defaults
   - Dynamic field inclusion
   - Version-specific serializers
   ```

2. **Error Response Standardization**
   ```
   File: backend/server/middleware/error_handler.py
   
   Check:
   - Is error format consistent?
   - Are all exceptions caught?
   - Is there a standard error schema?
   ```

## Specific Code Queries

### Query 1: Find All External API Integrations
```bash
# Find API service files
ls -la backend/api_services/

# Find API keys usage
grep -r "API_KEY\|CLIENT_ID\|SECRET" backend/ --include="*.py" | grep -v test

# Find HTTP client usage
grep -r "requests\.\|httpx\.\|aiohttp" backend/ --include="*.py"
```

### Query 2: WebSocket Debugging
```bash
# Find all WebSocket routes
find backend -name "routing.py" -exec cat {} \;

# Check WebSocket authentication
grep -r "scope\[.user.\]\|self\.scope" backend/ --include="*.py"

# Find WebSocket error handling
grep -r "WebSocketDisconnect\|ConnectionClosed" backend/ --include="*.py"
```

### Query 3: API Versioning Check
```bash
# Look for API versioning
grep -r "v1/\|v2/\|version" backend/server/urls.py

# Find version-specific views
find backend/api -type d -name "v*"
```

## Testing API Reliability

### Test 1: Rate Limit Behavior
```python
# Test rate limiter
import time
from api_services.polygon_service import PolygonService

service = PolygonService()
results = []

# Make rapid requests
for i in range(10):
    start = time.time()
    result = service.get_quote('AAPL')
    duration = time.time() - start
    
    results.append({
        'attempt': i,
        'success': 'error' not in result,
        'duration': duration,
        'cached': result.get('source') == 'cache'
    })
    
    print(f"Attempt {i}: {results[-1]}")

# Analyze pattern
cached_count = sum(1 for r in results if r['cached'])
print(f"Cached responses: {cached_count}/10")
```

### Test 2: WebSocket Stability
```javascript
// Frontend console test
const ws = new WebSocket('ws://localhost:8000/ws/agent-activity/test/');
let disconnectCount = 0;

ws.onopen = () => console.log('Connected');
ws.onclose = () => {
    console.log('Disconnected');
    disconnectCount++;
};
ws.onerror = (e) => console.error('Error:', e);

// Send messages periodically
setInterval(() => {
    if (ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({type: 'ping'}));
    }
}, 5000);

// Check stability after 1 minute
setTimeout(() => {
    console.log(`Disconnections in 1 minute: ${disconnectCount}`);
}, 60000);
```

### Test 3: API Response Consistency
```python
# Test response format consistency
from api.business_hub.views import StockViewSet
from rest_framework.test import APIRequestFactory

factory = APIRequestFactory()
view = StockViewSet.as_view({'get': 'retrieve'})

# Make multiple requests
responses = []
for _ in range(5):
    request = factory.get('/api/stocks/AAPL/')
    response = view(request, pk='AAPL')
    responses.append(response.data)

# Check consistency
keys_list = [set(r.keys()) for r in responses]
if len(set(map(tuple, keys_list))) == 1:
    print("✓ Response format consistent")
else:
    print("✗ Response format varies!")
    print(f"Different formats: {keys_list}")
```

## Critical Integration Points

1. **API Service Base Class**
   ```python
   # backend/api_services/base_service.py
   class BaseAPIService:
       def __init__(self):
           self.rate_limiter = RateLimiter()
           self.circuit_breaker = CircuitBreaker()
           self.cache = cache
       
       def make_request(self, endpoint, **kwargs):
           # Check rate limit
           if not self.rate_limiter.can_proceed():
               return self.get_cached_or_error()
           
           # Check circuit breaker
           if self.circuit_breaker.is_open():
               return self.get_cached_or_error()
           
           try:
               response = self._execute_request(endpoint, **kwargs)
               self.cache.set(self.cache_key(endpoint), response)
               return response
           except Exception as e:
               self.circuit_breaker.record_failure()
               raise
   ```

2. **WebSocket Middleware**
   ```python
   # backend/server/channelsmiddleware.py
   class WebSocketAuthMiddleware:
       async def __call__(self, scope, receive, send):
           # Add auth
           scope['user'] = await self.get_user(scope)
           
           # Add error handling
           try:
               return await self.app(scope, receive, send)
           except Exception as e:
               await send({
                   'type': 'websocket.close',
                   'code': 1011,
                   'reason': str(e)
               })
   ```

## Common Problems and Solutions

### Problem: API Keys Hardcoded
```python
# Bad - hardcoded
class PolygonService:
    API_KEY = "REDACTED"  # Don't do this!

# Good - environment variable
class PolygonService:
    def __init__(self):
        self.api_key = settings.POLYGON_API_KEY
        if not self.api_key:
            raise ImproperlyConfigured("POLYGON_API_KEY not set")
```

### Problem: No Request Retry Logic
```python
# Add retry decorator
from functools import wraps
import time

def retry_on_failure(max_attempts=3, delay=1):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:
                        raise
                    time.sleep(delay * (2 ** attempt))  # Exponential backoff
            return None
        return wrapper
    return decorator

@retry_on_failure(max_attempts=3)
def call_external_api(endpoint):
    # API call logic
```

### Problem: WebSocket Memory Leaks
```python
# Ensure cleanup in consumers
class ChatConsumer(AsyncWebsocketConsumer):
    async def disconnect(self, close_code):
        # Clean up subscriptions
        if hasattr(self, 'room_group_name'):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
        
        # Clear any stored data
        if hasattr(self, 'message_queue'):
            self.message_queue.clear()
        
        # Call parent disconnect
        await super().disconnect(close_code)
```

## Performance Optimization

### API Call Batching
```python
# Instead of multiple calls
# for symbol in symbols:
#     get_quote(symbol)

# Batch calls
def get_quotes_batch(symbols):
    # Use batch endpoint if available
    if hasattr(self, 'batch_endpoint'):
        return self.call_api(self.batch_endpoint, symbols=symbols)
    
    # Otherwise, use asyncio for parallel calls
    import asyncio
    
    async def fetch_all():
        tasks = [self.get_quote_async(s) for s in symbols]
        return await asyncio.gather(*tasks)
    
    return asyncio.run(fetch_all())
```

### Cache Warming Strategy
```python
# Preload common data
@shared_task
def warm_cache():
    common_symbols = ['AAPL', 'GOOGL', 'MSFT', 'AMZN']
    service = StockService()
    
    for symbol in common_symbols:
        try:
            data = service.get_quote(symbol)
            cache.set(f'stock:{symbol}', data, timeout=300)
        except Exception as e:
            logger.error(f"Cache warming failed for {symbol}: {e}")
```
# WebSocket Timeout Warning - Deep Analysis

## Error Pattern
```
Application instance <Task cancelling name='Task-72'
coro=<ProtocolTypeRouter.__call__() running at ...channels/routing.py:48>
wait_for=<Task cancelled name='Task-84'
coro=<RedisChannelLayer.receive() done, defined at ...channels_redis/core.py:251>>>
for connection <WebSocketProtocol client=['127.0.0.1', 51406] path=b'/ws/consciousness/'>
took too long to shut down and was killed.
```

## Root Cause Analysis

The error shows:
1. The main task is `ProtocolTypeRouter.__call__()` - this is the Channels routing layer
2. It's waiting for `RedisChannelLayer.receive()` - this is the Redis message receiver
3. The connection is being forcefully killed because the Redis receiver isn't closing quickly

## The Real Problem

The issue is NOT in our disconnect handler, but in the fact that the WebSocket is waiting for messages from Redis channel layer. When we disconnect, the Redis receive operation doesn't cancel immediately.

## Solution Approaches

### Approach 1: Minimal Disconnect (Current)
- Just cancel tasks and exit immediately
- Don't try to clean up Redis connections
- Let the framework handle cleanup

### Approach 2: Force Close Channel Layer
- Close the underlying Redis connection forcefully
- This might cause other issues

### Approach 3: Use Daphne Configuration
- Configure Daphne to allow longer shutdown times
- Or configure it to not wait for WebSocket cleanup

## Recommended Fix

The issue appears to be that the WebSocket connections are closing/reconnecting rapidly (within milliseconds), which might be a frontend issue causing the connections to immediately disconnect after connecting.

Looking at the logs:
```
21:28:09,888 INFO     🧠 Consciousness stream connected
21:28:09,889 WARNING  Application instance... took too long to shut down
```

The connection closes within 1ms of connecting! This suggests the frontend is immediately closing the connection.

## Next Steps

1. Check why the frontend is immediately disconnecting
2. Add connection stability logic to the frontend
3. Implement reconnection backoff
4. Consider using a connection pool
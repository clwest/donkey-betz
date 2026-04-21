# WebSocket Health Diagnostics - Complete Handoff Document

**Date**: September 4, 2025  
**Agent**: ws-health-diagnostics  
**Status**: Diagnostics Complete - Implementation Required  
**Priority**: HIGH - Blocking real-time features

## Executive Summary

The WebSocket infrastructure for AI Content Studio is properly configured but failing due to authentication incompatibility. The Django Channels middleware expects session-based authentication while the frontend sends DRF token authentication. This document provides complete diagnostics results and implementation steps for the fix.

## What Was Done

### 1. System Health Check
- ✅ Verified Daphne ASGI server running on port 8001 (PID 41909)
- ✅ Confirmed Redis server connectivity and responsiveness
- ✅ Validated Django Channels configuration in settings
- ✅ Checked WebSocket routing configuration

### 2. Connection Testing
- Tested WebSocket endpoint: `ws://localhost:8001/ws/assistant/`
- Attempted connections with various authentication methods
- Analyzed error responses and handshake failures
- Traced authentication flow through middleware stack

### 3. Code Analysis
- Reviewed ASGI configuration at `backend/core/asgi.py`
- Analyzed WebSocket consumer at `backend/assistant/consumers.py`
- Examined frontend connection logic at `ai-studio-web/src/services/agent-orchestra.service.ts`
- Identified authentication middleware incompatibility

### 4. Root Cause Identification
- **Primary Issue**: `AuthMiddlewareStack` only handles Django session authentication
- **Token Issue**: DRF tokens sent by frontend are not processed by WebSocket middleware
- **Result**: All WebSocket connections fail with HTTP 403 "Access denied"

## Current System State

### Working Components
| Component | Status | Details |
|-----------|--------|---------|
| Daphne Server | ✅ Working | Running on port 8001 |
| Redis | ✅ Working | Channel layer backend operational |
| Routing | ✅ Working | URLs properly configured |
| Frontend Logic | ✅ Working | Token included in connection attempts |

### Failing Components
| Component | Status | Issue |
|-----------|--------|-------|
| WebSocket Auth | ❌ Failing | No token authentication middleware |
| Connection Handshake | ❌ Failing | HTTP 403 on all attempts |
| Real-time Features | ❌ Blocked | Cannot establish WebSocket connections |

## Implementation Steps for Next Agent

### Step 1: Create Token Authentication Middleware

**File to Create**: `/Users/donkeyking/development/ai-content-studio/backend/core/websocket_auth.py`

```python
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model
from urllib.parse import parse_qs
import logging

logger = logging.getLogger(__name__)

@database_sync_to_async
def get_user_from_token(token_key):
    """
    Retrieve user from DRF token.
    Returns AnonymousUser if token is invalid or doesn't exist.
    """
    try:
        token = Token.objects.get(key=token_key)
        return token.user
    except Token.DoesNotExist:
        return AnonymousUser()

class TokenAuthMiddleware:
    """
    Token authentication middleware for Django Channels WebSocket connections.
    Extracts token from query parameters or headers and authenticates the user.
    """
    
    def __init__(self, inner):
        self.inner = inner
    
    async def __call__(self, scope, receive, send):
        # Initialize token_key
        token_key = None
        
        # Method 1: Extract token from query string (preferred for WebSocket)
        query_string = scope.get('query_string', b'').decode()
        if query_string:
            query_params = parse_qs(query_string)
            if 'token' in query_params:
                token_key = query_params['token'][0]
                logger.debug(f"Token found in query string: {token_key[:8]}...")
        
        # Method 2: Extract token from headers (fallback)
        if not token_key:
            headers = dict(scope['headers'])
            auth_header = headers.get(b'authorization', b'').decode()
            if auth_header.startswith('Token '):
                token_key = auth_header[6:]  # Remove 'Token ' prefix
                logger.debug(f"Token found in Authorization header: {token_key[:8]}...")
        
        # Authenticate user using token
        if token_key:
            scope['user'] = await get_user_from_token(token_key)
            if not scope['user'].is_anonymous:
                logger.info(f"WebSocket authenticated user: {scope['user'].username}")
            else:
                logger.warning("Invalid token provided for WebSocket connection")
        else:
            scope['user'] = AnonymousUser()
            logger.warning("WebSocket connection attempt without token")
        
        return await self.inner(scope, receive, send)
```

### Step 2: Update ASGI Configuration

**File to Modify**: `/Users/donkeyking/development/ai-content-studio/backend/core/asgi.py`

**Current Code (Lines 25-39)**:
```python
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator

# ... other code ...

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(websocket_urlpatterns)
        )
    ),
})
```

**Replace With**:
```python
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from .websocket_auth import TokenAuthMiddleware  # Import custom middleware

# ... other code ...

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AllowedHostsOriginValidator(
        TokenAuthMiddleware(  # Use token auth instead of AuthMiddlewareStack
            URLRouter(websocket_urlpatterns)
        )
    ),
})
```

### Step 3: Update WebSocket Consumer

**File to Modify**: `/Users/donkeyking/development/ai-content-studio/backend/assistant/consumers.py`

**Current Code (Lines 27-34)**:
```python
async def connect(self):
    """Accept WebSocket connection"""
    self.user = self.scope.get("user", None)
    # ... rest of code ...
```

**Replace With**:
```python
async def connect(self):
    """Accept WebSocket connection if authenticated"""
    self.user = self.scope.get("user", None)
    
    # Reject anonymous connections
    if not self.user or self.user.is_anonymous:
        logger.warning(
            f"Anonymous WebSocket connection rejected from "
            f"{self.scope.get('client', ['unknown', 0])[0]}"
        )
        await self.close(code=4001)  # Custom close code for auth failure
        return
    
    logger.info(f"WebSocket connection accepted for user: {self.user.username}")
    # ... rest of existing code ...
```

### Step 4: Enhance Frontend Error Handling (Optional but Recommended)

**File to Modify**: `/Users/donkeyking/development/ai-content-studio/ai-studio-web/src/services/agent-orchestra.service.ts`

**Add After Line 504** (in the WebSocket error handler):
```typescript
ws.addEventListener('close', (event) => {
    if (event.code === 4001) {
        console.error('WebSocket authentication failed. Please check your token.');
        // Optionally trigger re-authentication flow
        this.handleAuthenticationFailure();
    } else if (event.code === 1006) {
        console.error('WebSocket connection lost abnormally');
    }
    // ... existing reconnection logic ...
});
```

**Add New Method**:
```typescript
private handleAuthenticationFailure(): void {
    // Clear invalid token
    localStorage.removeItem('authToken');
    // Redirect to login or refresh token
    window.location.href = '/login';
}
```

## Testing & Verification

### 1. Basic Connection Test
```bash
# Test with valid token
python -c "
import asyncio
import websockets

async def test():
    uri = 'ws://localhost:8001/ws/assistant/?token=<redacted-993f8273-2026-04-20>'
    async with websockets.connect(uri) as ws:
        print('Connected successfully!')
        await ws.send('{\"type\": \"ping\"}')
        response = await ws.recv()
        print(f'Received: {response}')

asyncio.run(test())
"
```

### 2. Browser Console Test
```javascript
// Run in browser DevTools console
const testWebSocket = () => {
    const token = localStorage.getItem('authToken') || '<redacted-993f8273-2026-04-20>';
    const ws = new WebSocket(`ws://localhost:8001/ws/assistant/?token=${token}`);
    
    ws.onopen = () => {
        console.log('✅ WebSocket connected!');
        ws.send(JSON.stringify({ type: 'ping' }));
    };
    
    ws.onmessage = (event) => {
        console.log('📨 Received:', event.data);
    };
    
    ws.onerror = (error) => {
        console.error('❌ WebSocket error:', error);
    };
    
    ws.onclose = (event) => {
        console.log(`🔌 WebSocket closed: Code ${event.code}, Reason: ${event.reason}`);
    };
    
    return ws;
};

const ws = testWebSocket();
```

### 3. Django Shell Test
```bash
python manage.py shell
```
```python
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model

# Verify token exists
User = get_user_model()
user = User.objects.get(username='testuser')
token = Token.objects.get(user=user)
print(f"Token: {token.key}")
# Should output: <redacted-993f8273-2026-04-20>
```

### 4. Monitor Logs
```bash
# Watch Django logs for WebSocket connections
tail -f backend/logs/django.log | grep -E "(WebSocket|ws/assistant)"

# Monitor Daphne output
ps aux | grep daphne | grep -v grep
# Note the PID and check its output
```

## Expected Outcomes After Implementation

### Success Indicators
- ✅ WebSocket connections establish with status 101 (Switching Protocols)
- ✅ Frontend agent orchestration features work properly
- ✅ Real-time updates flow between backend and frontend
- ✅ Console shows successful WebSocket connections
- ✅ No more 403 authentication errors

### Potential Issues & Solutions

| Issue | Symptom | Solution |
|-------|---------|----------|
| Token not found | Still getting 403 errors | Verify token is being sent in query string |
| Import errors | Module not found | Ensure websocket_auth.py is in correct location |
| User is None | Consumer crashes | Check Token model exists in database |
| CORS issues | Connection blocked | Verify AllowedHostsOriginValidator settings |

## Additional Recommendations

### 1. Token Refresh Strategy
Consider implementing token refresh for long-lived WebSocket connections:
```python
# In TokenAuthMiddleware
async def validate_token_periodically(self, scope):
    # Implement token expiry checking
    # Refresh or disconnect if expired
    pass
```

### 2. Connection Pooling
For production, implement connection pooling to manage multiple WebSocket connections efficiently.

### 3. Monitoring & Metrics
Add monitoring for:
- Connection success/failure rates
- Average connection duration
- Message throughput
- Authentication failures

### 4. Security Enhancements
- Implement rate limiting per user
- Add IP-based connection limits
- Log suspicious authentication attempts
- Consider implementing JWT tokens for better security

## Files Modified/Created Summary

| Action | File | Purpose |
|--------|------|---------|
| CREATE | `backend/core/websocket_auth.py` | Token authentication middleware |
| MODIFY | `backend/core/asgi.py` | Use token auth middleware |
| MODIFY | `backend/assistant/consumers.py` | Handle unauthenticated connections |
| MODIFY | `ai-studio-web/src/services/agent-orchestra.service.ts` | Enhanced error handling (optional) |

## Next Steps

1. **Implement the fixes** in the order provided above
2. **Test each component** using the provided test scripts
3. **Monitor logs** during testing to ensure proper authentication flow
4. **Deploy to staging** for integration testing
5. **Update documentation** with WebSocket authentication details

## Related Documentation

- [Django Channels Authentication](https://channels.readthedocs.io/en/stable/topics/authentication.html)
- [DRF Token Authentication](https://www.django-rest-framework.org/api-guide/authentication/#tokenauthentication)
- [WebSocket Protocol](https://datatracker.ietf.org/doc/html/rfc6455)
- Previous diagnostics: `documentation/UCWSF_PATCH_NOTES.md`

## Contact & Support

This handoff was created by the ws-health-diagnostics agent. For questions about the implementation:
- Check Django Channels documentation for middleware details
- Review DRF token authentication documentation
- Test in development environment before production deployment

---

**End of Handoff Document**

*Generated by ws-health-diagnostics agent on September 4, 2025*
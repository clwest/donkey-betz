# Authentication System Documentation

## Overview

The Unified Donkey Betz platform uses token-based authentication to secure API endpoints and WebSocket connections. All API requests (except public endpoints) require a valid authentication token.

## Features

- **Token-based authentication** using Django REST Framework tokens
- **Unified middleware** for consistent authentication across all endpoints
- **WebSocket authentication** support
- **Caching optimization** for performance
- **Role-based access** (staff vs regular users)

## Public Endpoints (No Auth Required)

- `/api/v1/health/` - Health check
- `/api/v1/auth/login/` - User login
- `/api/v1/auth/register/` - User registration
- `/api/v1/auth/forgot-password/` - Password reset request
- `/api/v1/auth/reset-password/` - Password reset confirmation

## Generating Authentication Tokens

### Using the Token Generator Script

```bash
source .venv/bin/activate
python generate_auth_token.py
```

This will create two users with tokens:
- **Regular User**: `api_user`
- **Admin User**: `admin_api_user` (has staff privileges)

### Manual Token Generation

```python
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

# Create or get user
user = User.objects.create_user(
    username='my_api_user',
    email='user@example.com',
    password='<your-secure-password>'
)

# Generate token
token = Token.objects.create(user=user)
print(f"Token: {token.key}")
```

## Using Authentication Tokens

### HTTP Headers (Recommended)

```bash
# Using curl
curl -H "Authorization: Token YOUR_TOKEN_HERE" \
     http://localhost:8000/api/v1/status/

# Using Python requests
import requests
headers = {'Authorization': 'Token YOUR_TOKEN_HERE'}
response = requests.get('http://localhost:8000/api/v1/status/', headers=headers)
```

### Custom Header

```bash
curl -H "X-API-Key: YOUR_TOKEN_HERE" \
     http://localhost:8000/api/v1/status/
```

### Query Parameter (Development Only)

```bash
# Only works when DEBUG=True
curl http://localhost:8000/api/v1/status/?token=YOUR_TOKEN_HERE
```

## WebSocket Authentication

WebSocket connections require authentication tokens passed as query parameters:

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/intelligence/?token=YOUR_TOKEN_HERE');
```

## API Response Codes

- **200 OK** - Request successful
- **401 Unauthorized** - No token provided or invalid token
- **403 Forbidden** - Valid token but insufficient permissions
- **429 Too Many Requests** - Rate limit exceeded

## Performance Optimizations

### Intelligence API Caching

The `/api/intelligence/` endpoint uses multi-level caching:

1. **Full Response Cache** (5 minutes)
   - Complete API response cached
   - Instant responses for repeated requests

2. **Consciousness Data Cache** (5 minutes)
   - Heavy computation results cached
   - Shared across requests

3. **Health Data Cache** (1 minute)
   - System health metrics
   - Updates more frequently

Force refresh cache:
```bash
curl -H "Authorization: Token YOUR_TOKEN" \
     http://localhost:8000/api/intelligence/?force_refresh=true
```

## Rate Limiting

Special endpoints have additional rate limiting:

- `/api/v1/auth/login/` - 5 attempts per 5 minutes
- `/api/v1/auth/register/` - 3 attempts per hour
- `/api/v1/auth/forgot-password/` - 3 attempts per hour

## Security Headers

All API responses include security headers:

- `X-Content-Type-Options: nosniff`
- `X-XSS-Protection: 1; mode=block`
- `X-Frame-Options: DENY`
- `Referrer-Policy: strict-origin-when-cross-origin`
- `Strict-Transport-Security` (production only)

## Middleware Architecture

### UnifiedTokenAuthenticationMiddleware

Located in `core/auth_middleware.py`

- Validates tokens for all `/api/` endpoints
- Handles public path exceptions
- Enforces staff requirements for admin endpoints
- Provides consistent error responses

### WebSocketAuthenticationMiddleware

- Validates tokens for WebSocket connections
- Supports query string and header authentication
- Enforces authentication requirements

## Testing Authentication

### Health Check Script

```python
import requests

# Test with token
token = "YOUR_TOKEN_HERE"
headers = {'Authorization': f'Token {token}'}

# Test endpoints
endpoints = [
    '/api/v1/status/',
    '/api/v1/health/',
    '/api/intelligence/',
    '/api/proposals/'
]

for endpoint in endpoints:
    url = f'http://localhost:8000{endpoint}'
    response = requests.get(url, headers=headers)
    print(f"{endpoint}: {response.status_code}")
```

### WebSocket Test

```python
import asyncio
import websockets
import json

async def test_websocket():
    token = "YOUR_TOKEN_HERE"
    uri = f"ws://localhost:8000/ws/intelligence/?token={token}"

    async with websockets.connect(uri) as websocket:
        # Send test message
        await websocket.send(json.dumps({
            "type": "ping",
            "timestamp": "2025-01-01T00:00:00"
        }))

        # Receive response
        response = await websocket.recv()
        print(f"Response: {response}")

asyncio.run(test_websocket())
```

## Troubleshooting

### Common Issues

1. **401 Unauthorized**
   - Verify token is correct
   - Check token format: `Token <key>` not `Bearer <key>`
   - Ensure user is active

2. **403 Forbidden**
   - User lacks required permissions
   - Staff endpoint accessed with regular user token

3. **WebSocket Connection Refused**
   - Token not provided in query string
   - Invalid or expired token
   - WebSocket auth required (check settings)

### Debug Tips

Enable debug logging in `core/settings.py`:

```python
LOGGING = {
    'loggers': {
        'core.auth_middleware': {
            'level': 'DEBUG',
        }
    }
}
```

## API Endpoints Summary

### Authentication Endpoints

- `POST /api/v1/auth/login/` - Get authentication token
- `POST /api/v1/auth/logout/` - Invalidate token
- `POST /api/v1/auth/register/` - Create new user
- `GET /api/v1/auth/user/` - Get current user info

### Protected Endpoints

All require valid token:

- `GET /api/v1/status/` - Platform status
- `GET /api/intelligence/` - System intelligence data
- `GET /api/proposals/` - System proposals
- `WebSocket /ws/intelligence/` - Real-time updates

### Admin Endpoints

Require staff token:

- `/api/v1/admin/*` - Admin operations
- `/api/v1/system/*` - System management
- `/api/v1/metrics/admin/*` - Admin metrics

## Performance Metrics

After optimization:

- **Intelligence API**: ~70ms (from 25+ seconds)
- **Status API**: ~200ms
- **WebSocket Connection**: ~60ms
- **Cache Hit Response**: <10ms

## Next Steps

With authentication fully implemented, the platform is ready for:

1. **AI Nexus Development** - Build advanced AI features
2. **User Management UI** - Create frontend for auth
3. **API Documentation** - Generate OpenAPI specs
4. **Production Deployment** - Configure for production use
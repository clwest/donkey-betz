# Backend Configuration Guide

## Port Configuration

The Django backend can run in multiple modes depending on your needs:

### Server Modes

1. **Standard Django Development Server** (HTTP only)
   ```bash
   make run-backend
   # or
   python manage.py runserver 0.0.0.0:8000
   ```
   - Port: 8000
   - Features: HTTP API, large file upload support
   - No WebSocket support

2. **Daphne ASGI Server** (HTTP + WebSocket)
   ```bash
   make run-backend-ws
   # or
   daphne -b 0.0.0.0 -p 8000 server.asgi:application
   ```
   - Port: 8000
   - Features: HTTP API + WebSocket support
   - Single server handles both protocols

3. **Dual Server Mode** (Recommended for Development)
   ```bash
   make run-backend-ws-dual
   ```
   - Django Dev Server: Port 8000 (HTTP API with large file uploads)
   - Daphne: Port 8001 (WebSocket connections)
   - Best of both worlds: file upload support + WebSocket

## CORS Configuration

### Development Settings

In `backend/server/settings.py`:

```python
# Allow frontend development server
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",  # Vite dev server
    "http://localhost:3000",  # Alternative dev port
    "http://localhost:8000",  # Django
]

# For development, you can also use:
CORS_ALLOW_ALL_ORIGINS = True  # Only in DEBUG mode!

# Allow credentials for authentication
CORS_ALLOW_CREDENTIALS = True

# Allowed headers
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]
```

### Production Settings

```python
# Specific allowed origins
CORS_ALLOWED_ORIGINS = [
    "https://yourdomain.com",
    "https://app.yourdomain.com",
]

# Never use CORS_ALLOW_ALL_ORIGINS in production!
CORS_ALLOW_ALL_ORIGINS = False

# Ensure credentials are handled properly
CORS_ALLOW_CREDENTIALS = True
```

## WebSocket Routing

### ASGI Configuration

In `backend/server/asgi.py`:

```python
import os
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.core.asgi import get_asgi_application
import dashboard.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'server.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            dashboard.routing.websocket_urlpatterns
        )
    ),
})
```

### WebSocket URL Patterns

WebSocket endpoints are defined in each app's `routing.py`:

```python
# dashboard/routing.py
from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/unified-dashboard/$', consumers.UnifiedDashboardConsumer.as_asgi()),
    re_path(r'ws/agent-orchestra/$', consumers.AgentOrchestraConsumer.as_asgi()),
    re_path(r'ws/stock-intelligence/$', consumers.StockIntelligenceConsumer.as_asgi()),
    # ... other WebSocket routes
]
```

## Environment Variables

Create a `.env` file in the backend directory:

```env
# Django Settings
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DATABASE_URL=postgresql://user:password@localhost:5432/dbname

# Redis (for Channels and Celery)
REDIS_URL=redis://localhost:6379/0

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# External APIs
POLYGON_API_KEY=your-polygon-key
OPENAI_API_KEY=your-openai-key

# File Upload Settings
FILE_UPLOAD_MAX_MEMORY_SIZE=524288000  # 500MB
DATA_UPLOAD_MAX_MEMORY_SIZE=524288000  # 500MB
```

## Required Services

### Redis
Required for WebSocket support and Celery background tasks:
```bash
# Start Redis
redis-server

# Or use Docker
docker run -d -p 6379:6379 redis:alpine
```

### PostgreSQL
Main database:
```bash
# Using Docker
docker run -d -p 5432:5432 \
  -e POSTGRES_USER=postgres \
  -e POSTGRES_PASSWORD=postgres \
  -e POSTGRES_DB=moveyourass \
  postgres:15-alpine
```

### Celery Worker
For background tasks:
```bash
# Start Celery worker
celery -A server worker -l info

# Or use make command
make celery-start
```

## Authentication

### Token Authentication
The API uses JWT tokens for authentication:

```python
# In settings.py
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
}
```

### WebSocket Authentication
WebSockets authenticate via token in query parameters:
```
ws://localhost:8001/ws/endpoint/?token=your-jwt-token
```

## File Upload Configuration

For large file uploads (up to 500MB):

```python
# In settings.py
FILE_UPLOAD_MAX_MEMORY_SIZE = 524288000  # 500MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 524288000  # 500MB

# Temporary file handling
FILE_UPLOAD_TEMP_DIR = os.path.join(BASE_DIR, 'tmp')
```

## Monitoring and Debugging

### Debug WebSocket Connections
```python
# Enable Channels debug logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django.channels': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}
```

### Check Service Status
```bash
# Check all services
make status

# Check specific service
ps aux | grep daphne
ps aux | grep celery
redis-cli ping
```

## Troubleshooting

### WebSocket Connection Issues

1. **404 Not Found**
   - Check WebSocket routing configuration
   - Ensure URL pattern matches frontend

2. **Connection Refused**
   - Verify Daphne is running on correct port
   - Check firewall settings

3. **Authentication Failed**
   - Ensure token is valid and not expired
   - Check token is passed in query parameters

### CORS Issues

1. **Blocked by CORS Policy**
   - Add frontend URL to `CORS_ALLOWED_ORIGINS`
   - Ensure `CORS_ALLOW_CREDENTIALS = True`

2. **Preflight Request Failed**
   - Check `CORS_ALLOW_HEADERS` includes required headers
   - Verify OPTIONS requests are handled

### Large File Upload Issues

1. **413 Request Entity Too Large**
   - Increase `FILE_UPLOAD_MAX_MEMORY_SIZE`
   - Check nginx/proxy settings if applicable

2. **Connection Reset**
   - Increase timeout settings
   - Use Django dev server for large uploads

## Production Deployment

### Gunicorn + Daphne Setup

```bash
# HTTP API with Gunicorn
gunicorn server.wsgi:application --bind 0.0.0.0:8000

# WebSocket with Daphne
daphne -b 0.0.0.0:8001 server.asgi:application
```

### Nginx Configuration

```nginx
# HTTP API proxy
location /api {
    proxy_pass http://localhost:8000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
}

# WebSocket proxy
location /ws {
    proxy_pass http://localhost:8001;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
}
```

### Docker Deployment

See `docker-compose.yml` for production-ready configuration with:
- Django backend
- Daphne for WebSockets
- PostgreSQL database
- Redis cache
- Celery workers
- Nginx proxy
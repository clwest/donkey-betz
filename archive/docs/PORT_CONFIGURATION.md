# 🚀 UNIFIED DONKEY BETZ - PORT CONFIGURATION

## ✅ CORRECT PORT CONFIGURATION

Based on the Makefile and actual system setup:

```bash
BACKEND_PORT := 8000           # Django + Daphne (HTTP + WebSocket)
WEBSOCKET_PORT := 8000         # Same port - Daphne handles both
FRONTEND_PORT := 3000          # React frontend
REDIS_PORT := 6379            # Redis cache
POSTGRES_PORT := 5432         # PostgreSQL database
```

## 🔧 KEY INSIGHT

**Daphne handles BOTH HTTP and WebSocket on port 8000**

This is the standard Django Channels configuration where:
- Regular HTTP requests: `http://localhost:8000/`
- WebSocket connections: `ws://localhost:8000/ws/`

Both are served by the same Daphne ASGI server on port 8000.

## 📋 SERVICE ENDPOINTS

| Service | URL | Port | Notes |
|---------|-----|------|-------|
| Django Backend | http://localhost:8000 | 8000 | API endpoints |
| Admin Panel | http://localhost:8000/admin | 8000 | Django admin |
| API Docs | http://localhost:8000/api/docs | 8000 | API documentation |
| WebSocket | ws://localhost:8000/ws/ | 8000 | Real-time updates |
| React Frontend | http://localhost:3000 | 3000 | User interface |

## 🚀 STARTING THE PLATFORM

### Option 1: Using Makefile (Recommended)
```bash
# This starts everything with correct ports
make unified-dev
```

### Option 2: Manual Start
```bash
# Terminal 1 - Backend with WebSocket support
python manage.py runserver 8000
# OR for full WebSocket support:
daphne -b 0.0.0.0 -p 8000 ai_core.asgi:application

# Terminal 2 - Frontend
cd frontend && npm run dev

# Terminal 3 - Celery (optional)
celery -A celery_app worker --loglevel=info
```

## ⚠️ IMPORTANT NOTES

1. **NO SEPARATE WEBSOCKET SERVER** - WebSockets run on the same port as Django (8000)
2. **DAPHNE PREFERRED** - Use Daphne instead of runserver for full WebSocket support
3. **SINGLE PORT SIMPLICITY** - Having HTTP and WebSocket on the same port simplifies:
   - CORS configuration
   - Firewall rules
   - Reverse proxy setup
   - Docker configuration

## 🔍 TESTING WEBSOCKET CONNECTION

```python
# Test WebSocket connection on port 8000
import asyncio
import websockets
import json

async def test_ws():
    uri = "ws://localhost:8000/ws/"
    async with websockets.connect(uri) as websocket:
        await websocket.send(json.dumps({"type": "ping"}))
        response = await websocket.recv()
        print(f"Response: {response}")

asyncio.run(test_ws())
```

## 📝 ENVIRONMENT VARIABLES

Make sure your `.env` file has:
```env
BACKEND_URL=http://localhost:8000
WEBSOCKET_URL=ws://localhost:8000
```

## 🐳 DOCKER CONFIGURATION

If using Docker, the same port configuration applies:
```yaml
services:
  backend:
    ports:
      - "8000:8000"  # Both HTTP and WebSocket
```

## ✅ SUMMARY

- **Port 8000**: Django + WebSocket (via Daphne)
- **Port 3000**: React Frontend
- **Port 8001**: NOT USED (ignore any references to this)

The platform uses Daphne as the ASGI server which handles both HTTP and WebSocket connections on the same port (8000), which is the modern, recommended approach for Django Channels applications.

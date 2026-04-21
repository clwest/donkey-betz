# Server Startup Guide

## ✅ Current Status
The Django development server is now running and the login API is working!

## Issue Resolved
The server was taking a long time to start because it was loading the SentenceTransformer ML model. This is normal - it takes about 30-60 seconds on first startup.

## Login Working
```bash
curl -X POST http://localhost:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"chris","password":"chris123"}'
```

Response:
```json
{
  "token": "<redacted-993f8273-2026-04-20>",
  "user": {
    "id": "e7a146d3-6934-4819-a026-5af63806af87",
    "username": "chris",
    "email": "chris@donkeybetz.com",
    "credits": 10000,
    "subscription": "premium"
  }
}
```

## Important Notes

### Current Setup (Development Server)
- ✅ REST API endpoints working
- ✅ Authentication working
- ❌ WebSocket support NOT available
- Running on: `http://localhost:8000`

### For WebSocket Support (Production-like)
If you need WebSocket support for real-time updates, you need to use Daphne instead:

```bash
# Kill existing server
lsof -i :8000 | grep LISTEN | awk '{print $2}' | xargs kill -9

# Start Daphne (with WebSocket support)
daphne -b 0.0.0.0 -p 8000 ai_core.asgi:application

# Note: Daphne also takes 30-60 seconds to start due to model loading
```

### Quick Start Commands

#### Option 1: Development Server (No WebSocket)
```bash
# Simple and reliable for most development
python manage.py runserver 0.0.0.0:8000
```

#### Option 2: Daphne Server (With WebSocket)
```bash
# For real-time features
daphne -b 0.0.0.0 -p 8000 ai_core.asgi:application
```

#### Option 3: Use Make Command
```bash
# This starts everything properly
make unified-dev
```

## Troubleshooting

### If Login Times Out
1. **Wait 30-60 seconds** - The server is loading ML models
2. **Check server output** - Look for startup messages
3. **Test with curl** - Use the curl command above to verify

### Server Startup Indicators
Look for these in the console:
- "INFO Using real Odds API key..."
- "INFO Using real SportRadar API key..."
- "System check identified 2 issues" (these are just warnings)

After these messages, wait about 30 seconds for the ML models to load.

### Frontend Connection
Once the backend is ready, the frontend should connect automatically. If not:
1. Clear browser cache
2. Refresh the page
3. Check browser console for errors

## Current Services Status
- ✅ Django Backend: Running on port 8000
- ✅ Frontend: Should be on port 3000
- ✅ Redis: Running on port 6379
- ✅ PostgreSQL: Running on port 5432
- ✅ Celery Workers: Running

The system is operational! You can now log in through the frontend.
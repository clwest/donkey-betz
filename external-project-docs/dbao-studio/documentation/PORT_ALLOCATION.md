# DBAO Unified Platform - Port Allocation Map

## Port Conflicts Resolved ✅

### Previous Conflicts
- **ai-content-studio**: Backend port 8001, React port 8080
- **donkey-betz-agent-orchestra**: Backend port 8000, no dedicated React
- **Both projects**: Trying to manage separate Redis instances on 6379

### Unified Port Allocation

| Service | Port | Purpose | Primary Project | Notes |
|---------|------|---------|-----------------|-------|
| **Redis** | 6379 | Cache & Channels | Shared | Single instance for both projects |
| **DBAO Backend** | 8000 | Daphne ASGI + WebSocket | DBAO | Primary backend with unified routing |
| **AIC Backend** | 8001 | Django runserver | AI Content Studio | Optional, for separate operation |
| **React Frontend** | 5173 | Vite dev server | AI Content Studio | Unified UI for both projects |
| **React Alt** | 8080 | Alternative React | AI Content Studio | Backup port if 5173 conflicts |

## Service Dependencies

```
Redis (6379)
└── DBAO Backend (8000)
    ├── Daphne ASGI Server
    ├── Django REST API
    ├── WebSocket Consumers
    ├── Celery Workers
    └── Celery Beat Scheduler
└── React Frontend (5173)
    ├── Points to DBAO Backend API
    ├── Connects to DBAO WebSocket
    └── Unified UI for both projects
```

## WebSocket Routing (Unified)

### DBAO Routes (Primary)
- `ws://localhost:8000/ws/assistant/` - DBAO Assistant with ping/pong
- `ws://localhost:8000/ws/agents/` - Agent execution updates
- `ws://localhost:8000/ws/dashboard/` - Dashboard real-time data
- `ws://localhost:8000/ws/sports/` - Sports betting updates
- `ws://localhost:8000/ws/unified/` - Combined sports + agent updates
- `ws://localhost:8000/ws/echo/` - Test echo consumer

### AI Content Studio Routes (Aliased)
- `ws://localhost:8000/ws/aic-assistant/` - AIC Assistant consumer
- `ws://localhost:8000/ws/aic-agents/` - AIC Agents consumer

## Environment Variables

### React Frontend (.env)
```bash
VITE_API_URL=http://localhost:8000/api
VITE_WS_URL=ws://localhost:8000
```

### DBAO Backend (.env)
```bash
REDIS_URL=redis://localhost:6379/0
CHANNEL_LAYERS_HOST=127.0.0.1
CHANNEL_LAYERS_PORT=6379
```

## Startup Sequence

1. **Redis** starts on port 6379
2. **DBAO Backend** starts Daphne ASGI on port 8000
3. **Celery Workers** start in background
4. **React Frontend** starts on port 5173 pointing to DBAO backend
5. **Health checks** verify all services are operational

## Commands

### Unified Platform
```bash
# Start everything
make -f Makefile.unified unified-platform

# Check status
make -f Makefile.unified status

# Run smoke tests
make -f Makefile.unified smoke-test

# Stop everything
make -f Makefile.unified unified-stop
```

### Individual Services
```bash
# DBAO backend only
make -f Makefile.unified dbao-only

# React frontend only  
make -f Makefile.unified react-only

# Port management
make -f Makefile.unified port-check
make -f Makefile.unified port-kill-all
```

## Verification Checklist

- [ ] Redis accessible on 6379
- [ ] DBAO backend responds on 8000/api/health/
- [ ] WebSocket connects to 8000/ws/assistant/ with ping/pong
- [ ] React app loads on 5173
- [ ] API calls from React go to DBAO backend
- [ ] WebSocket messages flow between React and DBAO
- [ ] No port conflicts detected
- [ ] All services start cleanly

## Troubleshooting

### Port Conflicts
```bash
# Check what's using ports
lsof -i :6379,8000,8001,5173

# Kill processes on specific ports
lsof -ti:8000 | xargs kill -9
```

### Service Issues
```bash
# Check logs
tail -f /tmp/dbao-unified.log
tail -f /tmp/react-unified.log
tail -f /tmp/celery-worker.log

# Test connectivity
curl http://localhost:8000/api/health/
redis-cli ping
```

### WebSocket Problems
```bash
# Test WebSocket with wscat
wscat -c ws://localhost:8000/ws/assistant/

# Send ping, expect pong
{"type":"ping"}
```

This unified configuration eliminates all port conflicts and provides a single interface for managing both projects.
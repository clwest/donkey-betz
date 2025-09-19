# 🔧 WEBSOCKET FIX FOR MAKE UNIFIED-DEV

## The Problem
When you run `make unified-dev`, it's falling back to Django's `runserver` instead of using Daphne, which means WebSockets won't work. 

The issue is in the Makefile's `_start-backend` target:
1. It tries to run Daphne with `core.asgi:application` (wrong module)
2. When that fails, it falls back to `runserver` (no WebSocket support)

## Solutions

### Solution 1: Quick Fix - Use Daphne Directly
Stop the current server and run Daphne manually:
```bash
# Stop everything
make unified-stop

# Start Daphne with correct module
daphne -b 0.0.0.0 -p 8000 backend.asgi:application
```

### Solution 2: Fixed Make Command
Create a new Makefile target that uses Daphne correctly:

```bash
# Add this to your Makefile
unified-dev-ws: ## Start development with WebSocket support
	@echo "Starting with WebSocket support..."
	@make unified-stop
	@make _start-infrastructure
	@echo "Starting Daphne..."
	@daphne -b 0.0.0.0 -p 8000 backend.asgi:application &
	@echo "Starting frontend..."
	@cd frontend && npm run dev &
	@wait
```

### Solution 3: Fix the Makefile
Edit your Makefile and change line 221 from:
```makefile
# WRONG:
@cd $(PWD) && $(ACTIVATE) && daphne -b 0.0.0.0 -p $(BACKEND_PORT) core.asgi:application 2>/dev/null || \

# CORRECT:
@cd $(PWD) && $(ACTIVATE) && daphne -b 0.0.0.0 -p $(BACKEND_PORT) backend.asgi:application 2>/dev/null || \
```

## Testing WebSocket After Fix

Run the updated test script:
```bash
python test_websocket_fixed.py
```

You should see:
- ✅ Connected successfully! (not HTTP 500 errors)
- Server running with Daphne

## Using the Smart Startup Script

For the most reliable WebSocket support:
```bash
chmod +x start_smart.sh
./start_smart.sh
```

This ensures proper startup sequence and health checks.

## Summary

The issue is that `make unified-dev` is using Django's `runserver` instead of Daphne because:
1. The Makefile has the wrong ASGI module path (`core.asgi` instead of `backend.asgi`)
2. When Daphne fails, it silently falls back to runserver

**Immediate fix:** Just run Daphne directly:
```bash
daphne -b 0.0.0.0 -p 8000 backend.asgi:application
```

Your WebSockets will work immediately! 🚀

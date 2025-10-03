# Service Startup Guide for Debugging

## Current Status
All services have been successfully stopped:
- ✅ Django servers stopped
- ✅ Celery workers stopped  
- ✅ Redis stopped (via `brew services stop redis`)
- ✅ No remaining processes

## Starting Services for Debugging

### Option 1: Start Everything at Once
```bash
cd backend
make run-backend
```
This will start Django, Redis, and Celery together.

### Option 2: Start Services Individually (Recommended for Debugging)

#### 1. Start Redis First
```bash
# Option A: Using brew services (background)
brew services start redis

# Option B: Run in foreground to see logs
redis-server
```

#### 2. Start Django Development Server
```bash
cd backend
source .venv/bin/activate  # or source ../.venv/bin/activate
python manage.py runserver
```

#### 3. Start Celery Worker
Open a new terminal:
```bash
cd backend
source .venv/bin/activate
celery -A server worker -l info
```

## Debugging the AI Assistant Error

### Check Logs in Order:
1. **Redis logs**: Should show connections being established
2. **Django logs**: Look for any API errors or authentication issues
3. **Celery logs**: Check for task execution errors

### Common AI Assistant Issues:
1. **Missing API keys**: Check `.env` for OPENAI_API_KEY
2. **Redis connection**: Ensure Redis is running before Celery
3. **WebSocket errors**: Check if Daphne/Channels is configured
4. **Memory/RAG errors**: Check if embeddings are populated

### Useful Debug Commands:
```bash
# Check Redis is responding
redis-cli ping

# Check Django can connect to Redis
python manage.py shell
>>> from django.core.cache import cache
>>> cache.set('test', 'value')
>>> cache.get('test')

# Check Celery can connect
celery -A server inspect active

# View real-time logs
tail -f logs/django.log
tail -f logs/celery.log
tail -f logs/errors.log
```

### AI Assistant Specific Tests:
```bash
# Test AI service directly
python manage.py shell
>>> from agent_orchestra.services.ai_service import AIService
>>> ai = AIService()
>>> response = ai.generate_response("Hello")
>>> print(response)
```

## Service Dependencies
1. Redis must start first
2. Django can start anytime
3. Celery requires Redis to be running

## Monitoring Services
```bash
# Check all running processes
ps aux | grep -E "(redis|celery|python.*manage|python.*runserver)" | grep -v grep

# Check service status
make status
```

## Stopping Services Again
```bash
# Stop everything
make stop-services

# Or use the shutdown script
./shutdown_all_services.sh
```
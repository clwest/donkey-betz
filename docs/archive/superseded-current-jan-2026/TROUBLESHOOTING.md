<!-- ARCHIVED-DOC-V1 -->
> # ⛔ ARCHIVED — 2026-04-26 (Session 1100)
>
> This doc was retired during the Session 1099 → 1100 doc-drift cleanup
> because its stats diverged materially from runtime reality. **Content
> below is preserved unchanged for historical reference and potential
> future book material** (Chris's "how I learned to work with AI to build
> this platform").
>
> **What this used to be:** Troubleshooting playbook
>
> **Where to look now:**
> - [docs/topics/celery-workers.md](/docs/topics/celery-workers.md)
> - [CLAUDE.md (Troubleshooting section)](/CLAUDE.md (Troubleshooting section))
>
> **Source of truth for live numbers:** `docs/PLATFORM_INVENTORY.md`
> (regenerable via `python manage.py generate_platform_inventory`).

---

# Troubleshooting Guide

**Last Updated:** January 2026

---

## Table of Contents

1. [Quick Diagnostics](#quick-diagnostics)
2. [Common Issues](#common-issues)
3. [Service-Specific Issues](#service-specific-issues)
4. [Database Issues](#database-issues)
5. [Celery Issues](#celery-issues)
6. [Discord Bot Issues](#discord-bot-issues)
7. [DaVinci Resolve Issues](#davinci-resolve-issues)
8. [Performance Issues](#performance-issues)

---

## Quick Diagnostics

### Full System Health Check
```bash
# Platform health
curl http://localhost:8000/health/ping/

# Detailed status
curl http://localhost:8000/health/status/

# Database check
.venv/bin/python manage.py shell -c "
from django.db import connection
cursor = connection.cursor()
cursor.execute('SELECT 1')
print('Database: OK')
"

# Redis check
redis-cli ping

# Celery check
celery -A core inspect active
```

### Quick Restart
```bash
# Kill all services
pkill -f daphne
pkill -f celery
pkill -f redis-server

# Clean PID files
rm -f .daphne.pid .celery.pid .celery-beat.pid

# Restart
make start
make celery
```

---

## Common Issues

### 1. "Server not responding" / Connection Refused

**Symptoms:**
- Can't access http://localhost:8000
- curl returns "Connection refused"

**Causes:**
- Daphne not running
- Port already in use
- Redis not running

**Solutions:**
```bash
# Check if Daphne is running
ps aux | grep daphne

# Check port usage
lsof -i :8000

# Kill existing process and restart
pkill -f daphne
make start
```

### 2. "Database connection failed"

**Symptoms:**
- Server starts but pages show database errors
- `OperationalError: could not connect to server`

**Solutions:**
```bash
# Check PostgreSQL status
pg_isready

# Start PostgreSQL (macOS)
brew services start postgresql

# Test connection
psql -U postgres -c "SELECT 1"

# Check Django settings
python manage.py check --database default
```

### 3. "Redis connection refused"

**Symptoms:**
- Celery won't start
- WebSocket errors
- Session issues

**Solutions:**
```bash
# Start Redis
redis-server --daemonize yes

# Or via brew
brew services start redis

# Verify
redis-cli ping  # Should return PONG
```

### 4. "Module not found" Errors

**Symptoms:**
- `ModuleNotFoundError: No module named 'xxx'`

**Solutions:**
```bash
# Activate virtual environment
source .venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt

# Specific module
pip install <module_name>
```

### 5. "Migration errors"

**Symptoms:**
- `django.db.utils.ProgrammingError`
- Missing tables

**Solutions:**
```bash
# Run migrations
python manage.py migrate

# If stuck, check migration status
python manage.py showmigrations

# Reset specific app (DANGER: loses data)
python manage.py migrate <app> zero
python manage.py migrate <app>
```

---

## Service-Specific Issues

### Agent Execution Failures

**Symptoms:**
- Agent returns empty result
- "Agent not found" error

**Solutions:**
```python
# Check agent is registered
from core.agent_router import AgentRouter
router = AgentRouter()
print(list(router.AGENT_MAP.keys()))

# Test agent directly
from core.agents import get_image_agent
agent = get_image_agent(user=None)
result = agent.execute("test task", {}, {}, {})
print(result)
```

### Spider Collection Failures

**Symptoms:**
- No new spider data
- Spider errors in logs

**Solutions:**
```python
# Run spider manually
from ai_core.spiders.spider_registry import SpiderRegistry
registry = SpiderRegistry()
spider = registry.get_spider('hackernews')
data = spider.collect_data()
print(f"Collected: {len(data)} records")

# Check API keys
import os
print(os.getenv('NEWS_API_KEY'))
print(os.getenv('POLYGON_API_KEY'))
```

### OpenAI API Errors

**Symptoms:**
- "RateLimitError"
- "InvalidRequestError"
- "AuthenticationError"

**Solutions:**
```bash
# Check API key
echo $OPENAI_API_KEY

# Test API
python -c "
import openai
client = openai.OpenAI()
response = client.chat.completions.create(
    model='gpt-4o-mini',
    messages=[{'role': 'user', 'content': 'test'}]
)
print(response.choices[0].message.content)
"
```

**Note:** GPT-5-mini uses `max_completion_tokens`, not `max_tokens`.

---

## Database Issues

### Slow Queries

**Diagnosis:**
```python
# Check slow queries
from django.db import connection
print(connection.queries[-10:])
```

**Solutions:**
```bash
# Add indexes (example)
python manage.py shell -c "
from django.db import connection
cursor = connection.cursor()
cursor.execute('CREATE INDEX idx_spider_data_category ON core_spiderdata(category)')
"

# Vacuum database
psql -U postgres -d your_db -c "VACUUM ANALYZE"
```

### Database Locks

**Symptoms:**
- Queries hang indefinitely
- "deadlock detected"

**Solutions:**
```sql
-- View locks (in psql)
SELECT * FROM pg_locks WHERE NOT granted;

-- Kill blocking query
SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE ...;
```

### Data Corruption

**Solutions:**
```bash
# Backup first!
pg_dump -U postgres your_db > backup.sql

# Check integrity
python manage.py check --database default

# Restore from backup if needed
psql -U postgres your_db < backup.sql
```

---

## Celery Issues

### Tasks Not Running

**Symptoms:**
- Tasks stuck in "PENDING"
- No workers visible

**Solutions:**
```bash
# Check workers
celery -A core inspect active

# Start workers manually
celery -A core worker -l info

# Check Beat scheduler
celery -A core beat -l info

# Purge stuck tasks
celery -A core purge
```

### Memory Leaks in Workers

**Symptoms:**
- Workers consuming increasing memory
- OOM kills

**Solutions:**
```bash
# Restart workers with max tasks limit
celery -A core worker --max-tasks-per-child=100

# Or in celery.py:
app.conf.worker_max_tasks_per_child = 100
```

### Beat Schedule Not Running

**Symptoms:**
- Scheduled tasks not executing
- Beat log shows no activity

**Solutions:**
```bash
# Check beat is running
ps aux | grep celery-beat

# Check schedule in database
python manage.py shell -c "
from django_celery_beat.models import PeriodicTask
print(PeriodicTask.objects.filter(enabled=True).count())
"

# Restart beat
pkill -f celery-beat
celery -A core beat -l info
```

---

## Discord Bot Issues

### Bot Not Responding

**Symptoms:**
- Commands timeout
- Bot shows offline

**Solutions:**
```bash
# Check bot process
ps aux | grep discord

# Check token
echo $DISCORD_BOT_TOKEN

# Restart bot
python manage.py run_discord_bot
```

### Commands Not Syncing

**Symptoms:**
- Slash commands not appearing
- "Unknown command" errors

**Solutions:**
```python
# Force sync commands
from core.services.discord_bot import bot
await bot.tree.sync()
```

### Voice Features Not Working

**Symptoms:**
- Bot won't join voice channel
- No audio playback

**Solutions:**
- Install FFmpeg: `brew install ffmpeg`
- Check bot permissions in Discord server
- Verify ElevenLabs API key

---

## DaVinci Resolve Issues

### "DaVinci Resolve not available"

**Solutions:**
```bash
# Start DaVinci Resolve
open -a "DaVinci Resolve"

# Wait for full load, then start resolve_node
cd resolve_node
python app.py
```

### "Could not connect to Resolve"

**Solutions:**
- Ensure **Studio** version (free version lacks API)
- Check Python path includes Resolve modules:
  ```
  /Library/Application Support/Blackmagic Design/DaVinci Resolve/Developer/Scripting/Modules
  ```

### Render Jobs Never Complete

**Solutions:**
```bash
# Check render presets exist
# In Resolve: Deliver page → check "H.264 Master" exists

# Run in mock mode for testing
MOCK_MODE=true python app.py
```

---

## Performance Issues

### Slow API Responses

**Diagnosis:**
```python
# Profile view
from django.db import reset_queries
reset_queries()

# ... call view ...

from django.db import connection
print(f"Queries: {len(connection.queries)}")
```

**Solutions:**
- Add `select_related()` / `prefetch_related()`
- Add database indexes
- Cache frequent queries

### High Memory Usage

**Diagnosis:**
```bash
# Check process memory
ps aux --sort=-%mem | head -10

# Python memory profiling
pip install memory_profiler
python -m memory_profiler your_script.py
```

**Solutions:**
- Use iterators instead of loading full querysets
- Clear Django querysets after use
- Increase worker recycling

### WebSocket Disconnections

**Symptoms:**
- Frequent reconnections
- "Connection closed abnormally"

**Solutions:**
```bash
# Increase timeout in Daphne
daphne -b 0.0.0.0 -p 8000 --websocket_timeout 300 core.asgi:application

# Check Redis connection pool
python -c "
import redis
r = redis.Redis()
print(r.info('clients'))
"
```

---

## Logs

### Key Log Locations

| Service | Location |
|---------|----------|
| Django | stdout / `django.log` |
| Celery | stdout / `celery.log` |
| resolve_node | `resolve_node/logs/` |
| Discord Bot | stdout |

### Enable Debug Logging

```python
# In settings.py
LOGGING = {
    'version': 1,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'core': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}
```

---

## Getting Help

1. Check this troubleshooting guide
2. Search session handoffs in `docs/handoffs/`
3. Review `CLAUDE.md` for recent changes
4. Check `00-START-NEXT-SESSION.md` for known issues

---

## Related Documentation

- [INDEX.md](INDEX.md) - System overview
- [CELERY_TASKS.md](CELERY_TASKS.md) - Task details
- [DAVINCI_RESOLVE.md](../DAVINCI_RESOLVE.md) - Resolve troubleshooting

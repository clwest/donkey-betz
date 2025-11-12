# 🔧 Unified Donkey Betz - Debugging Guide

**Last Updated**: September 30, 2025
**Platform**: Unified AI Studio + DBAO
**Reality Score**: 98.5%

---

## 📋 Table of Contents

1. [Diagnostic Endpoints](#diagnostic-endpoints)
2. [Common Issues](#common-issues)
3. [Advanced Debugging](#advanced-debugging)
4. [Performance Monitoring](#performance-monitoring)
5. [Error Tracking](#error-tracking)

---

## 🔍 Diagnostic Endpoints

### 1. Master Diagnostic API

**URL**: `GET http://localhost:8000/api/diagnostics/`

**Purpose**: Complete system health snapshot

**Returns**:
```json
{
  "timestamp": "2025-09-30T...",
  "spider_system": {
    "status": "active|error",
    "spiders_found": 5,
    "sample_opportunities": [...],
    "platforms_active": ["Toptal", "Guru", "Flexjobs", "RemoteOK", "PeoplePerHour"]
  },
  "income_builder": {
    "status": "active|error",
    "opportunities_found": 10,
    "connected_to_spiders": true|false
  },
  "monetization_engine": {
    "status": "active|error",
    "can_record_earnings": true|false
  },
  "websocket_consumers": {
    "decision_command": {...},
    "consciousness_stream": {...}
  },
  "redis_data": {
    "connected": true|false,
    "total_keys": 1052,
    "databases_used": [0, 1, 2]
  },
  "database_stats": {
    "connected": true|false,
    "migrations_applied": 89,
    "sample_tables": [...]
  },
  "agent_registry": {
    "total_agents": 149,
    "total_advisors": 25
  },
  "summary": {
    "reality_score": "75%",
    "total_errors": 2,
    "systems_operational": 6,
    "recommendations": [...]
  },
  "errors": [...]
}
```

**What to Check**:
- ✅ `summary.reality_score` >= 80%
- ✅ `summary.total_errors` = 0
- ✅ All `status` fields = "active"
- ✅ `redis_data.connected` = true
- ✅ `database_stats.connected` = true

---

### 2. Visual Diagnostic Dashboard

**URL**: `http://localhost:8000/diagnostics/`

**Features**:
- Real-time system status monitoring
- WebSocket connection testing
- Spider network testing
- Live data flow visualization
- Error tracking and recommendations

**Usage**:
1. Open dashboard
2. Check Reality Score (top center)
3. Scan for red error indicators
4. Review recommendations section
5. Use "Test" buttons to verify components

---

### 3. Spider Network Test

**URL**: `POST http://localhost:8000/api/diagnostics/test-spiders/`

**Request**:
```json
{
  "profile": {
    "skills": ["Python", "Django", "React"],
    "skill_level": "intermediate",
    "available_hours": 20
  }
}
```

**Response**:
```json
{
  "success": true,
  "opportunities_found": 15,
  "data": {
    "opportunities": [...],
    "platforms": [...],
    "timestamp": "..."
  }
}
```

**Debugging**:
- If `success: false` → Check spider imports
- If `opportunities_found: 0` → Check API keys
- If platforms missing → Check spider configuration

---

### 4. Income Builder Test

**URL**: `POST http://localhost:8000/api/diagnostics/test-income-builder/`

**Request**:
```json
{
  "skills": ["Python", "Django"],
  "skill_level": "intermediate",
  "available_hours": 20
}
```

**Response**:
```json
{
  "success": true,
  "opportunities_found": 10,
  "data": [...]
}
```

**Debugging**:
- If not connected to spiders → Check `income_builder.py` imports
- If opportunities empty → Verify spider network active
- If TypeError → Check async/sync context

---

### 5. WebSocket Test Page

**URL**: `http://localhost:8000/diagnostics/websocket-test/`

**Features**:
- Manual WebSocket connection control
- Custom message sending
- Real-time message monitoring
- Connection status display

**Test Steps**:
1. Click "Connect"
2. Wait for "Connected" status
3. Send test message
4. Verify response received
5. Check message log

**Common Issues**:
- Connection fails → Check Redis running
- No messages → Check channel layer config
- Disconnects quickly → Check timeout settings

---

## 🐛 Common Issues

### Issue 1: Spider System Error

**Symptoms**:
```json
{
  "spider_system": {
    "status": "error",
    "error": "ModuleNotFoundError"
  }
}
```

**Causes**:
1. Spider module not imported correctly
2. Missing dependencies
3. API credentials not configured

**Fixes**:
```bash
# Check imports
python manage.py shell << 'EOF'
from intelligence import income_spider_orchestrator
print("✅ Spiders import successfully")
EOF

# Check dependencies
pip install -r requirements.txt

# Check API keys
echo $TOPTAL_API_KEY
echo $GURU_API_KEY
```

---

### Issue 2: Income Builder Not Connected

**Symptoms**:
```json
{
  "income_builder": {
    "connected_to_spiders": false
  }
}
```

**Causes**:
1. `spider_orchestrator` attribute missing
2. Async/sync mismatch
3. Import path incorrect

**Fix**:
```python
# intelligence/income_builder.py
from intelligence.income_spider_orchestrator import IncomeSpiderOrchestrator

class AIIncomeBuilder:
    def __init__(self):
        self.spider_orchestrator = IncomeSpiderOrchestrator()

    def find_opportunities(self, skills, skill_level, available_hours):
        # Synchronous wrapper for async spider calls
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        opportunities = loop.run_until_complete(
            self.spider_orchestrator.find_opportunities(...)
        )
        loop.close()
        return opportunities
```

---

### Issue 3: WebSocket Disconnections

**Symptoms**:
- Connection drops after 30-60 seconds
- "Connection closed unexpectedly" errors
- Frontend shows "Disconnected" status

**Causes**:
1. Redis timeout too short
2. No TCP keepalive configured
3. Channel capacity exceeded

**Fixes**:

**1. Update Redis Configuration**:
```python
# ai_core/settings.py
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [('127.0.0.1', 6379)],
            "capacity": 1000,
            "expiry": 60,
        },
    },
}
```

**2. Enable Redis Keepalive**:
```bash
# Via diagnostic endpoint (auto-applies)
curl -X POST http://localhost:8000/api/diagnostics/optimize-websocket/

# Or manually via Redis CLI
redis-cli CONFIG SET timeout 0
redis-cli CONFIG SET tcp-keepalive 60
```

**3. Clear Stale Connections**:
```bash
redis-cli --scan --pattern "websocket:*:stale" | xargs redis-cli DEL
```

---

### Issue 4: Agent Execution Fails

**Symptoms**:
```json
{
  "success": false,
  "error": "OpenAI API error"
}
```

**Causes**:
1. API key not configured
2. Rate limit exceeded
3. Invalid model name
4. Insufficient credits

**Debugging**:
```python
# Check API key
import os
from openai import OpenAI

key = os.getenv('OPENAI_API_KEY')
print(f"API Key configured: {bool(key)}")
print(f"API Key starts with: {key[:10]}..." if key else "NOT SET")

# Test API call
client = OpenAI(api_key=key)

try:
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": "Test"}],
        max_tokens=10
    )
    print("✅ OpenAI API working")
except Exception as e:
    print(f"❌ API Error: {e}")
```

**Fixes**:
1. Set API key: `export OPENAI_API_KEY="sk-..."`
2. Check rate limits: Visit OpenAI dashboard
3. Verify model access: Ensure account has GPT-4 access
4. Add credits if needed

---

### Issue 5: Database Migration Errors

**Symptoms**:
```
django.db.migrations.exceptions.InconsistentMigrationHistory
```

**Causes**:
1. Migrations out of sync
2. Database reset without migration cleanup
3. Conflicting migrations

**Fixes**:
```bash
# Check migration status
python manage.py showmigrations

# Fake migrations if database is current
python manage.py migrate --fake core

# Reset migrations (WARNING: Deletes data)
python manage.py migrate core zero
python manage.py migrate

# Create new migration if needed
python manage.py makemigrations
python manage.py migrate
```

---

### Issue 6: Redis Connection Refused

**Symptoms**:
```
redis.exceptions.ConnectionError: Error 111 connecting to localhost:6379. Connection refused.
```

**Cause**: Redis server not running

**Fixes**:
```bash
# Check if Redis is running
redis-cli PING
# Expected: PONG

# If not running, start Redis
redis-server

# Or use make command
make start

# Check Redis logs
tail -f /var/log/redis/redis-server.log

# Verify port
netstat -an | grep 6379
```

---

## 🔬 Advanced Debugging

### Enable Verbose Logging

**Add to `ai_core/settings.py`**:
```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': 'debug.log',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'ai_core': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
        },
        'intelligence': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
        },
        'core': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
        },
    },
}
```

---

### Monitor Real-Time Logs

**Terminal 1 (Server)**:
```bash
python manage.py runserver
```

**Terminal 2 (Logs)**:
```bash
tail -f debug.log | grep ERROR
```

**Terminal 3 (Redis Monitor)**:
```bash
redis-cli MONITOR
```

---

### Test Individual Components

**Django Shell Testing**:
```python
python manage.py shell

# Test Income Builder
from intelligence.income_builder import AIIncomeBuilder
builder = AIIncomeBuilder()
opportunities = builder.find_opportunities(
    skills=['Python'],
    skill_level='intermediate',
    available_hours=20
)
print(f"Found {len(opportunities)} opportunities")

# Test Agent
from ai_core.models import Agent
from ai_core.agents.agent_executor import AgentExecutor
import asyncio

agent = Agent.objects.get(name='content_creator')
executor = AgentExecutor()

async def test():
    result = await executor.execute_agent(
        agent=agent,
        task={'task_description': 'Test task', 'context': {}}
    )
    print(result)

asyncio.run(test())
```

---

### Database Query Debugging

**Enable Query Logging**:
```python
# ai_core/settings.py
LOGGING['loggers']['django.db.backends'] = {
    'handlers': ['console'],
    'level': 'DEBUG',
}
```

**Check Slow Queries**:
```python
from django.db import connection
from django.db import reset_queries

reset_queries()

# Run your code here
# ...

queries = connection.queries
slow_queries = [q for q in queries if float(q['time']) > 0.1]

for query in slow_queries:
    print(f"Time: {query['time']}s")
    print(f"SQL: {query['sql'][:200]}")
    print("---")
```

---

## 📊 Performance Monitoring

### System Performance Metrics

**Check via Diagnostic API**:
```bash
curl http://localhost:8000/api/diagnostics/ | jq '.summary'
```

**Expected**:
- Agent Response Time: < 2 seconds
- WebSocket Latency: < 100ms
- Database Query Time: < 50ms average
- Redis Cache Hit Rate: 85%+
- Frontend Update Speed: < 200ms

---

### Redis Performance

**Check Redis Info**:
```bash
redis-cli INFO | grep -E "used_memory|hit_rate|connected_clients"
```

**Key Metrics**:
- `used_memory_human`: Should be < 100MB for normal operation
- `keyspace_hits`: Increments with cache hits
- `keyspace_misses`: Should be < 20% of hits
- `connected_clients`: Should match expected connections

---

### Database Performance

**Check Connection Pool**:
```python
from django.db import connection

print(f"Queries executed: {len(connection.queries)}")
print(f"Database: {connection.settings_dict['NAME']}")
print(f"Total time: {sum(float(q['time']) for q in connection.queries):.2f}s")
```

**Check Index Usage**:
```sql
-- In PostgreSQL
SELECT schemaname, tablename, indexname, idx_scan
FROM pg_stat_user_indexes
WHERE idx_scan = 0
ORDER BY schemaname, tablename;
```

---

## ❌ Error Tracking

### Common Error Patterns

#### 1. `TypeError: 'coroutine' object is not iterable`

**Cause**: Trying to iterate over async function without await

**Fix**:
```python
# Wrong
results = agent.execute_async(task)

# Correct
results = await agent.execute_async(task)

# Or in sync context
import asyncio
results = asyncio.run(agent.execute_async(task))
```

---

#### 2. `NoReverseMatch for 'url_name'`

**Cause**: URL name doesn't match `urls.py` pattern

**Debug**:
```python
# Show all URL patterns
python manage.py show_urls | grep partnership

# Check name in urls.py
# core/urls.py
path('partnership/project/<uuid:project_id>/',
     views.partnership_project_detail,
     name='partnership-project-detail'),  # Note: hyphens, not underscores
```

**Fix**: Use exact name from `urls.py` in `redirect()` or `reverse()`

---

#### 3. `UserAgentLearning() got unexpected keyword arguments`

**Cause**: Using field names that don't exist in model

**Debug**:
```python
# Check model fields
python manage.py shell << 'EOF'
from core.models_unified_system import UserAgentLearning
fields = [f.name for f in UserAgentLearning._meta.get_fields()]
print("Available fields:", fields)
EOF
```

**Fix**: Use correct field names (e.g., `learning_content` instead of `context_data`)

---

#### 4. `CSRF token missing or incorrect`

**Cause**: CSRF protection enabled but token not in form

**Debug**: Check browser Network tab → Request Headers → Look for `X-CSRFToken`

**Fix**:
```html
<!-- Add to template -->
<meta name="csrf-token" content="{{ csrf_token }}">

<!-- In JavaScript -->
<script>
const csrftoken = document.querySelector('[name=csrf-token]').content;
fetch('/api/endpoint/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrftoken
    },
    body: JSON.stringify(data)
});
</script>
```

---

### Error Log Analysis

**Find Recent Errors**:
```bash
tail -100 debug.log | grep ERROR

# Or with context
grep -A 5 -B 5 ERROR debug.log | tail -50
```

**Count Error Types**:
```bash
grep ERROR debug.log | awk '{print $4}' | sort | uniq -c | sort -rn
```

**Track Error Rate**:
```bash
# Errors per hour
grep ERROR debug.log | awk '{print $2}' | cut -d':' -f1 | uniq -c
```

---

## 🎯 Quick Troubleshooting Checklist

When something doesn't work:

1. ✅ Check diagnostic dashboard Reality Score
2. ✅ Verify Redis is running: `redis-cli PING`
3. ✅ Verify PostgreSQL is running: `psql -l`
4. ✅ Check server logs for errors: `tail -f debug.log`
5. ✅ Test WebSocket connection: `/diagnostics/websocket-test/`
6. ✅ Verify API keys configured: `env | grep API_KEY`
7. ✅ Check migrations applied: `python manage.py showmigrations`
8. ✅ Test database connection: `python manage.py dbshell`
9. ✅ Clear Redis cache: `redis-cli FLUSHALL` (careful!)
10. ✅ Restart everything: `make stop && make start`

---

## 📚 Related Documentation

- **Testing Guide**: `testing_guide.md`
- **System Architecture**: `../architecture/system_design.md`
- **WebSocket Architecture**: `../architecture/websocket_architecture.md`

---

**Debugging Guide Complete**
**Version**: 1.0
**Last Updated**: September 30, 2025
**Maintainer**: Unified Donkey Betz Team

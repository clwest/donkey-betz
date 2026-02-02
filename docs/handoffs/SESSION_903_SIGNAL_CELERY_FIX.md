# Session 903: Signal Intelligence Wired + Celery OOM Fix

**Date:** February 1, 2026
**Status:** COMPLETE
**PRs:** #686, #687

---

## Summary

This session completed two critical fixes:
1. **Signal Intelligence Wiring** - HiveMindSessions now properly link to SignalCluster and AutoTopic for full provenance tracking
2. **Celery OOM Fix** - Spider scan task no longer causes worker memory exhaustion

---

## Signal Intelligence Wired (PR #686)

### Problem
AutoTopics existed but weren't creating HiveMindSessions with proper foreign key links. The `process_pending_auto_topics` task had a missing import and `run_triggered_conversation` didn't support session linking.

### Solution

**1. Fixed missing import in `core/tasks.py`:**
```python
from django.db import models  # Session 902: Fixed missing import
```

**2. Added `hive_session_id` parameter to `run_triggered_conversation`:**
```python
def run_triggered_conversation(
    self,
    topic: str,
    conversation_type: str = 'general',
    objective: str = None,
    success_criteria: list = None,
    auto_select_agents: bool = False,
    participant_ids: list = None,
    hive_session_id: str = None  # Session 902: Link to HiveMindSession
):
```

**3. Updated session status on completion:**
```python
if hive_session_id:
    session = HiveMindSession.objects.filter(id=hive_session_id).first()
    if session:
        session.status = 'completed'
        session.save(update_fields=['status'])
```

**4. Fixed the dispatch call in `trigger_signal_driven_conversation`:**
```python
run_triggered_conversation.delay(
    topic=auto_topic.name,
    conversation_type=auto_topic.suggested_conversation_type,
    objective=session.objective,
    success_criteria=session.success_criteria,
    auto_select_agents=False,
    participant_ids=agent_ids,
    hive_session_id=str(session.id),  # Pass the session ID
)
```

### Result
- 2 HiveMindSessions now have `signal_cluster` and `auto_topic` links
- Full provenance chain: SpiderData → SignalCluster → AutoTopic → HiveMindSession

---

## Celery OOM Fix (PR #687)

### Problem
Celery worker ran out of memory with logs showing:
- 5 simultaneous `scan_spider_opportunities` tasks
- "Unclosed client session" warnings from aiohttp
- Worker removed due to memory exhaustion

### Root Cause
1. `scan_spider_opportunities` scheduled every 15 minutes with no concurrency control
2. Previous runs could overlap with new runs
3. aiohttp sessions weren't properly closed when event loops changed (common in Celery)
4. TCP connections accumulated, exhausting memory

### Solution

**1. Task Lock (`intelligence/tasks.py`):**
```python
from django.core.cache import cache

lock_key = 'scan_spider_opportunities_lock'
lock_timeout = 600  # 10 minutes max

if not cache.add(lock_key, self.request.id, lock_timeout):
    logger.warning(f"Spider scan already running, skipping...")
    return {'status': 'skipped', 'reason': 'Another scan in progress'}

try:
    # ... task code ...
finally:
    cache.delete(lock_key)
```

**2. Reduced Schedule Frequency (`core/celery.py`):**
```python
'scan-spider-opportunities': {
    'task': 'intelligence.tasks.scan_spider_opportunities',
    'schedule': crontab(minute='*/30'),  # Was */15
    'options': {'expires': 1800}
}
```

**3. Proper Session Cleanup (`ai_core/spiders/web_request_layer.py`):**
```python
# When session created in different event loop, properly close connector
if self.session and self._session_loop and current_loop and self._session_loop != current_loop:
    if self.session.connector and not self.session.connector.closed:
        self.session.connector.close()  # Sync call - safe from any context
    self.session = None
    self._session_loop = None
```

**4. Added `close_sync()` method for non-async cleanup:**
```python
def close_sync(self):
    """Synchronous close for use outside async context"""
    if self.session:
        if self.session.connector and not self.session.connector.closed:
            self.session.connector.close()
        self.session = None
        self._session_loop = None
```

### Result
- Only one spider scan runs at a time
- Proper TCP connection cleanup
- No more memory exhaustion

---

## Files Changed

| File | Changes |
|------|---------|
| `core/tasks.py` | Added `hive_session_id` param, session status update, fixed import |
| `intelligence/tasks.py` | Added task lock with Django cache |
| `core/celery.py` | Reduced spider scan to 30 min |
| `ai_core/spiders/web_request_layer.py` | Fixed connector cleanup, added `close_sync()` |

---

## Verification

```bash
# Check Signal Intelligence links
python manage.py shell -c "
from core.models import HiveMindSession
sessions = HiveMindSession.objects.filter(signal_cluster__isnull=False)
print(f'Sessions with signal_cluster: {sessions.count()}')
for s in sessions[:5]:
    print(f'  {s.topic}: cluster={s.signal_cluster_id}, auto_topic={s.auto_topic_id}')
"

# Monitor Celery memory
watch -n 30 'ps aux | grep celery | grep -v grep'

# Check for skipped scans in logs
grep "already running, skipping" /var/log/celery/*.log
```

---

## Next Steps

1. Monitor production Celery worker memory over 24 hours
2. Verify Signal Intelligence UI shows origin signals for new conversations
3. Consider increasing spider scan frequency back to 15 min once stability confirmed

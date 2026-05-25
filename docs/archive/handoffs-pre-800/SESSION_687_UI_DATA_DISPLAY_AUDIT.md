# Session 687: UI Data Display Audit - Human Interface Integration

**Date:** January 5, 2026
**Focus:** Ensure all backend data displays correctly on React frontend
**Status:** COMPLETE

---

## Problem Statement

The new React frontend (Session 686) was built with the Human Interface Layer, but:

1. **Dashboard Recent Activity** - Only showing WebSocket updates, not loading initial data from API
2. **Agent Count Mismatch** - UI showing 57 agents instead of 72 (database out of sync with code)
3. **Human Page Attention Stream** - Needed real data flow from system events
4. **No automated attention generation** - System events weren't creating attention items

---

## Solutions Implemented

### 1. Dashboard Recent Activity Fix

**File:** `frontend/src/pages/DashboardPage.tsx`

Added API fetch for initial activity data:

```typescript
import { activityApi } from '@/lib/api'

// Fetch initial recent activity
const { data: initialActivity } = useQuery({
  queryKey: ['recent-activity'],
  queryFn: () => activityApi.recent(20, 24),
})

// Initialize recentActivity with fetched data
useEffect(() => {
  if (initialActivity?.data?.activities) {
    const formatted = initialActivity.data.activities.map((a) => ({
      type: a.title || a.type,
      timestamp: a.timestamp,
      data: { subtitle: a.subtitle, icon: a.icon },
    }))
    setRecentActivity(formatted)
  }
}, [initialActivity])
```

**Result:** Dashboard now loads real activity on mount + receives WebSocket updates.

---

### 2. Agent Count Synchronization

**Problem:** Database had 57 agents, `AgentRouter.AGENT_MAP` had 72.

**Investigation:**
- 22 agents in code but missing from database
- 7 "orphaned" agents in database but not in code

**Fix Applied:**
```python
# Synced 22 missing agents to database
for agent_key in missing_agents:
    Agent.objects.create(
        name=agent_key,
        slug=agent_key.lower().replace('agent', '').replace('_', '-'),
        is_active=True
    )

# Deactivated 7 orphaned agents
Agent.objects.filter(name__in=orphaned_agents).update(is_active=False)
```

**Result:** 72 active agents in database matching code.

---

### 3. Human Attention Bridge Service (NEW)

**File:** `core/services/human_attention_bridge.py` (~439 lines)

Created integration layer connecting system events to Human Interface attention stream:

```python
class HumanAttentionBridge:
    """Bridge that creates attention items from system events."""

    def create_pilot_gate_attention(self, gate, user=None)
    def create_agent_execution_attention(self, execution, urgency='medium', user=None)
    def create_arbitrage_attention(self, opportunity: dict, user=None)
    def create_system_alert(self, alert_type, title, summary, urgency='medium', payload=None, user=None)
    def create_content_review_attention(self, content_type, title, summary, content_id, ...)
    def create_spider_alert(self, spider_name, alert_type, title, summary, ...)

# Singleton instance
attention_bridge = HumanAttentionBridge()
```

**Django Signals for Auto-Creation:**

```python
@receiver(post_save, sender='core.PilotReadinessGate')
def on_pilot_gate_change(sender, instance, created, **kwargs):
    """Auto-create attention when pilot gate status changes to pending_review."""
    if instance.status == 'pending_review':
        attention_bridge.create_pilot_gate_attention(instance)

@receiver(post_save, sender='core.AgentExecution')
def on_agent_execution_complete(sender, instance, created, **kwargs):
    """Auto-create attention for failed agent executions."""
    if not created and instance.status == 'failed':
        critical_agents = ['ThinkingAgent', 'ArbitrageDetector', ...]
        if agent_name in critical_agents:
            attention_bridge.create_agent_execution_attention(instance)
```

---

### 4. ArbitrageDetector Integration

**File:** `core/agents/markets/arbitrage_detector.py`

Added Human Interface integration for HOT/GOOD arbitrage opportunities:

```python
def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
    # ... existing logic ...

    # Session 687: Create Human Interface attention items for HOT arbs
    self._create_attention_items(arb_opps)

    return result

def _create_attention_items(self, arb_opps: List[Dict]) -> None:
    """Session 687: Create Human Interface attention items for actionable arbs."""
    from core.services.human_attention_bridge import attention_bridge

    for arb in arb_opps:
        if arb.get('rating') not in ['HOT', 'GOOD']:
            continue

        attention_bridge.create_arbitrage_attention(
            opportunity={
                'id': arb.get('id', ''),
                'title': arb.get('event', 'Arbitrage Opportunity'),
                'profit_pct': arb.get('profit_pct', 0),
                'markets': arb.get('markets', []),
                'expires_at': arb.get('expires_at'),
                'rating': arb.get('rating'),
                'details': arb,
            }
        )
```

---

### 5. Celery Task for Automated Attention Generation

**File:** `core/tasks.py`

Added new task that scans system state and creates attention items:

```python
@shared_task
def generate_human_attention_items():
    """Generate attention items from various system events.

    Scans:
    - Pilot gates pending review
    - Failed agent executions (last 24h)
    - System health alerts
    - Spider data requiring attention
    """
    # Returns: {'status': 'completed', 'items_created': total, 'breakdown': stats}
```

**File:** `core/celery.py`

Added Celery Beat schedule:

```python
# Session 687: Human Interface attention items from system events
'generate-human-attention-items': {
    'task': 'core.tasks.generate_human_attention_items',
    'schedule': crontab(minute='*/15'),  # Every 15 minutes
    'options': {
        'expires': 900,
    }
},
```

---

## Files Changed

| File | Change |
|------|--------|
| `frontend/src/pages/DashboardPage.tsx` | Added initial activity fetch, updated rendering |
| `frontend/src/pages/HumanPage.tsx` | Added debug logging and error handling |
| `core/services/human_attention_bridge.py` | **NEW** - 439 lines, integration bridge |
| `core/agents/markets/arbitrage_detector.py` | Added `_create_attention_items()` method |
| `core/tasks.py` | Added `generate_human_attention_items` task |
| `core/celery.py` | Added beat schedule (every 15 minutes) |

---

## Data Flow Architecture

```
System Events
    │
    ├── Pilot Gate Status Change ──────────┐
    ├── Agent Execution Failed ────────────┤
    ├── ArbitrageDetector HOT/GOOD Arbs ───┤
    ├── System Health Alerts ──────────────┤
    └── Spider Data Alerts ────────────────┘
                                           │
                                           ▼
                              HumanAttentionBridge
                                           │
                                           ▼
                              HumanInterfaceService
                                           │
                                           ▼
                              HumanAttentionItem (DB)
                                           │
                                           ▼
                              /api/human/attention/
                                           │
                                           ▼
                              React HumanPage.tsx
```

---

## Testing Verification

1. **Dashboard Recent Activity:** Shows real data from API on page load
2. **Agent Count:** 72 active agents displayed correctly
3. **Human Attention API:** Returns real items from database
   ```
   Human Attention API Response: {success: true, items: Array(10), count: 10}
   ```
4. **Celery Beat:** Task scheduled every 15 minutes

---

## Next Session Recommendations

1. **Test ArbitrageDetector** - Run arbitrage detection to verify attention items created
2. **Add more event sources** - Content generation, spider alerts, etc.
3. **Human Page UI polish** - Pending/Urgent counts, Avg Decision Time metrics
4. **Decision actions** - Implement approve/reject/dismiss on attention items

---

## Commands

```bash
# Restart Celery Beat to pick up new schedule
pkill -f 'celery.*beat' && .venv/bin/celery -A core beat --loglevel=info &

# Manually run attention generation
.venv/bin/python manage.py shell -c "
from core.tasks import generate_human_attention_items
result = generate_human_attention_items()
print(result)
"

# Check attention items for a user
.venv/bin/python manage.py shell -c "
from core.models_human_interface import HumanAttentionItem
print(f'Total items: {HumanAttentionItem.objects.count()}')
for item in HumanAttentionItem.objects.all()[:5]:
    print(f'  - {item.title} ({item.urgency})')
"
```

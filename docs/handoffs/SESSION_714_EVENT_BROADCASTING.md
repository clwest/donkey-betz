# Session 714: Event Broadcasting (Phase 3)

**Date:** January 7, 2026
**Focus:** Real-time event broadcasting across all pages via WebSocket
**Status:** Phase 3 MOSTLY COMPLETE (3 of 5 pages integrated)

---

## Summary

Implemented Phase 3 of the Unified Human System integration - Event Broadcasting. This enables real-time updates across pages without polling, using WebSocket channel groups to broadcast system events to all connected clients.

---

## New Files Created

| File | Lines | Purpose |
|------|-------|---------|
| `core/consumers/system_events_consumer.py` | ~260 | WebSocket consumer for system-wide event broadcasting |
| `core/consumers/__init__.py` | ~15 | Module exports for consumers package |
| `docs/handoffs/SESSION_714_EVENT_BROADCASTING.md` | ~200 | This handoff document |

---

## Files Modified

### Backend

| File | Changes |
|------|---------|
| `core/routing.py` | Added `ws/system-events/` WebSocket route |
| `core/tasks.py` | Added event emitters to `generate_agent_dreams`, `execute_single_artifact`, `run_hive_mind_session`, `_deploy_pilot_for_gate`, and pilot auto-completion tasks |

### Frontend

| File | Changes |
|------|---------|
| `frontend/src/hooks/useWebSocket.ts` | Added `useSystemEvents` hook, 10 event types, typed event interfaces |
| `frontend/src/pages/IntelligencePage.tsx` | Added `useSystemEvents` for pilot and execution events |
| `frontend/src/pages/AgentsPage.tsx` | Added `useSystemEvents` for dream, level_up, and execution events |
| `frontend/src/pages/WorkspacePage.tsx` | Added `useSystemEvents` for file modification events |
| `frontend/src/pages/DashboardPage.tsx` | Added `useSystemEvents` for execution, body status, and dream events |
| `frontend/src/pages/HumanPage.tsx` | Added `useSystemEvents` for gate critical, body status, and pilot events |

---

## System Events Implemented

| Event Type | Emitted When | Pages Listening |
|------------|--------------|-----------------|
| `agent_execution_complete` | Agent task completed | Intelligence, Agents, Dashboard |
| `agent_execution_failed` | Agent task failed | Intelligence, Agents, Dashboard |
| `pilot_started` | New pilot deployed | Intelligence, Human |
| `pilot_completed` | Pilot auto-completed | Intelligence, Human |
| `dream_generated` | Agent dream created | Agents, Dashboard |
| `level_up` | Agent leveled up | Agents |
| `hive_mind_started` | Hive mind session began | (ready for HiveMindPage) |
| `gate_became_critical` | Gate needs attention | Human |
| `body_status_changed` | Body health changed | Dashboard, Human |
| `file_modified` | Workspace file changed | Workspace |

---

## Architecture

### Backend Consumer

```python
class SystemEventsConsumer(AsyncWebsocketConsumer):
    GROUP_NAME = "system_events"

    async def connect(self):
        await self.channel_layer.group_add(GROUP_NAME, self.channel_name)
        await self.accept()

    # Event handlers for each event type
    async def dream_generated(self, event): ...
    async def pilot_started(self, event): ...
    # etc.
```

### Event Emission Utilities

```python
# Async version
from core.consumers.system_events_consumer import emit_system_event
await emit_system_event('dream_generated', {...})

# Sync version (for Celery tasks, views)
from core.consumers.system_events_consumer import emit_system_event_sync
emit_system_event_sync('dream_generated', {...})
```

### Frontend Hook

```typescript
import { useSystemEvents } from '@/hooks/useWebSocket'

useSystemEvents({
  onDreamGenerated: (event) => {
    queryClient.invalidateQueries({ queryKey: ['agent-dreams'] })
  },
  onPilotCompleted: (event) => {
    queryClient.invalidateQueries({ queryKey: ['pilots'] })
  },
  onAnyEvent: (event) => console.log('Event:', event),
})
```

---

## Event Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           CELERY TASK                                    │
│   (generate_agent_dreams, execute_single_artifact, etc.)                │
└──────────────────────────────┬──────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                     emit_system_event_sync()                             │
│   channels.layers.get_channel_layer().group_send('system_events', ...)  │
└──────────────────────────────┬──────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    SystemEventsConsumer                                  │
│   Receives message, calls appropriate handler (dream_generated, etc.)   │
│   Forwards to all connected WebSocket clients                           │
└──────────────────────────────┬──────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    Frontend WebSocket                                    │
│   useSystemEvents() receives event, routes to registered callbacks      │
└──────────────────────────────┬──────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    React Query Invalidation                              │
│   queryClient.invalidateQueries() triggers data refresh                 │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## What's Remaining for Phase 3

1. **Add event handlers to DashboardPage**
   - `body_status_changed` - refresh body vitals
   - `agent_execution_complete` - refresh activity stats

2. **Add event handlers to HumanPage**
   - `gate_became_critical` - show alert
   - `body_status_changed` - refresh body health

3. **Add body_status_changed emitter**
   - Emit when body system pulse checks detect changes
   - Location: `core/services/heart.py` or body system services

---

## Testing

### Test WebSocket Connection

```bash
# Connect to WebSocket (requires wscat)
wscat -c ws://localhost:8000/ws/system-events/

# Should receive:
# {"type":"connection_established","message":"Connected to system events stream",...}
```

### Trigger Events

```bash
# Force dream generation (will emit dream_generated events)
DJANGO_SETTINGS_MODULE=core.settings .venv/bin/python manage.py shell -c "
from core.tasks import generate_agent_dreams
generate_agent_dreams.delay()
"
```

---

## Phase 3 Progress

| Task | Status |
|------|--------|
| Create SystemEventsConsumer | COMPLETE |
| Update routing.py | COMPLETE |
| Add event emitters to tasks.py | COMPLETE |
| Create useSystemEvents hook | COMPLETE |
| Add handlers to IntelligencePage | COMPLETE |
| Add handlers to AgentsPage | COMPLETE |
| Add handlers to WorkspacePage | COMPLETE |
| Add handlers to DashboardPage | COMPLETE |
| Add handlers to HumanPage | COMPLETE |
| Add body_status_changed emitter | PENDING (can be added when body services emit events) |

---

## Next Steps (Phase 4)

Phase 4 focuses on Shared State Store Unification:
- Create `frontend/src/stores/unifiedStore.ts`
- Merge opportunity/pilot/gate state
- Implement optimistic updates
- Add global state indicators (badges, sidebar widgets)

---

*Session 714 - Building the real-time nervous system*

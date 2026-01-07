# Session 702: HEART Service UI Integration

**Date:** January 6, 2026
**Focus:** Connect HEART Service to React Frontend
**Status:** COMPLETE

---

## Overview

Integrated the HEART service (created in Session 701) with the React frontend, providing real-time system health monitoring on the Dashboard and detailed monitoring in the Admin page.

---

## Implementation Summary

### 1. API Layer (`frontend/src/lib/api.ts`)

Added `heartApi` with 5 endpoints:

```typescript
export const heartApi = {
  pulse: () => api.get('/heart/pulse/'),      // Run full health check
  status: () => api.get('/heart/status/'),    // Get cached vitals
  history: (hours, limit) => api.get('/heart/history/', { params: { hours, limit } }),
  component: (name) => api.get(`/heart/component/${name}/`),
  alive: () => api.get('/heart/alive/'),      // Quick alive check
}
```

### 2. HeartWidget Component (`frontend/src/components/HeartWidget.tsx`)

New reusable component (~280 lines) featuring:

- **Health Score Gauge** - Circular progress indicator (0-100%)
- **Body Part Indicators** - 6 status indicators with icons:
  - Brain (ThinkingAgent)
  - Nervous System (LLM Routers)
  - Organs (72 Agents)
  - Sensory (77 Spiders)
  - Skin (Workspace Manager)
  - Memory (Database & Redis)
- **Compact/Full Modes** - Adaptable display for different contexts
- **Auto-Refresh** - 30-second polling interval
- **WebSocket Ready** - Listens to dashboard WebSocket for heartbeat broadcasts

### 3. Dashboard Integration (`frontend/src/pages/DashboardPage.tsx`)

Replaced the static "System Status" section with the HeartWidget:

```tsx
{/* HEART Service - System Health (Session 702) */}
<HeartWidget />
```

### 4. Admin Page HEART Tab (`frontend/src/pages/AdminPage.tsx`)

Added comprehensive HEART tab (~230 lines) as the default tab:

- **Overall Health Stats** - Health score, status, component count, last check
- **Body Parts Grid** - Detailed status for each body part with:
  - Response times
  - Error messages
  - Component details
- **Heartbeat History** - 24-hour log of all heartbeats
- **Human Body Architecture Table** - Reference showing all body parts and their purposes

### 5. WebSocket Hook (`frontend/src/hooks/useWebSocket.ts`)

Added specialized hook and types:

```typescript
export function useHeartUpdates(onUpdate?: (data: HeartBeatUpdate) => void) {
  return useWebSocket('/heart', { onMessage: (data) => onUpdate?.(data) })
}

export interface HeartBeatUpdate {
  type: 'heartbeat' | 'component_status' | 'health_alert'
  health_score: number
  overall_status: 'healthy' | 'degraded' | 'critical'
  // ...
}
```

### 6. Auth Middleware Update (`core/auth_middleware.py`)

Added HEART endpoints to `PUBLIC_PATHS` for unauthenticated access:

```python
# Session 702: HEART Service APIs (read-only health monitoring for React frontend)
'/api/heart/pulse/',
'/api/heart/status/',
'/api/heart/history/',
'/api/heart/component/',
'/api/heart/alive/',
```

---

## Files Changed

### Created (1)
| File | Lines | Purpose |
|------|-------|---------|
| `frontend/src/components/HeartWidget.tsx` | ~280 | Reusable health widget |

### Modified (5)
| File | Changes |
|------|---------|
| `frontend/src/lib/api.ts` | +18 lines - heartApi |
| `frontend/src/pages/DashboardPage.tsx` | Replaced System Status with HeartWidget |
| `frontend/src/pages/AdminPage.tsx` | +230 lines - HEART tab |
| `frontend/src/hooks/useWebSocket.ts` | +25 lines - useHeartUpdates hook |
| `core/auth_middleware.py` | +7 lines - HEART public paths |

---

## UI Screenshots (Conceptual)

### Dashboard - HeartWidget
```
┌─────────────────────────────────────────────────────┐
│  System Health (HEART)              100% Healthy    │
│                                                     │
│  ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐  │
│  │ 🧠  │ │ ⚡  │ │ 👥  │ │ 👁️  │ │ ✋  │ │ 💾  │  │
│  │Brain│ │Nerv.│ │Organs│ │Sens.│ │Skin │ │Memory│  │
│  │  ✓  │ │  ✓  │ │  ✓  │ │  ✓  │ │  ✓  │ │  ✓  │  │
│  └─────┘ └─────┘ └─────┘ └─────┘ └─────┘ └─────┘  │
│                                                     │
│  Last heartbeat: 15 seconds ago                     │
└─────────────────────────────────────────────────────┘
```

### Admin Page - HEART Tab
```
┌─────────────────────────────────────────────────────┐
│  [HEART] [Services] [Celery] [Spiders] [Agents]     │
├─────────────────────────────────────────────────────┤
│  Health Score    Status      Components    Last     │
│  ┌──────────┐   ┌────────┐   ┌────────┐   ┌──────┐ │
│  │   100%   │   │ Healthy│   │  6/6   │   │14:32 │ │
│  │    ❤️    │   │   ✓    │   │healthy │   │      │ │
│  └──────────┘   └────────┘   └────────┘   └──────┘ │
│                                                     │
│  Body Part Status                       [Refresh]   │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐│
│  │🧠 Brain      │ │⚡ Nervous    │ │👥 Organs     ││
│  │ThinkingAgent │ │LLM Routers   │ │72 Agents     ││
│  │✓ healthy 0ms│ │✓ healthy 315ms│ │✓ healthy 0ms││
│  └──────────────┘ └──────────────┘ └──────────────┘│
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐│
│  │👁️ Sensory    │ │✋ Skin       │ │💾 Memory     ││
│  │77 Spiders    │ │Workspace     │ │DB + Redis    ││
│  │✓ healthy 0ms│ │✓ healthy 1ms │ │✓ healthy 1ms ││
│  └──────────────┘ └──────────────┘ └──────────────┘│
│                                                     │
│  Heartbeat History (24h)                            │
│  ├─ 100% - 6/6 healthy - 2:48:27 PM - healthy      │
│  ├─ 100% - 6/6 healthy - 2:47:27 PM - healthy      │
│  └─ ...                                             │
└─────────────────────────────────────────────────────┘
```

---

## Status Color Mapping

| Status | Color | Health Score |
|--------|-------|--------------|
| Healthy | Green | 80-100% |
| Degraded | Amber | 50-79% |
| Critical | Red | 0-49% |

---

## API Response Structure

```json
{
  "success": true,
  "health_score": 100.0,
  "overall_status": "healthy",
  "is_alive": true,
  "last_check": "2026-01-07T02:24:04.465340+00:00",
  "components": {
    "brain": {
      "name": "Brain (ThinkingAgent)",
      "status": "healthy",
      "is_healthy": true,
      "response_time_ms": 0,
      "uptime_percent_24h": 100.0,
      "details": { "model": "claude-opus-4", "agent_class": "ThinkingAgent" }
    },
    "nervous_system": { ... },
    "organs": { ... },
    "sensory": { ... },
    "skin": { ... },
    "memory": { ... }
  }
}
```

---

## Testing

```bash
# API test
curl http://localhost:8000/api/heart/status/
# Returns: {"success":true,"health_score":100.0,...}

# Frontend build
cd frontend && npm run build
# ✓ built in 1.50s
```

---

## Next Steps

1. **LUNGS UI Integration** - Connect the new LUNGS service (budget/resource monitoring) to the frontend
2. **WebSocket Consumer** - Create `/ws/heart/` consumer for real-time updates (optional)
3. **Historical Charts** - Add health score trend chart to Admin HEART tab

---

**Session 702 Frontend Complete** - HEART Service fully integrated with React UI

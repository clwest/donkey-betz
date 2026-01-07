# Session 715: Unified State Store (Phase 4)

**Date:** January 7, 2026
**Focus:** Shared state store unification across all pages
**Status:** Phase 4 COMPLETE

---

## Summary

Implemented Phase 4 of the Unified Human System integration - Shared State Store Unification. This provides a central Zustand store that tracks pending decisions, opportunities, pilots, and gates, with automatic real-time updates via system events.

---

## New Files Created

| File | Lines | Purpose |
|------|-------|---------|
| `frontend/src/stores/unifiedStore.ts` | ~370 | Unified state for decisions, opportunities, pilots, gates |
| `docs/handoffs/SESSION_715_UNIFIED_STATE_STORE.md` | ~200 | This handoff document |

---

## Files Modified

| File | Changes |
|------|---------|
| `frontend/src/components/layout/Sidebar.tsx` | Added badge counts for Human and Intelligence pages |
| `frontend/src/components/layout/Layout.tsx` | Wired system events to unified store updates |

---

## Unified Store Architecture

### State Shape

```typescript
interface UnifiedState {
  // Attention/Decisions
  attentionStats: AttentionStats | null
  pendingDecisionsCount: number

  // Opportunities
  topOpportunities: Opportunity[]
  activeOpportunity: Opportunity | null

  // Pilots
  runningPilots: RunningPilot[]
  runningPilotsCount: number

  // Gates
  criticalGates: CriticalGate[]
  criticalGatesCount: number

  // Loading states
  isLoadingAttention: boolean
  isLoadingOpportunities: boolean
  isLoadingPilots: boolean
  isLoadingGates: boolean

  // Error states
  error: string | null

  // Cache timestamps
  lastFetch: {
    attention: Date | null
    opportunities: Date | null
    pilots: Date | null
    gates: Date | null
  }
}
```

### Fetch Methods

```typescript
fetchAttentionStats()   // GET /api/human/attention-stats/
fetchTopOpportunities() // GET /api/opportunities/top/
fetchRunningPilots()    // GET /api/pilots/dashboard/
fetchCriticalGates()    // GET /api/pilots/gates/
fetchAll()              // Parallel fetch of all data
```

### Optimistic Update Methods

```typescript
setActiveOpportunity(opp: Opportunity | null)
decrementPendingDecisions()  // Use after marking decision as handled
incrementPendingDecisions()  // Use when new decision arrives
```

### Selector Hooks

```typescript
// Counts for badges
usePendingDecisionsCount()  // Pending human decisions
useRunningPilotsCount()     // Currently running pilots
useCriticalGatesCount()     // Gates needing attention
useTotalBadgeCount()        // Combined pending + critical

// Data slices
useTopOpportunities()       // Top 5 opportunities
useRunningPilots()          // Running pilot details
useActiveOpportunity()      // Currently selected opportunity

// Computed values
useHasCriticalItems()       // Boolean: any critical items?
useIsLoading()              // Boolean: any data loading?
```

---

## Sidebar Badge Integration

### Badge Mapping

| Page | Badge Shows |
|------|-------------|
| `/human` | Pending decisions count |
| `/intelligence` | Running pilots + Critical gates |

### Implementation

```typescript
const getBadgeCount = (path: string): number | null => {
  switch (path) {
    case '/human':
      return pendingDecisions > 0 ? pendingDecisions : null
    case '/intelligence':
      return runningPilots > 0 || criticalGates > 0
        ? runningPilots + criticalGates
        : null
    default:
      return null
  }
}
```

### Badge Styling

```jsx
<span className="ml-auto flex h-5 min-w-5 items-center justify-center rounded-full bg-primary-600 px-1.5 text-xs font-medium text-white">
  {badge > 99 ? '99+' : badge}
</span>
```

---

## System Events Integration

### Layout Component Event Handling

```typescript
// Subscribe to system events for real-time store updates
useSystemEvents({
  onPilotStarted: handlePilotEvent,    // Refresh pilots + gates
  onPilotCompleted: handlePilotEvent,  // Refresh pilots + gates
  onGateBecameCritical: handleGateEvent, // Refresh gates + attention
  onAgentExecutionComplete: handleAgentExecution, // Refresh opportunities
})
```

### Event Flow

```
System Event Emitted (backend)
         │
         ▼
SystemEventsConsumer broadcasts
         │
         ▼
Layout.tsx useSystemEvents receives
         │
         ▼
Handler calls unified store fetch
         │
         ▼
Store updates state
         │
         ▼
Sidebar badges re-render
```

---

## Data Refresh Strategy

1. **Initial Load**: Sidebar `useEffect` calls `fetchAll()` on mount
2. **Polling**: Sidebar refreshes every 60 seconds via `setInterval`
3. **Real-time**: Layout receives system events and triggers specific fetches
4. **Optimistic**: Components can call optimistic update methods for instant UI feedback

---

## API Endpoints Used

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/human/attention-stats/` | GET | Pending decisions count |
| `/api/opportunities/top/` | GET | Top opportunities list |
| `/api/pilots/dashboard/` | GET | Running pilots data |
| `/api/pilots/gates/` | GET | All gates (filtered for critical) |

---

## Testing

### Verify Store Data

```bash
# Check APIs return data
curl http://localhost:8000/api/human/attention-stats/
curl http://localhost:8000/api/opportunities/top/
curl http://localhost:8000/api/pilots/dashboard/
curl http://localhost:8000/api/pilots/gates/
```

### Verify Badges

1. Open http://localhost:8080/dashboard
2. Check sidebar for badge counts on Human and Intelligence pages
3. Navigate to verify counts match page data

### Verify Real-time Updates

1. Open browser console to see WebSocket events
2. Trigger a pilot start from backend
3. Watch sidebar badge update without refresh

---

## Phase 4 Progress

| Task | Status |
|------|--------|
| Create unifiedStore.ts | COMPLETE |
| Add selector hooks | COMPLETE |
| Add optimistic update methods | COMPLETE |
| Integrate badges into Sidebar | COMPLETE |
| Wire system events in Layout | COMPLETE |
| Update documentation | COMPLETE |

---

## Next Steps (Phase 5)

Phase 5 focuses on Sci-Fi Features UI - building frontend pages for the 13 features that have complete backends but no UI:

1. Hive Mind Page
2. Memory Palace Page
3. Evolution Dashboard
4. Mood & Personality Page
5. Rivalries & Alliances
6. Time Travel Page
7. Time Capsules Page
8-13. Additional features

---

*Session 715 - Unifying state across the entire application*

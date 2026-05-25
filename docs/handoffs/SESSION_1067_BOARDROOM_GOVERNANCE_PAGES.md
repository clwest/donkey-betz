---
originating_session: 1067
provenance_confidence: HIGH
provenance_note: auto-added by backfill_doc_provenance
---

# Session 1067: Full-Page Boardroom & Governance Routes

**Date:** 2026-02-23
**PRs:** #1426, #1427, #1428, #1429

## What Was Done

### 1. Full-Page Boardroom (`/boardroom`) — PR #1426
Created `frontend/src/pages/BoardroomPage.tsx` — a dedicated full-page operator inbox elevated from the workspace `BoardroomTab`:
- **Summary cards row**: Pending count, Decided today, ML accuracy, Avg response time (from `humanApi.attentionStats()`)
- **Filter bar**: Urgency chips (all/critical/high/medium/low), type dropdown (review/insight/alert/opportunity), search input, sort dropdown (newest/oldest/urgency)
- **Two tabs**: Inbox (pending attention items) and Draft Decisions (from `decisionsApi.list()`)
- **Slide-over drawer**: Clicking an item opens a right-side panel with full details — summary, ML prediction panel (confidence bar, approval probability gauge, reasoning signals, similar past decisions), agent output, raw data toggle, and Approve/Ignore/Defer action buttons
- **Bulk actions toolbar**: Select multiple items, bulk approve/ignore with progress feedback
- **Auto-refresh**: 30s polling via React Query `refetchInterval`
- **NEW badges**: Items created since last visit highlighted

### 2. Full-Page Governance (`/governance`) — PR #1426
Created `frontend/src/pages/GovernancePage.tsx` — a dedicated full-page system control panel elevated from the workspace `GovernanceTab`:
- **Health banner**: Green/red status bar based on emergency controls state, live polling indicator
- **KPI cards row**: Active agents, System health %, Open gates, Pending remediations
- **Four tabs**: Alerts, Gates, Decisions (self-healing), Activity
- **Emergency controls**: Prominent placement with halt/skin-lock actions
- **Self-healing progress**: Progress bar, 4-stat grid, agent progress table, batch remediation controls
- **Live polling toggle**: 12s interval when enabled

### 3. Routes & Navigation — PR #1426
- Added `/boardroom` and `/governance` routes to `App.tsx`
- Added sidebar nav items: Boardroom (Gavel icon) and Governance (ShieldCheck icon)
- Badge counts: Boardroom shows `pendingDecisionsCount`, Governance shows `criticalGatesCount`
- Added `governanceStats` endpoint to `decisionsApi` in `api.ts`

### 4. Fix: ml_prediction Object Rendering — PR #1427
`DecisionDetailModal` typed `ml_prediction` as `string` but the API returns an object `{reasoning, prediction, predicted_at, similar_items, approval_probability}`. Rendering the object directly caused React error #31. Fixed by checking `typeof` and extracting `.prediction` or `.reasoning` before rendering. Same treatment for `ml_recommendation`.

### 5. Fix: Spider Raw Dict Summaries — PR #1428
**Backend** (`core/tasks.py`): `monitor_and_process_opportunities` was using `str(data.raw_data)[:300]` as the summary for spider attention items, producing raw Python dict repr like `{'items': [{'link': ...`. Now extracts human-readable titles from nested `items`/`results`/`articles` lists, or falls back to top-level text fields (`summary`/`description`/`content`).

**Frontend** (`BoardroomPage.tsx`, `BoardroomTab.tsx`): Added `cleanRawSummary()` safety net that detects raw dict/JSON strings already in the DB and parses out readable content via JSON parse or regex fallback.

### 6. Governance Critical Decisions Section — PR #1429
PA identified that Governance page counted pending decisions in the KPI card but never listed them. Added:
- **"Critical Decisions" section** — always visible above tabs, fetches draft decisions from `decisionsApi.list()`. Shows topic, decision type + impact area badges, recommended stance preview, and Promote/Reject buttons
- **Slide-over drawer** — clicking a decision opens full details: topic, recommended stance (highlighted card), numbered key insights, suggested feature, participants, decision ID
- **"Open Boardroom" link** for navigating to full inbox
- 30s auto-refresh

## Files Changed

| File | Change |
|------|--------|
| `frontend/src/pages/BoardroomPage.tsx` | **NEW** — Full-page boardroom inbox |
| `frontend/src/pages/GovernancePage.tsx` | **NEW** then enhanced — Full-page governance + critical decisions section + drawer |
| `frontend/src/App.tsx` | Added 2 routes |
| `frontend/src/components/layout/Sidebar.tsx` | Added 2 nav items (Gavel, ShieldCheck) + badge counts |
| `frontend/src/lib/api.ts` | Added `governanceStats` endpoint |
| `frontend/src/components/platform/DecisionDetailModal.tsx` | Fixed ml_prediction/ml_recommendation object rendering |
| `frontend/src/pages/workspace/tabs/BoardroomTab.tsx` | Added `cleanRawSummary()` for spider data |
| `core/tasks.py` | Fixed spider summary extraction in `monitor_and_process_opportunities` |

## Known Issues / Follow-ups
- Existing spider attention items with raw dict summaries will be cleaned on the frontend via `cleanRawSummary()` — new items will have proper summaries from the backend fix
- The workspace BoardroomTab and GovernanceTab still exist — they're not redundant (workspace is project-specific, full pages are system-wide) but could share more code via extraction
- `humanApi.attentionStats()` endpoint may return limited data — summary cards show `--` for missing fields gracefully

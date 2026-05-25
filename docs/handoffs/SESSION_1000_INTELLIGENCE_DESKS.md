---
originating_session: 1000
provenance_confidence: HIGH
provenance_note: auto-added by backfill_doc_provenance
---

# Session 1000: Activate All Intelligence Desks

**Date:** February 12, 2026
**Status:** Complete
**Milestone:** Session 1000 - 23 agents activated from idle to daily production

## Summary

Added a unified intelligence desk system that runs all 4 desk coordinators (Stocks, Sports, Blockchain, Narrative) on a daily Celery schedule. Each desk orchestrates 3-9 sub-agents, producing cached intelligence briefs served via API and displayed in a new Command Center panel. Also wired 2 missing agents (BookmakerAgent, DecisionEnforcerAgent) to the router, bringing total routable agents to 82.

## Changes

### Phase 1: Router Additions (core/agent_router.py)

Added 2 agents to imports and `AGENT_MAP`:
- `BookmakerAgent` (from `core.agents.bookmaker_agent`)
- `DecisionEnforcerAgent` (from `core.agents.decision_enforcer_agent`)

**Result:** 82 routable agents (up from 80).

### Phase 2: Celery Task (core/tasks.py)

New `run_all_desks_intelligence()` shared task that runs 4 desks sequentially:

| Desk | Coordinator | Agents Activated |
|------|------------|-----------------|
| Stocks | `MarketIntelligenceCoordinator.execute()` | BullCaseAgent, BearCaseAgent, StockAuditCoordinator, StockAnalystAgent, MarketMovementMonitorAgent, InstitutionalWatcherAgent, MarketAnomalyDetectorAgent, SignalScannerAgent |
| Sports | `SportsBettingCoordinator.generate_brief()` | GamePredictor, SportsOddsAnalyst, ArbitrageDetector, LineMovementAnalyzer, SharpActionDetector |
| Blockchain | `BlockchainAuditCoordinator.execute()` | SmartContractAuditorAgent, TransactionMonitorAgent, WhaleWatcherAgent, ExploitDetectorAgent |
| Narrative | `NarrativeDriftCoordinator.execute()` | NarrativeHistorianAgent, TrendBreakDetectorAgent, CulturalImpactAgent |

Each desk:
- Wrapped in try/except (one desk failing doesn't block others)
- Results cached at `desk:{name}:latest` with 6-hour TTL
- Timing logged per desk
- Returns `{desks_completed, desks_failed, timing}`

### Phase 3: Beat Schedule (core/celery.py)

Added `run-all-desks-intelligence` entry:
- Schedule: `crontab(minute=0, hour=6)` (daily 6 AM)
- Queue: `long_running`
- Expires: 3600s

### Phase 4: API Endpoints (core/views_home.py, core/urls.py)

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/home/intelligence-desks/` | GET | Returns cached desk briefs with status, summary, agents, timestamp |
| `/api/home/trigger-desks/` | POST | On-demand trigger via Celery `.delay()` |

Also enriched `boot()` response with `intelligence_desks_ready` count in `while_away` dict.

### Phase 5: Frontend (CommandCenterPage.tsx, api.ts)

- Added `homeApi.intelligenceDesks()` and `homeApi.triggerDesks()` to API client
- Added `useQuery` for intelligence desks (5-min refetch interval)
- Added `useMutation` for trigger button
- Added "intel desks ready" pill in While Away section (purple, Brain icon)
- New `IntelligenceDesksPanel` component:
  - 4-card grid (Stocks=green, Sports=amber, Blockchain=cyan, Narrative=purple)
  - Each card: icon, name, status badge (Ready/No Data), summary text, agent count, timestamp
  - "Run All Desks" button triggers on-demand execution
  - Collapsible, auto-expands when desks have data
- Updated `BootData` TypeScript interface with `intelligence_desks_ready`

## Files Modified (7)

| File | Lines Changed |
|------|--------------|
| `core/agent_router.py` | +8 (2 imports, 2 AGENT_MAP entries) |
| `core/tasks.py` | +130 (run_all_desks_intelligence task) |
| `core/celery.py` | +8 (beat schedule entry) |
| `core/views_home.py` | +65 (2 endpoints + boot enrichment) |
| `core/urls.py` | +3 (import update + 2 URL routes) |
| `frontend/src/lib/api.ts` | +2 (homeApi methods) |
| `frontend/src/pages/CommandCenterPage.tsx` | +140 (types, panel component, query, mutation, pills) |

## Agents Activated (23 total)

| Category | Agents |
|----------|--------|
| Now routable (2) | BookmakerAgent, DecisionEnforcerAgent |
| Stocks desk (9) | MarketIntelligenceCoordinator, BullCaseAgent, BearCaseAgent, StockAuditCoordinator, StockAnalystAgent, MarketMovementMonitorAgent, InstitutionalWatcherAgent, MarketAnomalyDetectorAgent, SignalScannerAgent |
| Sports desk (5) | GamePredictor, SportsOddsAnalyst, ArbitrageDetector, LineMovementAnalyzer, SharpActionDetector |
| Blockchain desk (5) | BlockchainAuditCoordinator, SmartContractAuditorAgent, TransactionMonitorAgent, WhaleWatcherAgent, ExploitDetectorAgent |
| Narrative desk (4) | NarrativeDriftCoordinator, NarrativeHistorianAgent, TrendBreakDetectorAgent, CulturalImpactAgent |

## No New Models, No Migrations

Desk briefs stored in Django cache (6-hour TTL, regenerated daily). Stock desk also persists to existing `MarketIntelligenceBrief` model.

## Verification

- All Python files compile (`py_compile`)
- Frontend builds successfully (2,376 KB)
- 82 routable agents confirmed via Django shell
- BookmakerAgent and DecisionEnforcerAgent present in AGENT_MAP

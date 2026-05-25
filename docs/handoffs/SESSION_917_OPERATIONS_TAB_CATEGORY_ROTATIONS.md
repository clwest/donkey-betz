---
originating_session: 917
provenance_confidence: HIGH
provenance_note: auto-added by backfill_doc_provenance
---

# Session 917: Operations Tab Category Rotations

**Date:** February 2, 2026
**Status:** Complete

---

## Problem Statement

The Operations Tab was only showing Research, Reports, Content, and Summaries. Market reports from financial agents had stopped appearing a few days prior, and many other agent categories weren't creating workspace operations at all.

---

## Root Cause Analysis

### Two Separate Task Systems

The system had two types of scheduled agent tasks:

1. **`agent_category_rotation(category)`** - Uses `universal_agent_workspace_output()` which **DOES write to WorkspaceOperation** table
2. **`run_*_agents()` tasks** (e.g., `run_stock_financial_agents`) - Uses `router.route()` which **DOES NOT write to WorkspaceOperation**

Only the `financial-agent-category-rotation` was configured to use the workspace-writing approach. Other categories used the non-writing approach.

### Categories Missing Workspace Writes

| Category | Agents | Prior Task | Issue |
|----------|--------|------------|-------|
| financial | 10 | `financial-agent-category-rotation` | Was configured but timing collision |
| sports | 2 | `run_prediction_market_agents` | Used `router.route()` - no workspace writes |
| blockchain | 5 | None scheduled | Never configured |
| narrative | 4 | `run-narrative-culture-agents` | Used `router.route()` - no workspace writes |
| strategy | 6 | `run-strategy-marketing-agents` | Used `router.route()` - no workspace writes |

---

## Solution Implemented

### 1. Added Category Rotation Schedules

Added new scheduled tasks in `CELERY_BEAT_SCHEDULE` that use `agent_category_rotation()`:

| Task | Category | Schedule | Agents |
|------|----------|----------|--------|
| `financial-agent-category-rotation` | financial | Every 4h at :05 | 10 |
| `sports-agent-category-rotation` | sports | Every 2h at :45 | 2 |
| `blockchain-agent-category-rotation` | blockchain | Every 4h at :15 | 5 |
| `narrative-agent-category-rotation` | narrative | Every 6h at :25 | 4 |
| `strategy-agent-category-rotation` | strategy | Every 5h at :35 | 6 |

### 2. Added Manual Trigger Endpoint

New endpoint for testing and on-demand generation:

```
POST /api/workspace-triggers/trigger-category/

Body:
  category: 'financial' | 'sports' | 'blockchain' | 'narrative' |
            'strategy' | 'research' | 'content' | ... | 'all'

Response:
  {
    "success": true,
    "message": "Category rotation triggered for: financial",
    "task_id": "abc123...",
    "category": "financial"
  }
```

**Triggering 'all' will run:** financial, sports, blockchain, strategy, narrative

---

## Agents by Category (Full List)

### Financial (10 agents)
- StockAuditCoordinator → `financial/stocks`
- StockAnalystAgent → `financial/analysis`
- MarketMovementMonitorAgent → `financial/movements`
- InstitutionalWatcherAgent → `financial/institutional`
- MarketAnomalyDetectorAgent → `financial/anomalies`
- BullCaseAgent → `financial/bull-cases`
- BearCaseAgent → `financial/bear-cases`
- SignalScannerAgent → `financial/signals`
- MarketIntelligenceCoordinator → `financial/intelligence`
- PredictionMarketAnalyst → `financial/predictions`

### Sports (2 agents)
- SportsOddsAnalyst → `sports/odds`
- ArbitrageDetector → `sports/arbitrage`

### Blockchain (5 agents)
- BlockchainAuditCoordinator → `blockchain/audits`
- SmartContractAuditorAgent → `blockchain/contracts`
- TransactionMonitorAgent → `blockchain/transactions`
- WhaleWatcherAgent → `blockchain/whales`
- ExploitDetectorAgent → `blockchain/exploits`

### Narrative (4 agents)
- NarrativeDriftCoordinator → `narrative/drift`
- NarrativeHistorianAgent → `narrative/history`
- TrendBreakDetectorAgent → `narrative/trends`
- CulturalImpactAgent → `narrative/culture`

### Strategy (6 agents)
- BrandStrategyAgent → `strategy/brand`
- ContentStrategyAgent → `strategy/content`
- MarketingStrategyAgent → `strategy/marketing`
- SEOOptimizerAgent → `strategy/seo`
- SocialMediaAgent → `strategy/social`
- GrowthHackerAgent → `strategy/growth`

---

## Files Changed

| File | Changes |
|------|---------|
| `core/settings.py` | Added 4 new category rotation schedules, fixed financial timing |
| `core/views_workspace_triggers.py` | Added `trigger_category_rotation()` endpoint |
| `core/urls.py` | Added URL route for trigger-category endpoint |

---

## Testing

### Manual Trigger (Production)

```bash
# Trigger financial agents
curl -X POST -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"category": "financial"}' \
  "https://donkey-betz-platform-production.up.railway.app/api/workspace-triggers/trigger-category/"

# Trigger all priority categories
curl -X POST -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"category": "all"}' \
  "https://donkey-betz-platform-production.up.railway.app/api/workspace-triggers/trigger-category/"
```

### Check Results

```bash
# Check workspace operations for financial category
curl -H "Authorization: Token $TOKEN" \
  "https://donkey-betz-platform-production.up.railway.app/api/workspace-operations/?limit=20"
```

---

## Deployment Notes

After deploying:
1. Sync Celery Beat schedules: `python manage.py sync_celery_beat --apply`
2. Trigger category rotations manually to verify: `/api/workspace-triggers/trigger-category/`
3. Check Operations Tab in UI for new entries

---

## Expected Operations Tab Content After Fix

The Operations Tab should now show entries from:

| Category | Directory | Update Frequency |
|----------|-----------|------------------|
| Research | `research/` | Every 4h |
| Content | `content/` | Every 6h |
| Financial | `financial/` | Every 4h |
| Sports | `sports/` | Every 2h |
| Blockchain | `blockchain/` | Every 4h |
| Narrative | `narrative/` | Every 6h |
| Strategy | `strategy/` | Every 5h |
| Summaries | `summaries/` | Daily |
| Reports | `reports/` | Every 8h |

---

**Operations Tab now tracks 27+ agents across 5 key categories with workspace writes.**

---
originating_session: 975
provenance_confidence: HIGH
provenance_note: auto-added by backfill_doc_provenance
---

# Session 975 — Stock Intelligence Dashboard

**Date:** February 9, 2026
**Previous Session:** 974b (PA Async Celery)
**Branch:** `feature/stock-intelligence-dashboard`

---

## Problem

The system has rich stock market data flowing through SEC spiders, market intelligence briefs, stock alerts, and prediction outcomes — but none of it surfaces in the web UI. Data only goes to Discord. Users have no way to review briefs, filter alerts, track prediction accuracy, or browse SEC filings from the browser.

## Solution

Created a dedicated **Stock Intelligence** page (`/stocks`) as a standalone sidebar entry with 5 sub-tabs, backed by 6 read-only API endpoints. Zero migrations — all 4 models already exist.

---

## Changes

### Files Created (2)

| File | Purpose |
|------|---------|
| `core/views_stock_intelligence.py` | 6 API endpoints for stock data |
| `frontend/src/pages/StockIntelligencePage.tsx` | Tabbed dashboard with 5 sub-tabs |

### Files Modified (4)

| File | Changes |
|------|---------|
| `core/urls.py` | Added 6 URL patterns under `api/stocks/` |
| `frontend/src/lib/api.ts` | Added `StockDashboard`, `MarketBrief`, `MarketBriefDetail`, `StockAlert`, `PredictionOutcome` interfaces + `stockApi` object |
| `frontend/src/App.tsx` | Added `StockIntelligencePage` import + `/stocks` route |
| `frontend/src/components/layout/Sidebar.tsx` | Added "Stock Intelligence" entry with `TrendingUp` icon |

No migrations needed.

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/stocks/dashboard/` | GET | Overview: latest brief, alert counts by type, prediction accuracy, SEC count |
| `/api/stocks/briefs/` | GET | Paginated `MarketIntelligenceBrief` list (`?limit=&offset=`) |
| `/api/stocks/briefs/<uuid>/` | GET | Full brief detail with JSON fields (opportunities, debate zone, risks) |
| `/api/stocks/alerts/` | GET | Filterable alerts (`?type=&symbol=&action=&bookmarked=true`) |
| `/api/stocks/predictions/` | GET | Predictions with accuracy stats (`?ticker=`) |
| `/api/stocks/sec-filings/` | GET | SEC Edgar `SpiderData` entries (`?limit=&offset=`) |

All endpoints: `@api_view(['GET'])`, `@permission_classes([IsAuthenticated])`.

## Frontend Sub-tabs

| Tab | Content |
|-----|---------|
| **Overview** | Stats cards (briefs, alerts, accuracy, SEC), latest brief summary, alert type breakdown, prediction performance |
| **Market Briefs** | Paginated list, click-to-expand with high conviction opportunities, debate zone, bullish/bearish, risk alerts, confidence distribution |
| **Alerts** | Filter by type/symbol/bookmarked, color-coded type badges, bull/bear score bars, recommended action labels |
| **SEC Filings** | Spider data from `sec_edgar`, raw items displayed, relevance scores |
| **Predictions** | Table with ticker, type, conviction, predicted vs actual moves, 7D/30D correctness, aggregate stats bar |

## Models Used (Zero Migrations)

- `MarketIntelligenceBrief` — `core.models_unified_system` (daily briefs with executive_summary, JSON opportunity/risk fields)
- `StockMarketAlert` — `core.models_autonomous_alerts` (8 alert types, bull/bear scores, recommended actions)
- `PredictionOutcome` — `core.models_unified_system` (prediction tracking with 7D/30D accuracy)
- `SpiderData` — `core.models_unified_system` (filtered by `spider_name='sec_edgar'`)

## Design Decisions

1. **Standalone page, not a workspace tab** — Stock Intelligence is a distinct vertical that deserves its own sidebar entry
2. **Read-only endpoints** — All GET, no mutations for v1
3. **Sub-tabs inline** — Matches ContentStudioTab pattern (horizontal pill buttons)
4. **Pagination** — All list endpoints paginated (briefs accumulate daily, alerts can be numerous)

## Verification

- `python -c "import py_compile; py_compile.compile('core/views_stock_intelligence.py')"` — clean
- `npx tsc --noEmit` — zero new errors
- Navigate to `/stocks` — all 5 sub-tabs render

---
originating_session: 999
provenance_confidence: HIGH
provenance_note: auto-added by backfill_doc_provenance
---

# Session 999: Stock Intelligence Hub

**Date:** February 12, 2026
**Focus:** Add a consolidated "Hub" tab as the default landing view on the Stock Intelligence page.

## What Was Done

### New Backend Endpoint: `/api/stocks/hub/`

**File:** `core/views_stock_intelligence.py`

New `stock_hub()` view consolidates data from existing models into a single response:
- `stats`: total_briefs, total_alerts, total_predictions, accuracy_7d, accuracy_30d, sec_filings_count
- `latest_brief`: Most recent MarketIntelligenceBrief (same shape as dashboard)
- `top_alerts`: 6 most recent StockMarketAlert entries (compact)
- `top_predictions`: 8 most recent PredictionOutcome with actual results and W/L
- `market_news`: 10 expanded items from financial spiders (yahoo_finance, polygon, coingecko, finnhub, financial) using raw_data.items[] expansion pattern from sports hub
- `sec_recent`: 5 expanded items from sec_edgar spider

### URL Wiring

**File:** `core/urls.py`

Added `stock_hub` import and `path('api/stocks/hub/', stock_hub, name='stock-hub')` before the existing stock dashboard route.

### Frontend API Binding

**File:** `frontend/src/lib/api.ts`

Added `hub: () => api.get('/stocks/hub/')` to `stockApi` object.

### Frontend Hub Tab Component

**File:** `frontend/src/pages/StockIntelligencePage.tsx`

- New `HubTab` component — Bloomberg-terminal-inspired dark theme layout
- Hub is now the **default landing tab** (changed from Ticker Lookup)
- SubTab type expanded: `'hub' | 'ticker' | 'overview' | 'briefs' | 'alerts' | 'sec' | 'predictions'`

Layout:
```
Stats Row: Briefs | Alerts | 7D Accuracy | SEC
┌─────────────────────────┬──────────────────────────┐
│ LATEST MARKET BRIEF     │  PREDICTION SCORECARD    │
│ (summary, health badge) │  (W/L table, 8 recent)   │
├─────────────────────────┼──────────────────────────┤
│ TOP ALERTS              │  MARKET NEWS             │
│ (6 compact cards)       │  (10 spider items)       │
├─────────────────────────┴──────────────────────────┤
│ RECENT SEC FILINGS (5 items, compact list)         │
└────────────────────────────────────────────────────┘
```

Each section has "View all" links that switch to the relevant sub-tab.

## Files Changed (4)

| File | Change |
|------|--------|
| `core/views_stock_intelligence.py` | New `stock_hub()` endpoint |
| `core/urls.py` | Wire `api/stocks/hub/` URL |
| `frontend/src/lib/api.ts` | Add `hub()` to `stockApi` |
| `frontend/src/pages/StockIntelligencePage.tsx` | New `HubTab` component, default tab |

## No Migration Needed

All queries use existing models (MarketIntelligenceBrief, StockMarketAlert, PredictionOutcome, SpiderData).

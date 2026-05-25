---
originating_session: 979
provenance_confidence: HIGH
provenance_note: auto-added by backfill_doc_provenance
---

# Session 979 — Stock Intelligence PA Routing + Defensive spider_data_tool

**Date:** February 9, 2026
**Previous Session:** 977 (PA Production Timeout Fix)
**Branch:** `main`
**PR:** #1029

---

## Problem

User asks PA "Why doesn't the stock Intelligence show any stocks?" and gets:
```
Unknown action: list. Valid actions: recent, by_spider, by_category, search, stats.
```

### Root Causes (3 layers)

1. **Overly broad keyword match:** The word "intelligence" in "stock intelligence" matched the `spider_data` intent (bare `'intelligence'` keyword at line 771), routing the query to `spider_data_tool` instead of anything stock-related.

2. **Invalid default action:** `_build_tool_payload()` set `'action': 'list'` as the base default (line 813), but `spider_data_tool` only accepts `recent`, `by_spider`, `by_category`, `search`, `stats`. No spider_data-specific override existed.

3. **No stock intelligence PA integration:** Session 975 added the `/stocks` frontend dashboard + 6 API endpoints, but never wired the PA to route stock queries or query those models.

---

## Solution

### 1. New `stock_intelligence` intent + tool (unified_pa_entrypoint.py)

- Added `stock_intelligence` intent detection **before** `spider_data` — matches "stock", "stocks", "market brief", "sec filing", "edgar", "bull case", "bear case", etc.
- Removed bare `'intelligence'` from spider_data keywords (replaced with `'spider intelligence'`)
- Added `stock_intelligence` to `INTENT_ENRICHMENT_MAP` with `['domain_context', 'spider_trends']`
- Added `stock_intelligence` to `DIRECT_RELEVANCE_INTENTS`
- Added payload builder: routes to `overview`, `briefs`, `alerts`, `predictions`, or `sec_filings` based on message keywords
- Added spider_data payload override: defaults to `'recent'` (not invalid `'list'`)
- Added analytical directive for LLM analysis
- Added result formatter for all 5 stock actions

### 2. New `stock_intelligence_tool` handler (tool_dispatcher.py)

Registered `_handle_stock_intelligence` with 5 actions mirroring the `/stocks` dashboard API:

| Action | Models Queried | Data Returned |
|--------|---------------|---------------|
| `overview` | MarketIntelligenceBrief, StockMarketAlert, PredictionOutcome, SpiderData | Latest brief, alert counts by type, prediction accuracy (7D/30D), SEC filing count |
| `briefs` | MarketIntelligenceBrief | Paginated briefs with date, type, summary, stocks analyzed |
| `alerts` | StockMarketAlert | Alerts with symbol, type, bull/bear scores, recommended action |
| `predictions` | PredictionOutcome | Predictions with ticker, conviction, correctness + aggregate accuracy stats |
| `sec_filings` | SpiderData (sec_edgar) | SEC Edgar filings with URL, data type, relevance score |

### 3. Defensive spider_data_tool

Changed `raise ValueError(...)` on unknown actions to `logger.warning()` + fallback to `'recent'` action via recursive call.

---

## Changes

### Files Modified (2)

| File | Changes |
|------|---------|
| `core/services/unified_pa_entrypoint.py` | New `stock_intelligence` intent (before spider_data), removed bare `'intelligence'` from spider_data, enrichment/relevance maps, payload builder, spider_data default override, analytical directive, result formatter |
| `core/services/tool_dispatcher.py` | Registered + implemented `_handle_stock_intelligence` (5 actions), made `_handle_spider_data` defensive on unknown actions |

No migrations needed.

---

## Verification

| Query | Before | After |
|-------|--------|-------|
| "What stocks are being tracked?" | `ValueError: Unknown action: list` | `stock_intelligence_tool` (overview) |
| "Show me market briefs" | Misrouted to spider_data | `stock_intelligence_tool` (briefs) |
| "What have the spiders collected?" | Worked (if action was valid) | `spider_data_tool` (recent) — unchanged |
| "What's the latest spider intelligence?" | Worked | `spider_data_tool` (recent) — still matches |
| spider_data with invalid action | `ValueError` crash | Warning logged, falls back to `recent` |

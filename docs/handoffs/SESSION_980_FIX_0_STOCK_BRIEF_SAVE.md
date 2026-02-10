# Session 980 — Fix: Market Intelligence Brief "0 stocks analyzed"

**Date:** February 9, 2026
**Previous Session:** 979 (Stock Intelligence PA Routing)
**Branch:** `session-980/fix-0-stock-brief-save`
**PR:** TBD

---

## Problem

The Stock Intelligence dashboard shows **"0 stocks analyzed"** on the latest brief (Feb 9, Monday) while older briefs (Feb 7-8) show 10 stocks. The bull/bear agent pipeline silently fails and the coordinator saves a brief with empty data anyway, overwriting any previously good brief for the same date.

### Root Causes

1. **Silent agent failure:** When `_run_bull_case()` or `_run_bear_case()` fail (timeout, GPT error, market data error), they return `{'error': '...'}` with no `bull_cases`/`bear_cases` keys — but the coordinator does not log these errors.
2. **Unconditional save:** `_save_brief_for_tomorrow()` saves via `update_or_create()` even when `total_stocks_analyzed == 0`, overwriting any good previous brief for that date.
3. **No weekend fallback:** `_load_previous_brief()` only loads yesterday's brief exactly. On Monday, yesterday is Sunday (no brief) — so change tracking breaks.

### Pipeline Flow

```
Celery task run_market_intelligence_desk (Mon-Fri 8 AM)
  → MarketIntelligenceCoordinator.execute()
    → _select_tickers() → 10 tickers
    → _run_bull_case() → BullCaseAgent → MarketDataService → YahooFinanceSpider → yfinance
    → _run_bear_case() → same chain
    → _synthesize_debate(bull, bear, risk) → matches by ticker
    → _count_total_stocks(synthesis) → total_stocks_analyzed
    → _save_brief_for_tomorrow(brief) → MarketIntelligenceBrief.update_or_create()
```

---

## Solution

### 1. Guard in `_save_brief_for_tomorrow` (~line 940)

Before the `update_or_create`, check if `total_stocks > 0`. If 0, log a warning and return early — preserves the previous good brief.

### 2. Failure logging after agent execution (~line 180)

After `_run_bull_case` and `_run_bear_case`, log explicit warnings when agents return errors, plus an info line with bull/bear case counts. Makes it easy to diagnose why a brief came back empty from Railway logs.

### 3. Fallback brief loading in `_load_previous_brief` (~line 337)

When yesterday's brief doesn't exist (weekend gap, failed run), fall back to the most recent brief within the last 5 days that has `total_stocks_analyzed > 0`. This ensures change tracking works on Mondays and after failed runs.

---

## Changes

### Files Modified (1)

| File | Changes |
|------|---------|
| `core/agents/stocks/market_intelligence_coordinator.py` | (1) 0-stock save guard in `_save_brief_for_tomorrow`, (2) agent error + count logging in `execute()`, (3) 5-day fallback in `_load_previous_brief` with `total_stocks_analyzed__gt=0` filter |

No migrations needed. No frontend changes.

---

## Verification

- `py_compile` passes
- Existing briefs with data are unaffected — the guard only blocks 0-stock saves
- When bull/bear agents fail, logs now show explicit warnings with error details
- `_load_previous_brief` on Monday loads Friday's brief if Sat/Sun have no briefs

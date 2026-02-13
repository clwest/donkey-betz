# Stock Intelligence

Dedicated dashboard surfacing stock market data from spiders and agents, with PA integration for natural language queries.

## Dashboard (/stocks)

7 sub-tabs with 7 read-only API endpoints. Hub is the default landing tab.

| Sub-tab | Endpoint | Content |
|---------|----------|---------|
| **Hub** (default) | GET /api/stocks/hub/ | Consolidated view: latest brief, top alerts, prediction scorecard, market news, SEC filings |
| **Ticker Lookup** | GET /api/stocks/ticker/:symbol/ | Unified single-ticker intelligence |
| **Overview** | GET /api/stocks/dashboard/ | Latest brief, alert counts, prediction accuracy, SEC count |
| **Market Briefs** | GET /api/stocks/briefs/ | Paginated briefs with detail view |
| **Alerts** | GET /api/stocks/alerts/ | Filterable by type/symbol/action/bookmarked |
| **SEC Filings** | GET /api/stocks/sec-filings/ | Edgar filings |
| **Predictions** | GET /api/stocks/predictions/ | 7D/30D accuracy stats |

## Models

- **MarketIntelligenceBrief:** Daily market analysis with full JSON fields (total_stocks_analyzed, recommendations)
- **StockMarketAlert:** Type/symbol/action with bookmarking. Yahoo Finance threshold 2% (lowered from 5%), title-based dedup
- **PredictionOutcome:** Bull/bear targets with `UniqueConstraint(brief, ticker, prediction_type)`. `_parse_target_move()` regex for "25%+", "-25% or more". Session 994: handles numeric types from GPT JSON (int/float returned directly). Per-iteration error handling in `_record_predictions_for_learning()` — one bad ticker doesn't kill the batch.
- **SpiderData:** Source data from financial spiders

## Brief Save Guard

`_save_brief_for_tomorrow()` skips saving when `total_stocks_analyzed == 0`, preserving the previous good brief. 5-day weekend fallback for `_load_previous_brief`.

## PA Integration (Session 979)

`stock_intelligence` intent routes stock/market/SEC queries to `stock_intelligence_tool` with 5 actions: overview, briefs, alerts, predictions, sec_filings.

**Routing fix:** `'intelligence'` keyword was removed from `spider_data` intent to prevent "stock intelligence" queries from misrouting. `spider_data_tool` made defensive — unknown actions fall back to `'recent'` instead of raising ValueError.

## Brief Detail UI

Structured cards replaced raw JSON dump: ticker, recommendation badge, bull/bear arguments with score bars, risk factors.

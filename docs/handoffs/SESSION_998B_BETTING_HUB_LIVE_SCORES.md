---
originating_session: 998
provenance_confidence: HIGH
provenance_note: auto-added by backfill_doc_provenance
---

# Session 998B: Sports Betting Hub + Live Scores + AI Predictions

**Date:** February 12, 2026
**Focus:** Hub tab with news/injury feed, live score display, odds-consensus AI predictions

## What Was Built

### Part 1: Betting Hub Tab + News/Injury Spiders

**New spiders:**
- `SportsNewsSpider` — aggregates ESPN, NYT Sports, CBS Sports, Yahoo Sports, SI via RSS
- `SportsInjurySpider` — aggregates RotoWire, CBS Injuries, RotoGrinders via RSS
- Both registered in `spider_registry.py` with `sports_news` / `sports_injuries` data types

**Hub feed API:**
- `GET /api/v1/betting/hub-feed/` — returns latest sports news + injury reports from SpiderData
- Rendered in new "Hub" tab on `/betting` page with news cards and injury alerts

**Frontend:**
- New Hub tab added as first tab in BettingPage.tsx (11 tabs total)
- Sidebar link for `/betting` added

### Part 2: Railway Odds Tables Fix

Migration `0241_session_998b_recreate_odds_tables` — recreated missing odds-related tables on Railway that were lost during a previous deploy. Also guarded PA conversation persistence against None values.

### Part 3: Live Scores + AI Predictions on Today's Games

**Problem:** Today's Games showed LIVE badge but no scores (spider filtered out in-progress games), and predictions were broken (MLPrediction model has no `event_id` field).

**Spider fix (`theodds_spider.py`):**
- `fetch_scores()` no longer skips in-progress games — returns both completed and live games with scores
- Passes `completed` field as-is from API (`True` for final, `False` for live)

**Odds-consensus predictions (`views_odds_sports.py`):**
- Replaced broken `MLPrediction` DB lookup with inline odds-implied probability calculation
- `_american_to_probability()` converts American odds to implied probability
- Picks favorite team when implied probability > 55%
- New `prediction_correct` field: `True`/`False` for completed games, `None` for pending

**Frontend (`BettingPage.tsx`):**
- Live games now show scores (not just completed games)
- AI Pick banners change color based on outcome: green (correct W), red (wrong L), purple (pending)
- Stats row: Live / AI Picks / Completed / Upcoming (replaced Total Games + With Predictions)

## Files Changed (14 across all parts)

| File | Change |
|------|--------|
| `ai_core/spiders/real_data_collector.py` | SportsNewsSpider + SportsInjurySpider |
| `ai_core/spiders/spider_registry.py` | Register new spiders |
| `ai_core/spiders/specialized/theodds_spider.py` | `fetch_scores()`: include live games |
| `core/urls.py` | Hub feed endpoint |
| `core/views_spider_feed.py` | New hub feed API view |
| `core/views_odds_sports.py` | Odds-consensus predictions + `prediction_correct` |
| `core/views_personal_assistant.py` | Guard conversations against None |
| `core/migrations/0241_session_998b_recreate_odds_tables.py` | Recreate odds tables |
| `frontend/src/lib/api.ts` | Hub feed API call |
| `frontend/src/pages/BettingPage.tsx` | Hub tab, live scores, W/L badges, stats row |
| `frontend/src/components/layout/Sidebar.tsx` | Betting sidebar link |
| `docs/topics/frontend.md` | Updated route description |
| `docs/topics/spider-network.md` | Added new spider categories |
| `CLAUDE.md` | Updated spider count |

## Key Technical Details

**American odds → probability:**
```python
def _american_to_probability(odds: int) -> float:
    if odds > 0:
        return 100 / (odds + 100)      # +150 → 0.40
    else:
        return abs(odds) / (abs(odds) + 100)  # -200 → 0.667
```

**Prediction threshold:** Only predicts when implied probability > 55% — avoids coin-flip matchups.

## Spiders (Updated Count)

79 spiders total (74 working, 5 need API keys). +2 new: SportsNewsSpider, SportsInjurySpider.

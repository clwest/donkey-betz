---
originating_session: 950
provenance_confidence: HIGH
provenance_note: auto-added by backfill_doc_provenance
---

# Session 950 - Kalshi Sports Categorization Fix

**Date:** February 6, 2026
**Focus:** Fix sports betting markets miscategorized in Market Intelligence reports
**PRs:** #924 (scroll fix), #926 (Kalshi categorization)

---

## Summary

Fixed two issues:
1. Sports betting markets from Kalshi were being miscategorized as "tech" or "general"
2. Workspace pages couldn't scroll after PA dock was added in Session 948

---

## Issue 1: Sports Betting Categorization

### Problem
Market Intelligence reports showed sports betting markets (NBA player props, esports, parlays) categorized as "tech" because the Kalshi spider's `_extract_category()` method only had 'nfl' and 'nba' buried in the 'entertainment' category, and no patterns for:
- Player names (Kawhi Leonard, Zach LaVine, etc.)
- Sports betting terms (points, assists, rebounds, parlays)
- Esports games (Valorant, League of Legends, etc.)

### Solution - PR #926

Added dedicated 'sports' category with comprehensive patterns:

```python
'sports': [
    # Major leagues
    'nba', 'nfl', 'mlb', 'nhl', 'mls', 'wnba', 'ncaa', 'pga', 'ufc', 'mma',
    # Esports
    'esports', 'league of legends', 'valorant', 'counter-strike', 'dota',
    'overwatch', 'call of duty', 'fortnite', 'csgo', 'cs2',
    # Player stats
    'points', 'assists', 'rebounds', 'touchdowns', 'yards', 'goals',
    # Betting terms
    'parlay', 'spread', 'over', 'under', 'moneyline', 'prop bet',
    # Teams and players
    'lakers', 'celtics', 'warriors', 'lebron', 'curry', 'mahomes', ...
]
```

### Additional Fixes

**Multi-leg Parlay Title Cleanup:**
Added `_clean_title()` method to handle concatenated bet legs:
```python
# Before: "yes Kawhi Leonard: 1+,yes Zach LaVine: 1+,yes Jayson Tatum: 1+..."
# After:  "Kawhi Leonard + 9 others Parlay (10 legs)"
```

**Volume/Probability Fallbacks:**
- Use `last_price` as fallback for probability when yes_bid/yes_ask are empty
- Check multiple volume fields: volume, volume_24h, dollar_volume

---

## Issue 2: Workspace Scroll Fix

### Problem
After adding the Global PA Dock in Session 948 (PR #908), workspace pages couldn't scroll.

### Cause
`frontend/src/components/layout/Layout.tsx` had `overflow-hidden` on the content wrapper.

### Solution - PR #924
Changed to `overflow-auto`:
```jsx
<div className="flex-1 min-h-0 overflow-auto">  {/* was overflow-hidden */}
  <Outlet />
</div>
```

---

## Files Changed

| File | Changes |
|------|---------|
| `ai_core/spiders/specialized/kalshi_spider.py` | Added 'sports' category, `_clean_title()`, volume fallbacks |
| `core/agents/stocks/market_intelligence_coordinator.py` | Added 'sports' to categories, added sports_signals |
| `frontend/src/components/layout/Layout.tsx` | Fixed overflow-hidden to overflow-auto |

---

## Additional Fix: Empty Stock Analysis - PR #927

### Problem
Market Intelligence reports showed 0 stocks in debate zone, bullish, and bearish categories.

### Root Cause
Session 761 refactored BullCaseAgent and BearCaseAgent to use LLM tool calling, but changed the return structure:
- **Before:** `{'bull_cases': [{'ticker': 'AAPL', 'conviction': 'HIGH', ...}, ...]}`
- **After:** `{'analysis': '...', 'ticker': 'AAPL', 'conviction': 'HIGH'}` (single dict)

The coordinator's `_synthesize_debate()` expected lists but got single dicts, resulting in empty synthesis.

### Fix
Updated both agents to iterate over all tickers and return the expected list format:
- `BullCaseAgent.execute()` now returns `{'bull_cases': [...]}`
- `BearCaseAgent.execute()` now returns `{'bear_cases': [...]}`

---

## Remaining Issues

- **Some markets still showing 0 volume, 50% probability** - These may be genuinely low-volume markets from Kalshi

---

## Testing

```bash
# Test Kalshi spider categorization
python manage.py shell
>>> from ai_core.spiders.specialized.kalshi_spider import KalshiSpider
>>> spider = KalshiSpider()
>>> data = spider.fetch_data(max_results=50)
>>> sports = [m for m in data if m.get('category') == 'sports']
>>> print(f"Found {len(sports)} sports markets")

# Check title cleanup
>>> [m['title'] for m in sports if 'Parlay' in m.get('title', '')]
```

---

## Session 951 Additions

### PA Platform Query Tool - Session 951

**Problem:** PA couldn't answer questions about platform data (e.g., "what reports have been written by agents") because it had no tool for querying the database.

**Root Cause:** The PA had 29 tools for creative generation, strategy, and research, but NO tool for querying:
- `Deliverable` model (blog posts, reports, analyses)
- `AuditReport` model (agent audit findings)
- `Initiative` model (tracked initiatives)

**Solution:** Added `platform_query_tool` with 5 query types:
- `deliverables` - Query blog posts, reports, analyses with filters (agent, type, category, days)
- `audit_reports` - Query audit reports from agents
- `initiatives` - Query tracked initiatives
- `agent_outputs` - Query outputs by specific agent or get summary by agent
- `content_summary` - Overview of all platform content

**Files Changed:**
- `core/personal_ai_assistant_enhanced.py`:
  - Added tool definition (lines 1260-1287)
  - Added handler dispatch (line 1481)
  - Added `_handle_platform_query_tool()` method (lines 13766-13963)

**Verification:**
```python
# Test the new tool
result = assistant._handle_platform_query_tool({'query_type': 'content_summary'})
# Returns: 355 deliverables, 61 audit reports, 169 initiatives
```

---

## Next Steps

- **Option F in session doc**: Investigate why BullCaseAgent/BearCaseAgent return empty results
- Consider adding more sports teams and player names to patterns
- Add observability for category distribution in Market Intelligence reports
